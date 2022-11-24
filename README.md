<div align="center" markdown>

<img src="" style="width: 100%;"/>

# Import Volumes with Masks

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-Run">How to Run</a> •
  <a href="#Input-Data-Structure">Input Data Structure</a>
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

1. Run agent on your computer where data is stored. Watch [how-to video](https://youtu.be/aO7Zc4kTrVg).
2. Copy your data to special folder on your computer that was created by agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more [in documentation](https://github.com/supervisely/docs/blob/master/customization/agents/agent-storage/agent-storage.md). Watch [how-to video](https://youtu.be/63Kc8Xq9H0U).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right click to open context menu and start app. Now app will upload data directly from your computer to the platform.

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
│       ├── volume_1.nrrd
│       │   ├── mask_1.nrrd
│       │   ├── mask_2.nrrd
│       │   └── ...
│       ├── volume_2.nrrd
│       │   ├── mask_1.nrrd
│       │   └── ...
│       └── ...    
├── <DATASET_NAME_1>
│   ├── volumes
│   │   ├── volume_1.nrrd
│   │   └── ...
│   └── masks
│       ├── volume_1.nrrd
│       │   ├── mask_1.nrrd
│       │   └── ...
│       └── ...    
└── ...
```
`class2idx.json` is optional json file containing dictionary `{ "class_name" (str) : index (int) }`
where indexes is values from `.nrrd` masks. Don't specify 0 as index in this file (reserved value for not labeled fields).
If you don't provide this file, class names will be created automatically (`class1`, `class2`, ...).

`class2idx.json` example:
```
{
    "brain": 1,
    "lung": 2
}
```

