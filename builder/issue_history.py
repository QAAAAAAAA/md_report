#!/usr/bin/env python
# -*- coding: utf-8 -*-

from definitions import ROOT_DIR
from builder.utils import IssueHistoryItems
import os
import json


class IssueHistory:

    def __init__(self, json_file: str, new_version: str = ""):
        self.versions = self.__read_json_file(json_file)
        self.new_version = new_version

    def __read_json_file(self, json_file):
        self.json_file_path = "%s/%s" % (ROOT_DIR, json_file)
        read_type = "r" if os.path.exists(self.json_file_path) else "w"
        with open(self.json_file_path, read_type) as json_file:
            try:
                return json.load(json_file)
            except:
                return []

    def generate_new_version(
        self, bugs_during_test: int = 0, line_changed: str = "", line_covered: int = 0, test_coverage: int = 0
    ):
        print("issue_history.json ➡️ ", self.json_file_path)

        new_version = {
            IssueHistoryItems.VERSION: self.new_version,
            IssueHistoryItems.BUGS_DURING_TEST: bugs_during_test,
            IssueHistoryItems.LINE_CHANGED: line_changed,
            IssueHistoryItems.LINE_COVERED: line_covered,
            IssueHistoryItems.TEST_COVERAGE: test_coverage,
        }

        versions = [new_version, *(x for x in self.versions if x["version"] != self.new_version)]

        self.versions = versions
        with open(self.json_file_path, "w") as json_file:
            json.dump(self.versions, json_file, indent=2)
