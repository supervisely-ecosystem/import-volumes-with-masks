<div align="center" markdown>

<img src="https://user-images.githubusercontent.com/97401023/203817046-018b4b41-e69a-4c1f-8b99-6c7f69a6a7d4.png" style="width: 100%;"/>

# Import Volumes with Masks

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-Run">How to Run</a> •
  <a href="#Input-Data-Structure">Input Data Structure</a> •
  <a href="#Demo">Demo</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-volumes-with-masks)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-volumes-with-masks)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-volumes-with-masks.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-volumes-with-masks.png)](https://supervise.ly)

</div>

# Overview

Import volumes in `NRRD` format with masks in `NRRD` format with semantic segmentation labels.

# How to Run

App can be launched from ecosystem, team files and from agent.

<details open>
<summary>Run from ecosystem</summary>
<br>
1. Click `Run application...` button on the right side of the app page. Modal window will be opened.
<img src="https://user-images.githubusercontent.com/97401023/203985563-e1fca937-5cda-4af2-83a1-435238108d3c.png" />

2. If you want to upload project folder from your computer, choose `Drag & Drop` option. You can upload the project folder to drag-and-drop field or you can click on the drag-and-drop field and choose project from your computer in opened window. 
<img src="https://user-images.githubusercontent.com/97401023/203985668-9d5fb085-235b-4e4e-903f-54e110a6dd08.png" />

3. If you want to use project from Team Files, choose `Team Files` option and choose folder to use in the app. 
<img src="https://user-images.githubusercontent.com/97401023/203985717-a54a6867-d903-4be0-a160-975e633eb9f8.png" />

4. Enter project name to `Result Project Name` field or leave the default value.
5. If you want to leave your folder in Team Files after successful import, uncheck the box `Remove temporary files after successful import` below.
6. Also you can set `Advanced parameters` such as agent, app version and other.
7. Click `Run` button to start app.
</details>

<details>
<summary>Run from team files</summary>
<br>
1. Run the application from the context menu of the folder on Team Files page
<img src="https://user-images.githubusercontent.com/97401023/203985820-e657e722-9d8f-46a5-a596-c64051ff7c64.png" />

2. If you want to upload project folder from your computer, choose `Drag & Drop` option. You can upload the project folder to drag-and-drop field or you can click on the drag-and-drop field and choose project from your computer in opened window. 
<img src="https://user-images.githubusercontent.com/97401023/203985668-9d5fb085-235b-4e4e-903f-54e110a6dd08.png" />

3. If you want to use project from Team Files, choose `Team Files` option and choose folder to use in the app. 
<img src="https://user-images.githubusercontent.com/97401023/203985717-a54a6867-d903-4be0-a160-975e633eb9f8.png" />

4. Enter project name to `Result Project Name` field or leave the default value.
5. If you want to leave your folder in Team Files after successful import, uncheck the box `Remove temporary files after successful import` below.
6. Also you can set `Advanced parameters` such as agent, app version and other.
7. Click `Run` button to start app.
</details>

<details>
<summary>Run from agent</summary>
<br>
Application supports import from special directory on your local computer. It is made for Enterprise Edition customers who need to upload tens or even hundreds of gigabytes of data without using drag-ang-drop mechanism:

1. Run agent on your computer where data is stored. Watch [how-to video](https://youtu.be/aO7Zc4kTrVg).
2. Copy your data to special folder on your computer that was created by agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more [in documentation](https://github.com/supervisely/docs/blob/master/customization/agents/agent-storage/agent-storage.md). Watch [how-to video](https://youtu.be/63Kc8Xq9H0U).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right click to open context menu and start app. Now app will upload data directly from your computer to the platform.
</details>

# Input Data Structure

Project name will not be taken from the root folder name. You should specify project name in modal window when you run the app.

Project directory example:

```
my_volumes_project
├── class2idx.json (optional)
├── <DATASET_NAME_0>
│   ├── volumes
│   │   ├── volume_1.nrrd
│   │   ├── volume_2.nrrd
│   │   └── ...
│   └── masks
│       ├── volume_1.nrrd (directory)
│       │   ├── mask_1.nrrd
│       │   ├── mask_2.nrrd
│       │   └── ...
│       ├── volume_2.nrrd (directory)
│       │   ├── mask_1.nrrd
│       │   └── ...
│       └── ...    
├── <DATASET_NAME_1>
│   ├── volumes
│   │   ├── volume_1.nrrd (directory)
│   │   └── ...
│   └── masks
│       ├── volume_1.nrrd (directory)
│       │   ├── mask_1.nrrd
│       │   └── ...
│       └── ...    
└── ...
```
`class2idx.json` is optional json file containing dictionary `{ "class_name" (str) : index (int) }`
where indexes is values from `.nrrd` masks. Don't specify 0 as index in this file (reserved value for not labeled fields).
If you don't provide this file, class names will be created automatically (`class1`, `class2`, ...).

Mask files of each volume can contain one or more objects.

`class2idx.json` example:
```
{
    "brain": 1,
    "lung": 2
}
```

# Demo

[Download demo project (... Mb)]()

Demp project contains 1 dataset `ds0` with 2 volumes.
First volume has 1 mask `.nrrd` file with 1 `brain` object.
Mask file of second volume contain 2 `lung` objects.

After uploading this project should look like:

1. Volume with `brain` object
<img />

1. Volume with two `lung` objects.
<img />
