import json
import os
import shutil
import subprocess
from typing import Dict

import supervisely as sly
from git import Repo

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(CURRENT_DIR, "repos")
sly.fs.clean_dir(REPO_DIR)


def process_repo(repo: Dict):
    repo_url = repo["url"]
    repo_name = repo_url.split("/")[-1].split(".")[0]
    forces = repo.get("forces", {})

    sly.logger.info(
        f"Started processing repo {repo_name} from {repo_url} and following forces: {forces}"
    )

    local_repo_path = os.path.join(REPO_DIR, repo_name)
    sly.fs.mkdir(local_repo_path, remove_content_if_exists=True)

    repo = Repo.clone_from(repo_url, local_repo_path)

    sly.logger.info(f"Cloned repo {repo_name} to {local_repo_path}.")

    repo_requirements_path = os.path.join(local_repo_path, "requirements.txt")
    # Installing repo requirements to local environment, if requirements.txt exists.
    if os.path.exists(repo_requirements_path):
        sly.logger.info(f"Found requirements.txt in {repo_name} repo, will install requirements.")
        # Excluding supervisely and dataset-tools from requirements.txt
        repo_requirements = open(repo_requirements_path, "r").readlines()
        to_install = []
        for line in repo_requirements:
            if "supervisely" not in line and "dataset-tools" not in line:
                to_install.append(line.strip())

        sly.logger.info(f"Found {len(to_install)} requirements to install.")
        # Installing requirements.
        for line in to_install:
            sly.logger.info(f"Installing {line}...")
            return_code = subprocess.check_call(
                f"pip install {line}",
                shell=True,
                cwd=local_repo_path,
                stdout=subprocess.PIPE,
                text=True,
            )

            if return_code != 0:
                sly.logger.error(f"Failed to install {line}.")
                raise RuntimeError(f"Failed to install {line}.")

            sly.logger.info(f"Successfully installed {line}.")

    script_path = os.path.join(local_repo_path, "src", "main.py")
    command = f"PYTHONPATH=\"{local_repo_path}:${{PYTHONPATH}}\" python {script_path} --forces '{json.dumps(forces)}'"

    sly.logger.info(f"Preparing to run command: {command}")

    process = subprocess.Popen(
        command, shell=True, cwd=local_repo_path, stdout=subprocess.PIPE, text=True
    )

    for line in iter(process.stdout.readline, ""):
        print(line.strip())

    # Wait for the process to finish and get the return code.
    return_code = process.wait()

    if return_code != 0:
        sly.logger.error(f"Script finished with error code {return_code}.")
        raise RuntimeError(f"Script finished with error code {return_code}.")
    else:
        sly.logger.info("Script finished successfully.")

    delete_pycache(local_repo_path)

    # Adding all files to index.
    index = repo.index
    index.add("*")

    # If there is no changes in index, then there is nothing to commit.
    if not index.diff("HEAD"):
        sly.logger.info(f"No files was added to index in {repo_name} repo. Nothing to commit.")
        sly.fs.remove_dir(local_repo_path)
        return

    repo.index.commit("Automatic commit by repo-updater.")

    sly.logger.info("Created commit. Pushing...")

    remote = repo.remote("origin")
    remote.push()

    sly.logger.info(f"Commit was pushed to {repo_name} repo.")
    sly.fs.remove_dir(local_repo_path)


def delete_pycache(local_repo_path):
    pycache_dir = os.path.join(local_repo_path, "src", "__pycache__")
    shutil.rmtree(pycache_dir, ignore_errors=True)


if __name__ == "__main__":
    # * Path to the JSON file with repo urls and force parameters.
    # Example:
    # [
    #     {
    # ?       "url": "https://github.com/dataset-ninja/some-repo.git",
    #         "forces": {
    # *                     "force_stats": ["ObjectsDistribution"],
    # *                     "force_visuals": ["Poster"],
    # *                     "force_texts": ["all"]}
    #                   }
    #      }
    # ]

    REPOS_JSON = os.path.join(CURRENT_DIR, "repos.json")

    if not os.path.exists(REPOS_JSON):
        sly.logger.error(f"File {REPOS_JSON} not found.")
        raise FileNotFoundError(f"File {REPOS_JSON} not found.")

    repos = json.load(open(REPOS_JSON, "r"))

    sly.logger.info(f"Found {len(repos)} repos in {REPOS_JSON}.")

    for repo in repos:
        process_repo(repo)

    sly.logger.info("All repos was processed successfully.")
