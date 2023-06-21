import os
import nrrd
import numpy as np
import supervisely as sly
import src.functions as f
from distutils.util import strtobool
from dotenv import load_dotenv
from copy import copy
from collections import OrderedDict

# load ENV variables for debug
# has no effect in production
if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))
    sly.fs.clean_dir(os.environ["SLY_APP_DATA_DIR"])

api = sly.Api.from_env()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()
task_id = sly.env.task_id()

sly.logger.info("Script arguments", extra={"TEAM_ID": team_id, "WORKSPACE_ID": workspace_id})

data_dir = sly.app.get_data_dir()
project_name = os.environ["modal.state.projectName"]
remove_source = bool(strtobool(os.getenv("modal.state.removeSource")))
remote_path = os.environ["FOLDER"]
is_on_agent = api.file.is_on_agent(remote_path)

try:
    project_path = f.download_folder_from_team_files(
        api, remote_path, team_id, is_on_agent, data_dir
    )
except Exception as e:
    sly.logger.info(
        "INFO FOR DEBUGGING",
        extra={
            "remote_path": remote_path,
            "team_id": team_id,
            "is_on_agent": is_on_agent,
            "data_dir": data_dir,
        },
    )
    raise e

if api.project.exists(workspace_id, project_name):
    project_name = api.project.get_free_name(workspace_id, project_name)

class2idx_path = os.path.join(project_path, "class2idx.json")

project_info = api.project.create(workspace_id, project_name, sly.ProjectType.VOLUMES)
class2idx_found = False
idx2class = {}
if sly.fs.file_exists(class2idx_path):
    class2idx = sly.json.load_json_file(class2idx_path)
    idx2class = {idx: sly.ObjClass(class_name, sly.Mask3D) for class_name, idx in class2idx.items()}
    max_id = max(idx2class.keys())
    project_meta = sly.ProjectMeta(list(idx2class.values()))
    class2idx_found = True
    class2idx_changed = False
    mask_class = OrderedDict(copy(idx2class))
else:
    project_meta = sly.ProjectMeta()
    max_id = 0
    mask_class = None

api.project.update_meta(project_info.id, project_meta.to_json())

for ds_name in sorted(os.listdir(project_path)):
    ds_dir = os.path.join(project_path, ds_name)
    if sly.fs.dir_exists(ds_dir):
        dataset = api.dataset.create(project_info.id, ds_name)
        volumes_dir = os.path.join(ds_dir, "volume")
        masks_dir = os.path.join(ds_dir, "mask")
        if not sly.fs.dir_exists(volumes_dir):
            raise NotADirectoryError(f"'volume' folder not found in dataset '{ds_name}'")
        if not sly.fs.dir_exists(masks_dir):
            raise NotADirectoryError(f"'mask' folder not found in dataset '{ds_name}'")
        volumes_names = [
            file for file in sorted(os.listdir(volumes_dir)) if sly.volume.has_valid_ext(file)
        ]
        volumes_paths = [os.path.join(volumes_dir, volume) for volume in volumes_names]

        volumes_progress = sly.tqdm_sly(
            desc=f"Uploading volumes to {dataset.name} dataset", total=len(volumes_names)
        )

        try:
            volume_infos = api.volume.upload_nrrd_series_paths(
                dataset.id,
                volumes_names,
                volumes_paths,
                volumes_progress,
            )
        except Exception as e:
            sly.logger.info(
                "INFO FOR DEBUGGING",
                extra={
                    "project_id": project_info.id,
                    "dataset_id": dataset.id,
                    "volumes_names": volumes_names,
                    "volumes_paths": volumes_paths,
                },
            )
            raise e

        volume_names2ids = {volume_info.name: volume_info.id for volume_info in volume_infos}

        anns_progress = sly.tqdm_sly(
            desc=f"Uploading volume annotations to {dataset.name} dataset",
            total=len(volume_names2ids),
        )

        for volume_name, volume_id in volume_names2ids.items():
            volume_masks_dir = os.path.join(masks_dir, volume_name)
            if not sly.fs.dir_exists(volume_masks_dir):
                raise RuntimeError(f"Mask folder for volume {volume_name} not found.")
            if sly.fs.dir_empty(volume_masks_dir):
                raise RuntimeError(f"Mask folder for volume {volume_name} is empty.")
            _, volume_meta = sly.volume.read_nrrd_serie_volume_np(
                os.path.join(volumes_dir, volume_name)
            )
            spatial_figures = []
            geometries = []
            ann_objects = {}
            masks_filenames = sorted(os.listdir(volume_masks_dir))

            # for backward compatibility with the export app
            while "human-readable-objects" in masks_filenames:
                masks_filenames.remove("human-readable-objects")
            while "semantic_segmentation.nrrd" in masks_filenames:
                masks_filenames.remove("semantic_segmentation.nrrd")

            for mask_filename in masks_filenames:
                if not sly.volume.has_valid_ext(mask_filename):
                    continue
                mask_path = os.path.join(volume_masks_dir, mask_filename)

                if mask_class:
                    _, current_class = mask_class.popitem(last=False)
                else:
                    max_id += 1
                    current_class = sly.ObjClass(f"class_{int(max_id)}", sly.Mask3D)
                    idx2class[max_id] = current_class
                    class2idx_changed = True

                mask_object = sly.VolumeObject(current_class)

                if mask_object.key() not in ann_objects.keys():
                    ann_objects[mask_object.key()] = mask_object

                # exclude empty figures
                mask_data, _ = nrrd.read(mask_path)
                if mask_data.max() == 0:
                    continue

                with open(mask_path, "rb") as file:
                    geometry_bytes = file.read()

                zero_figure = sly.VolumeFigure(
                    mask_object, sly.Mask3D(np.zeros((3, 3, 3), dtype=np.bool_)), None, None
                )
                spatial_figures.append(zero_figure)
                geometries.append(geometry_bytes)

            volume_ann = sly.VolumeAnnotation(
                volume_meta,
                sly.VolumeObjectCollection(list(ann_objects.values())),
                spatial_figures=spatial_figures,
            )

            if not class2idx_found or class2idx_changed:
                project_meta = sly.ProjectMeta(list(idx2class.values()))
                api.project.update_meta(project_info.id, project_meta.to_json())

            key_id_map = sly.KeyIdMap()

            try:
                api.volume.annotation.append(volume_id, volume_ann, key_id_map)
                api.volume.figure.upload_sf_geometry(
                    volume_ann.spatial_figures, geometries, key_id_map
                )
            except Exception as e:
                sly.logger.info(
                    "INFO FOR DEBUGGING",
                    extra={
                        "project_id": project_info.id,
                        "dataset_id": dataset.id,
                        "item_name": volume_name,
                        "item_id": volume_id,
                        "volume_ann": volume_ann.to_json(),
                    },
                )
                raise e
            anns_progress(1)

if remove_source and not is_on_agent:
    api.file.remove(team_id=team_id, path=remote_path)
    remote_folder_name = os.path.basename(os.path.normpath(remote_path))
    sly.logger.info(msg=f"Source directory: '{remote_folder_name}' was successfully removed.")

sly.logger.info(msg=f"Project '{project_info.name}' uploaded succesfully.")

api.app.set_output_project(task_id, project_info.id, project_name)
