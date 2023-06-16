import os
import numpy as np
import supervisely as sly
import src.functions as f
from distutils.util import strtobool
from dotenv import load_dotenv

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

sly.logger.info(
    "Script arguments", extra={"TEAM_ID": team_id, "WORKSPACE_ID": workspace_id}
)

data_dir = sly.app.get_data_dir()
project_name = os.environ["modal.state.projectName"]
remove_source = bool(strtobool(os.getenv("modal.state.removeSource")))
remote_path = os.environ["TEAM_FILES_FOLDER"]
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
    idx2class = {
        idx: sly.ObjClass(class_name, sly.Bitmap)
        for class_name, idx in class2idx.items()
    }

    project_meta = sly.ProjectMeta(list(idx2class.values()))
    class2idx_found = True
else:
    project_meta = sly.ProjectMeta()

api.project.update_meta(project_info.id, project_meta.to_json())
planes = [sly.Plane.SAGITTAL, sly.Plane.CORONAL, sly.Plane.AXIAL]

for ds_name in os.listdir(project_path):
    ds_dir = os.path.join(project_path, ds_name)
    if sly.fs.dir_exists(ds_dir):
        dataset = api.dataset.create(project_info.id, ds_name)
        volumes_dir = os.path.join(ds_dir, "volume")
        masks_dir = os.path.join(ds_dir, "mask")
        if not sly.fs.dir_exists(volumes_dir):
            raise NotADirectoryError(
                f"'volume' folder not found in dataset '{ds_name}'"
            )
        if not sly.fs.dir_exists(masks_dir):
            raise NotADirectoryError(f"'mask' folder not found in dataset '{ds_name}'")
        volumes_names = [
            file for file in os.listdir(volumes_dir) if sly.volume.has_valid_ext(file)
        ]
        volumes_paths = [os.path.join(volumes_dir, volume) for volume in volumes_names]
        volumes_progress = sly.Progress(
            f"Uploading volumes to {dataset.name} dataset", len(volumes_names)
        )
        try:
            item_infos = api.volume.upload_nrrd_series_paths(
                dataset.id,
                volumes_names,
                volumes_paths,
                volumes_progress.iters_done_report,
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
        item_names2ids = {item_info.name: item_info.id for item_info in item_infos}
        anns_progress = sly.Progress(
            f"Uploading volume annotations to {dataset.name} dataset",
            len(item_names2ids),
        )
        for item_name, item_id in item_names2ids.items():
            item_masks_dir = os.path.join(masks_dir, item_name)
            if not sly.fs.dir_exists(item_masks_dir):
                raise RuntimeError(f"Mask folder for item {item_name} not found.")
            if sly.fs.dir_empty(item_masks_dir):
                raise RuntimeError(f"Mask folder for item {item_name} is empty.")
            volume, volume_meta = sly.volume.read_nrrd_serie_volume_np(
                os.path.join(volumes_dir, item_name)
            )
            ann_figures = {plane_name: {} for plane_name in planes}
            ann_objects = {}
            masks_filenames = sorted(os.listdir(item_masks_dir))

            # for backward compatibility with  the export app
            while "human-readable-objects" in masks_filenames:
                masks_filenames.remove("human-readable-objects")

            for mask_filename in masks_filenames:
                if not sly.volume.has_valid_ext(mask_filename):
                    continue
                mask_path = os.path.join(item_masks_dir, mask_filename)
                volume_mask, meta = sly.volume.read_nrrd_serie_volume_np(mask_path)
                unique_values = np.unique(volume_mask).tolist()
                for val in unique_values:
                    if val not in idx2class and val != 0:
                        idx2class[val] = sly.ObjClass(f"class{int(val)}", sly.Bitmap)
                mask_objects = {
                    val: sly.VolumeObject(idx2class[val])
                    for val in unique_values
                    if val != 0
                }
                for (
                    class_idx,
                    volume_object,
                ) in mask_objects.items():  # objects of different classes
                    if volume_object.key() not in ann_objects.keys():
                        ann_objects[volume_object.key()] = volume_object

                    for plane_idx, _ in enumerate(
                        planes
                    ):  # create figures for all 3 planes
                        f.create_plane_figures(
                            volume_mask,
                            ann_figures,
                            class_idx,
                            volume_object,
                            plane_idx,
                        )

            frames = {plane_name: [] for plane_name in planes}
            for plane_name in planes:
                for slice_idx, slice_figures in ann_figures[plane_name].items():
                    frames[plane_name].append(sly.Slice(slice_idx, slice_figures))
            volume_ann = sly.VolumeAnnotation(
                volume_meta,
                sly.VolumeObjectCollection(list(ann_objects.values())),
                *[
                    sly.Plane(
                        plane_name, items=frames[plane_name], volume_meta=volume_meta
                    )
                    for plane_name in planes
                ],
            )
            volume_ann.validate_figures_bounds()
            if not class2idx_found:
                project_meta = sly.ProjectMeta(list(idx2class.values()))
                api.project.update_meta(project_info.id, project_meta.to_json())
            ann_json = volume_ann.to_json()
            sly.json.dump_json_file(ann_json, os.path.join(data_dir, "tmp.json"))

            try:
                api.volume.annotation.append(item_id, volume_ann)
            except Exception as e:
                sly.logger.info(
                    "INFO FOR DEBUGGING",
                    extra={
                        "project_id": project_info.id,
                        "dataset_id": dataset.id,
                        "item_name": item_name,
                        "item_id": item_id,
                        "volume_ann": volume_ann.to_json(),
                    },
                )
                raise e
            anns_progress.iter_done_report()
            sly.logger.info(f"Volume {item_name} has been uploaded successfully.")

if remove_source and not is_on_agent:
    api.file.remove(team_id=team_id, path=remote_path)
    remote_folder_name = os.path.basename(os.path.normpath(remote_path))
    sly.logger.info(
        msg=f"Source directory: '{remote_folder_name}' was successfully removed."
    )

api.app.set_output_project(task_id, project_info.id, project_name)
