"""
This is my pet project.
This script will be run when new pr merged into base branch is dev.
Script will deploy all change and alert for slack group aware about the change.
"""

import os
from main import alert_slack, GitUtils
import requests
import yaml

# define url
BASE_URL = os.getenv("BACKEND_BASE_URL")
URL_CATEGORY = f"{BASE_URL}/categories"
URL_BLOG_META = f"{BASE_URL}/blogs/"
URL_BLOG_CONTENT = f"{BASE_URL}/blogs-content"

HEADER = {"X-REQUEST-API-TOKEN": os.getenv("API_KEY_NAME")}


def read_file(file_path: str):
    with open(file_path, "r") as f:
        if file_path.endswith("yaml"):
            return yaml.safe_load(f)
        else:
            return f.read()


def update_file(file_path: str, data):
    with open(file_path, "w") as f:
        yaml.dump({"data": data}, f)


def create(yaml_path: str, url: str) -> str:
    data = read_file(yaml_path)
    req = requests.post(url=url, data=data, headers=HEADER)
    # TODO: need to check that if success then update file
    return req.json()


def update(yaml_path: str, url: str, data) -> str:  # need to load file and read id
    data = read_file(yaml_path)
    req = requests.post(url=url, data=data, headers=HEADER)
    # TODO: need to check that if success then update file
    return req.json()["msg"]


def update_content(path: str, url: str) -> str:
    content = read_file(path)
    metadata = read_file(path.replace("README.md", "info.yaml"))
    req = requests.put(
        url=url, data={"slug": metadata["slug"], "content": content}, headers=HEADER
    )
    return req.json()["msg"]


def create_content(path: str, url: str) -> str:
    content = read_file(path)
    metadata = read_file(path.replace("README.md", "info.yaml"))
    req = requests.post(
        url=url, data={"slug": metadata["slug"], "content": content}, headers=HEADER
    )
    return req.json()["msg"]


if __name__ == "__main__":
    alert_slack("Hi <!here>. new code merged in `dev` branch. Process deploy start...")

    g = GitUtils(remote_branch="dev", current_branch="dev")

    if len(g.get_category_change()) > 0:
        for x in g.get_category_change():
            if str(x["_path"]).endswith("yaml"):
                msg = (
                    create(x["_path"], URL_CATEGORY)
                    if x["_type"] == "A"
                    else update(x["_path"], URL_CATEGORY)
                )
                alert_slack(msg)

    if len(g.get_blog_change()) > 0:
        for x in g.get_blog_change():
            if x["_path"].endswith("yaml"):
                msg = (
                    create(x["_path"], URL_BLOG_META)
                    if x["_type"] == "A"
                    else update(x["_path"], URL_BLOG_META)
                )
                alert_slack(msg)

        # priority for create metadata first
        for x in g.get_blog_change():
            msg = (
                create_content(x["_path"], URL_BLOG_CONTENT)
                if x["_type"] == "A"
                else update_content(x["_path"], URL_BLOG_CONTENT)
            )
            alert_slack(msg)
