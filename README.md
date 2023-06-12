# Automatic repo-updater for Dataset Ninja repos

## How to use

**Note:** datasets for the repos should be already uploaded to the Supervisely instance. Otherwise, the dataset data should be presented in the path specified in the `convert.py` script. If not, the script will fail with FileNotFoundError.<br>

1. Add git URLs to the `repos.json` file.
2. Optionally: fill the `forces` dictionary with the list of forces you want to apply to the repo.
3. Run `python main.py` to start the process. The script will iterate over all repos in the `repos.json`, launch the `main.py` script from the repo and commit the changes if there are any.

## Forces typing

```python
forces: Dict[str, List[str]] = {
    "force_stats": [],
    "force_visuals": [],
    "force_texts": [],
}
```

## Available forces

Specified in the forces parameters will be rebuilt regardless of their existence in the repo.
All categories have the `"all"` option to force all items in the category.

| Force caregory  |                             Available options                              |
| :-------------: | :------------------------------------------------------------------------: |
|                 |      `"all"`, "ClassBalance", "ClassCooccurrence", "ClassesPerImage",      |
|  `force_stats`  |            "ObjectsDistribution", "ObjectSizes", "ClassSizes",             |
|                 |              "ClassesHeatmaps", "ClassesPreview", "Previews"               |
| `force_visuals` | `"all"`, "Poster", "SideAnnotationsGrid", "HorizontalGrid", "VerticalGrid" |
|  `force_texts`  |      `"all"`, "summary", "citation", "license", "readme", "download"       |
