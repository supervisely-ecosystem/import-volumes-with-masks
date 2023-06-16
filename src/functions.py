import supervisely as sly
import os
import numpy as np
from typing import List, Dict


def download_folder_from_team_files(
    api: sly.Api, remote_path: str, team_id: int, is_on_agent: bool, save_path: str
) -> str:
    if is_on_agent:
        _, cur_files_path = api.file.parse_agent_id_and_path(remote_path)
    else:
        cur_files_path = remote_path
    project_folder = os.path.basename(os.path.normpath(cur_files_path))
    project_path = os.path.join(save_path, project_folder)
    if sly.fs.dir_exists(project_path):
        return project_path
    sizeb = api.file.get_directory_size(team_id, remote_path)
    progress = sly.Progress(f"Downloading {project_folder}", sizeb, is_size=True)

    api.file.download_directory(
        team_id=team_id,
        remote_path=remote_path,
        local_save_path=project_path,
        progress_cb=progress.iters_done_report,
    )
    return project_path


def create_plane_figures(
    volume_mask: np.ndarray,
    ann_figures: Dict[str, Dict[int, List[sly.VolumeFigure]]],
    class_idx: int,
    volume_object: sly.VolumeObject,
    plane_idx: int,
) -> None:
    planes = [sly.Plane.SAGITTAL, sly.Plane.CORONAL, sly.Plane.AXIAL]
    for slice_idx in range(volume_mask.shape[plane_idx]):
        # if instead of np.take to increase speed
        if plane_idx == 0:
            class_object_mask = volume_mask[slice_idx, :, :] == class_idx
        elif plane_idx == 1:
            class_object_mask = volume_mask[:, slice_idx, :] == class_idx
        elif plane_idx == 2:
            class_object_mask = volume_mask[:, :, slice_idx] == class_idx

        if not np.any(class_object_mask):
            continue
        if slice_idx not in ann_figures[planes[plane_idx]].keys():
            ann_figures[planes[plane_idx]][slice_idx] = []
        figure = sly.VolumeFigure(
            volume_object,
            sly.Bitmap(class_object_mask.T),
            planes[plane_idx],
            slice_idx,
        )
        ann_figures[planes[plane_idx]][slice_idx].append(figure)
