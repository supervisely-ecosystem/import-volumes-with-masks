<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/39ec61e2-41b4-4c1d-b901-1b81c75e4603" style="width: 100%;"/>

# Import Volumes with 3D Masks

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Whats-New">What's New</a> •
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

# What's New

🏷️ Version `1.0.6`
- To maintain backwards compatibility with [Export Volumes with 3D Annotations](https://ecosystem.supervisely.com/ecosystem/apps/export-volume-project) application, any Mask3D annotations that were in the project originally will be skipped during the import process. This enhancement is related to the new format for storing Mask3D objects geometry as `.nrrd` files in the `mask` directory. To learn more read [this article](https://docs.supervisely.com/data-organization/00_ann_format_navi/08_supervisely_format_volume).
- If you want to import these masks as well, please delete the `ann` folder (if present) from the dataset folder.
- If you want to import file `semantic_segmentation.nrrd` along the other masks, just rename it to any other name. In case you import only this file, it will be imported without renaming. This mechanism is made specifically to prevent duplication of objects during backwards compatibility.

🔥 Version `1.0.2`
 - Object masks import as 3D shape figures, providing convenient editing options across all planes. With this feature, you can easily manipulate object masks in various dimensions, making the editing process more intuitive and efficient.
 - Seamless Compatibility with [Export Volumes with 3D Annotations](https://ecosystem.supervisely.com/ecosystem/apps/export-volume-project). This means that projects exported with [Export App](https://app.supervisely.com/ecosystem/apps/export-volume-project) can now be directly loaded into this app without any modifications to the project folder structure. This streamlines your workflow, saving you valuable time and effort when transitioning between the two applications. But be careful with the `class2idx.json`, because this application uses its logic to work with classes, which is described in <a href="#Input-Data-Structure">Input Data Structure</a>

# How to Run

The App can be launched from the Ecosystem, Team Files, or Agent.

<details>
<summary open>Run from team files</summary>
<br>

1. Run the application from the context menu of the folder (right mouse button) on the Team Files page
  
   <img width="800" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/fc5f101e-9732-4958-9bb6-2a305241a290">


2. Fill in the project name in the `Result Project Name` field or leave the default value.
3. If you want to leave your folder in Team Files after successful import, uncheck the box `Remove temporary files after successful import` below.
4. Also, you can set `Advanced settings` such as agent, app version, and others.
5. Click the `Run` button to start the App.
</details>

<details>
<summary>Run from ecosystem</summary>
<br>

1. Click the `Run application` button on the right side of the App page. A modal window will be opened.
  
   <img width="622" alt="app" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/415e9631-5ecc-4d9d-a46e-7ca7d69ddda1">

2. If you want to upload a project folder from your computer, choose `Drag & Drop` option. You can upload the project folder to the drag-and-drop field or you can click on the drag-and-drop field and choose the project from your computer in the opened window. 
  
   <img width="337" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/2202b95a-2c36-4dbf-a7b6-bac306f8611a">

3. If you want to use a project from Team Files, choose the `Team Files` option and choose a folder to use in the app. 
  
   <img width="335" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/26ee2c1d-1894-4aa4-b0e1-ca3900163a31">

4. Fill in the project name in the `Result Project Name` field or leave the default value.
5. If you want to leave your folder in Team Files after successful import, uncheck the box `Remove temporary files after successful import` below.
6. Also, you can set `Advanced settings` such as agent, app version, and others.
7. Click the `Run` button to start the App.
</details>

<details>
<summary>Run from agent</summary>
<br>

The application supports import from a special directory on your local computer. It is made for Enterprise Edition customers who need to upload tens or even hundreds of gigabytes of data without using the drag-and-drop mechanism:

1. Run an agent on your computer where data is stored. Watch the [how-to video](https://youtu.be/aO7Zc4kTrVg).
2. Copy your data to the special folder on your computer that was created by the agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more in the [documentation](https://github.com/supervisely/docs/blob/master/customization/agents/agent-storage/agent-storage.md). Watch the [how-to video](https://youtu.be/63Kc8Xq9H0U).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right-click to open the context menu and start the App. Now the App will upload data directly from your computer to the platform.
</details>

# Input Data Structure

The Project name will not be taken from the root folder name. You should specify the project name in the modal window when you run the App.

Project directory example:

```
📂my_volumes_project
├──📜class2idx.json (optional)
├──📂dataset_01
│   ├──📂volume
│   │   ├──📜volume_1.nrrd
│   │   ├──📜volume_2.nrrd
│   │   └──📜...
│   └──📂mask
│       ├──📂volume_1.nrrd
│       │   ├──📜mask_1.nrrd
│       │   ├──📜mask_2.nrrd
│       │   └──📜...
│       ├──📂volume_2.nrrd
│       │   ├──📜mask_1.nrrd
│       │   └──📜...
│       └── ...    
├──📂dataset_02
│   ├──📂volume
│   │   ├──📜volume_1.nrrd
│   │   └──📜...
│   └──📂mask
│       ├──📂volume_1.nrrd
│       │   ├──📜mask_1.nrrd
│       │   └──📜...
│       └──📂...    
└──📂...
```
`class2idx.json` is an optional JSON file containing dictionary `{ "class_name" (str) : index (int) }`
where indexes are values from `.nrrd` masks. Don't specify `0` as index in masks (reserved value for not labeled fields).
If you don't provide `class2idx.json`, class names will be created automatically (`class_1`, `class_2`, ...).

`class2idx.json` example:
```
{
    "brain": 1,
    "lung": 2
}
```

<div>
   <details>
      <summary>ℹ️ Click here to see <code>class2idx.json</code> structure in the app versions <code>1.0.2 - 1.0.6</code></summary>
      <br/>
   <p>
      <code>class2idx.json</code> is an optional JSON file containing dictionary <code>{ "class_name" (str): index (int) }</code>
      where indexes start from <code>1</code> and increment accordingly the number of masks. If the number of classes is less than the number of masks, classes with the names like <code>class_2</code> will be created automatically for every mask. 
      If you don't provide this file, class names will be created automatically (<code>class_1</code>, <code>class_2</code>, ...).
      <br/><br/>
      💡Сlasses in JSON must be written in the same order as the masks are sorted by name inside the directory.
      <br/><br/>
      ⚠️The class indexes are not tied to the order of the files, they are only used for numbering. You can skip any number. Do not use the same one twice.
      <br/><br/>
      <code>class2idx.json</code> example:
      <br/><br/>
      <script type="application/json" id="jsonData">
         {
            "dataset_01_volume_1_mask_1": 1,
            "dataset_01_volume_1_mask_2": 2,
            "dataset_01_volume_2_mask_1": 3,
            "dataset_02_volume_1_mask_1": 4
         }
      </script>
      <br/><br/>
       Demo Project [72.9 MB] <a href=https://github.com/supervisely-ecosystem/import-volumes-with-masks/releases/download/v1.0.2/Volume_Project_with_Masks_demo.tar>Download</a>
   </p>
   </details>
</div>
<br>  

# Demo

Demo Project [72.9 MB] [Download](https://github.com/supervisely-ecosystem/import-volumes-with-masks/releases/download/v1.0.2/Volume_Project_with_Masks_demo.tar)

The demo project contains 1 dataset `dataset_01` with 2 volumes:
 - The first volume has 2 masks `.nrrd` files where each contains 1 object - `lung_1` and `lung_2`, respectively.
 - The second volume has 1 mask `.nrrd` file with a `brain` object.

After uploading this project should look like this:

1. Volume with `lung_1` and `lung_2` objects.

   <img width="1280" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/0cacc57a-511b-46c5-99bb-1a0473300372">

2. Volume with `brain` object.

   <img width="1280" src="https://github.com/supervisely-ecosystem/import-volumes-with-masks/assets/57998637/631b3410-ab79-4695-a3f4-7f1779feaf62">



