import supervisely as sly
from tqdm import tqdm
from supervisely.io.json import load_json_file
import os


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

    progress = tqdm(desc=f"Downloading {project_folder}", total=sizeb, unit="M", unit_scale=True)

    api.file.download_directory(
        team_id=team_id,
        remote_path=remote_path,
        local_save_path=project_path,
        progress_cb=progress.update,
    )
    return project_path


def get_masks_to_exclude(ann_json_path: str) -> list:
    masks_to_exclude = []
    ann_json = load_json_file(ann_json_path)
    spatial_figures = ann_json.get("spatialFigures", [])
    for figure in spatial_figures:
        mask_name = figure.get("key", None) + ".nrrd"
        if mask_name is not None:
            masks_to_exclude.append(mask_name)
    return masks_to_exclude
