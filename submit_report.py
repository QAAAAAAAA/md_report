#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ
from builder.const import GITLAB_CONFIG
from builder.request_v2 import Api
from builder.utils import md_file_path
import base64

RELEASE_REPORT_RPOJECT_ID = 22296


class SubmitReport(object):
    def __init__(self):
        self.project_name = environ.get("project_name")
        self.epic_ticket = environ.get("epic_ticket")
        self.md_file_path = md_file_path(project_name=self.project_name, epic_ticket=self.epic_ticket)
        self.api = Api(GITLAB_CONFIG.HOST)

    def __generate_files(self):
        change_files = [
            "%s/issue_history.json" % self.project_name,
            self.md_file_path,
        ]

        return [
            {
                "target_path": i,
                "content": base64.b64encode(open(i, "rb").read()).decode("utf-8"),
                "encoding": "base64",
            }
            for i in change_files
        ]

    def run(self):
        # create branch
        self.api.request_2(
            "projects/%s/branch" % RELEASE_REPORT_RPOJECT_ID,
            json_payload={"target_branch": "master", "new_branch": self.md_file_path},
            method="POST",
        )

        # commit change files
        commit_payload = {
            "target_branch": self.md_file_path,
            "file_info": self.__generate_files(),
            "commit_message": "testing report %s" % self.md_file_path,
        }
        self.api.request_2("projects/%s/commit" % RELEASE_REPORT_RPOJECT_ID, json_payload=commit_payload, method="POST")

        # create MR from change branch to master branch
        create_mr_payload = {
            "source_branch": self.md_file_path,
            "target_branch": "master",
            "title": "Merging release report %s to Master" % self.md_file_path,
            "assignee_id": 565,
            "description": "testing report %s" % self.md_file_path,
            "remove_source_branch": True,
        }
        self.api.request_2(
            "projects/%s/create_mr" % RELEASE_REPORT_RPOJECT_ID, json_payload=create_mr_payload, method="POST"
        )


SubmitReport().run()
