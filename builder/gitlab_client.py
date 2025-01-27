#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from builder.const import APP_ERROR, GITLAB_CONFIG
from typing import List, Dict
import gitlab
import re
from os.path import join
from collections import defaultdict


class GitlabClient:

    def __init__(self):
        self.gt = gitlab.Gitlab(GITLAB_CONFIG.BASE_URL, private_token="o5u-WR5AYw6dsZrWcGh9")

    def get_project_by_namespace(self, repo_with_namespace):
        return self.gt.projects.get(repo_with_namespace)

    @staticmethod
    def get_mr_by_commits(urls):
        res = defaultdict(set)
        if isinstance(urls, str):
            urls = [urls]

        GIT_SIGN_IN_URL = "%s/users/sign_in" % GITLAB_CONFIG.BASE_URL
        with requests.Session() as session:
            token = None
            sign_in_page = session.get(GIT_SIGN_IN_URL).content
            for l in sign_in_page.split(b"\n"):
                m = re.search('name="authenticity_token" value="([^"]+)"', l.decode())
                if m:
                    token = m.group(1)
                    break

            data = {"user[login]": "username", "user[password]": "password", "authenticity_token": token}
            session.post(GIT_SIGN_IN_URL, data=data)
            for i in urls:
                mr_path = i
                if "/-/commit/" in i:
                    r = session.get(join(i, "merge_requests.json"))
                    r_content = json.loads(r.content)
                    if len(r_content) == 0:
                        continue

                    mr_path = r_content[0]["path"]

                format_path = mr_path.split("/-/merge_requests/")
                repo_with_namespace = format_path[0].replace(GITLAB_CONFIG.BASE_URL, "").strip("/")
                mr_id = format_path[1]
                res[repo_with_namespace].add(mr_id)

        return res

    @staticmethod
    def get_mr_and_change_lines(project, mr_id):
        mr = project.mergerequests.get(mr_id, lazy=True)
        changes = mr.changes()
        mr_state = changes["state"]

        if not bool(changes["diff_refs"]):
            return {"mr_state": mr_state, "change_lines": 0}

        merge_commit_sha = (
            changes["merge_commit_sha"] if bool(changes["merge_commit_sha"]) else changes["diff_refs"]["head_sha"]
        )
        base_sha = changes["diff_refs"]["base_sha"]

        url = "%s/projects/%s/compare?source_commit_hash=%s&destination_commit_hash=%s" % (
            GITLAB_CONFIG.HOST,
            project.id,
            base_sha,
            merge_commit_sha,
        )
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(res.content, project.id, mr_id, base_sha, merge_commit_sha)

        return {"mr_state": mr_state, "change_lines": res.json()["change_lines"]}

    def check_branch_status(self, project_id: int, branch_name: str):
        res = requests.get("%s/projects/%s/branch?branch_name=%s" % (GITLAB_CONFIG.HOST, project_id, branch_name))
        if res.status_code == 200:
            return True
        else:
            res = requests.get("%s/projects/%s/tags?tag_name=%s" % (GITLAB_CONFIG.HOST, project_id, branch_name))
            if res.status_code == 200:
                return True

        return False

    def get_mr(self, project_id, mr_id):
        res = requests.get("%s/projects/%s/merge_requests/%s" % (GITLAB_CONFIG.HOST, project_id, mr_id))
        return res.json()

    def get_previous_version(self, project_id: int, current_version: str) -> str:
        url = "%s/projects/%s/tags" % (GITLAB_CONFIG.HOST, project_id)

        res = requests.get(url)

        if res.status_code != 200:
            raise Exception(APP_ERROR.GITLAB_PREV_BRANCH_MISSING)

        try:
            versions: List[dict]
            versions = res.json()

            if len(versions) <= 1:
                return "master"

            version_index = -1

            for i, each in enumerate(versions):
                if each["tag_name"] == current_version:
                    version_index = i
                    break

            if version_index == -1:
                # dev haven't created a tag yet
                return versions[0].get("tag_name")

            if version_index == len(versions) - 1:
                return "master"
            return versions[version_index + 1].get("tag_name")

        except Exception as error:
            raise Exception(APP_ERROR.GITLAB_PREV_BRANCH_MISSING)

    def get_repo_data(self, project_id) -> Dict:
        url = "%s/projects/%s" % (GITLAB_CONFIG.HOST, project_id)

        res = requests.get(url)

        if res.status_code != 200:
            raise Exception(APP_ERROR.GITLAB_INFO_QUERY)

        try:
            info = res.json()

            http_url: str = info.get("http_url", "").replace(".git", "")

            return {"http_url": http_url, "repo_name": info["repo_name"]}
        except Exception as error:
            raise Exception(APP_ERROR.GITLAB_INFO_QUERY)
