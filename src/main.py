import os
import numpy as np
import supervisely as sly
import src.functions as f
from distutils.util import strtobool
from dotenv import load_dotenv

# load ENV variables for debug
# has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

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
    idx2class = {
        idx: sly.ObjClass(class_name, sly.Bitmap)
        for class_name, idx in class2idx.items()
    }

    project_meta = sly.ProjectMeta(list(idx2class.values()))
    class2idx_found = True
else:
    project_meta = sly.ProjectMeta()

api.project.update_meta(project_info.id, project_meta.to_json())

for ds_name in os.listdir(project_path):
    ds_dir = os.path.join(project_path, ds_name)
    if sly.fs.dir_exists(ds_dir):
        dataset = api.dataset.create(project_info.id, ds_name)
        volumes_dir = os.path.join(ds_dir, "volumes")
        masks_dir = os.path.join(ds_dir, "masks")
        if not sly.fs.dir_exists(volumes_dir):
            raise NotADirectoryError(
                f"'volumes' folder not found in dataset '{ds_name}'"
            )
        if not sly.fs.dir_exists(masks_dir):
            raise NotADirectoryError(f"'masks' folder not found in dataset '{ds_name}'")
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
        for item_name, item_id in item_names2ids.items():
            item_masks_dir = os.path.join(masks_dir, item_name)
            if not sly.fs.dir_exists(item_masks_dir):
                raise RuntimeError(f"Masks folder for item {item_name} not found.")
            if sly.fs.dir_empty(item_masks_dir):
                raise RuntimeError(f"Masks folder for item {item_name} is empty.")
            volume, volume_meta = sly.volume.read_nrrd_serie_volume_np(
                os.path.join(volumes_dir, item_name)
            )
            ann_figures = {"saggital": {}, "coronal": {}, "axial": {}}
            ann_objects = {}
            masks_filenames = sorted(os.listdir(item_masks_dir))
            for mask_filename in masks_filenames:
                if mask_filename == ".DS_Store":  # TODO: remove
                    continue
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
                for idx, volume_object in mask_objects.items():

                    if idx not in ann_objects.keys():
                        ann_objects[idx] = volume_object
                    for i in range(volume_mask.shape[0]):  # saggital
                        class_object_mask = volume_mask[i, :, :] == idx
                        if not np.any(class_object_mask):
                            continue
                        if i not in ann_figures["saggital"].keys():
                            ann_figures["saggital"][i] = []
                        figure = sly.VolumeFigure(
                            volume_object,
                            sly.Bitmap(class_object_mask.T),
                            sly.Plane.SAGITTAL,
                            i,
                        )
                        ann_figures["saggital"][i].append(figure)
                    for i in range(volume_mask.shape[1]):  # coronal
                        class_object_mask = volume_mask[:, i, :] == idx
                        if not np.any(class_object_mask):
                            continue
                        if i not in ann_figures["coronal"].keys():
                            ann_figures["coronal"][i] = []
                        figure = sly.VolumeFigure(
                            volume_object,
                            sly.Bitmap(class_object_mask.T),
                            sly.Plane.CORONAL,
                            i,
                        )
                        ann_figures["coronal"][i].append(figure)
                    for i in range(volume_mask.shape[2]):  # axial
                        class_object_mask = volume_mask[:, :, i] == idx
                        if not np.any(class_object_mask):
                            continue
                        if i not in ann_figures["axial"].keys():
                            ann_figures["axial"][i] = []
                        figure = sly.VolumeFigure(
                            volume_object,
                            sly.Bitmap(class_object_mask.T),
                            sly.Plane.AXIAL,
                            i,
                        )
                        ann_figures["axial"][i].append(figure)

            frames = {"saggital": [], "coronal": [], "axial": []}
            for plane_name in ["saggital", "coronal", "axial"]:
                for k, v in ann_figures[plane_name].items():
                    frames[plane_name].append(sly.Slice(k, v))
            volume_ann = sly.VolumeAnnotation(
                volume_meta,
                sly.VolumeObjectCollection(list(ann_objects.values())),
                sly.Plane(
                    sly.Plane.SAGITTAL,
                    items=frames["saggital"],
                    volume_meta=volume_meta,
                ),
                sly.Plane(
                    sly.Plane.CORONAL,
                    items=frames["coronal"],
                    volume_meta=volume_meta,
                ),
                sly.Plane(
                    sly.Plane.AXIAL,
                    items=frames["axial"],
                    volume_meta=volume_meta,
                ),
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
            sly.logger.info(f"Volume {item_name} has been uploaded successfully.")

if remove_source and not is_on_agent:
    api.file.remove(team_id=team_id, path=remote_path)
    remote_folder_name = os.path.basename(os.path.normpath(remote_path))
    sly.logger.info(
        msg=f"Source directory: '{remote_folder_name}' was successfully removed."
    )

api.app.set_output_project(task_id, project_info.id, project_name)
