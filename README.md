# Automatic repo-updater for Dataset Ninja repos

## How to use

1. Add git URLs to the `repos.json` file.
2. Optionally: fill the `forces` dictionary with the list of forces you want to apply to the repo.
3. Run `python main.py` to start the process. The script will iterate over all repos in the `repos.json`, launch the `main.py` script from the repo and commit the changes if there are any.

## Available forces

Specified in the forces parameters will be rebuilt regardless of their existence in the repo.

| Force caregory  |                         Available options                         |
| :-------------: | :---------------------------------------------------------------: |
|                 |      "ClassBalance", "ClassCooccurrence", "ClassesPerImage",      |
|  `force_stats`  |        "ObjectsDistribution", "ObjectSizes", "ClassSizes",        |
|                 |          "ClassesHeatmaps", "ClassesPreview", "Previews"          |
| `force_visuals` | "Poster", "SideAnnotationsGrid", "HorizontalGrid", "VerticalGrid" |
|  `force_texts`  |      "summary", "citation", "license", "readme", "download"       |
