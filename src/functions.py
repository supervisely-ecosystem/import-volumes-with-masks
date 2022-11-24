import supervisely as sly
import os


def download_folder_from_team_files(
    api: sly.Api, remote_path: str, team_id: int, is_on_agent: bool, save_path: str
) -> str:
    if is_on_agent:
        agent_id, cur_files_path = api.file.parse_agent_id_and_path(remote_path)
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
