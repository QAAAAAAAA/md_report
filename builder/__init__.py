#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
from builder.jira_client import JiraClient
import datetime
from builder.const import APP_ERROR, GITLAB_CONFIG, JIRA_CONFIG, TCMS_CONFIG
from jira.resources import Issue
from jira.client import ResultList
from builder.logger import logger
from builder.tcms_client import TCMS_Client, TestCase
from builder.issue_history import IssueHistory
from builder.markdown import MarkdownGenerator
from builder.utils import parsed_args, ProjectName, md_file_path


class AppInput(object):
    def __init__(self, project_name, epic_ticket, test_run_ids, testing_conclusion):
        self.epic_ticket = epic_ticket
        self.test_run_ids = [int(item) for item in test_run_ids.split(",")]
        self.project_name = project_name
        self.testing_conclusion = testing_conclusion


class ReportManager:

    def __init__(self):
        print("Starting report...")
        print("==================")
        self.cmd_input = AppInput(**parsed_args())
        self.jira_client = JiraClient(self.cmd_input.epic_ticket)
        self.issue_history = IssueHistory(
            json_file="%s/issue_history.json" % self.cmd_input.project_name, new_version=self.cmd_input.epic_ticket
        )
        self.tcms_client = TCMS_Client()

    def get_test_cases(self, test_run_ids: List[int]) -> List[TestCase]:
        result: List[TestCase]
        result = []
        test_ids = {}
        for test_run_id in test_run_ids:
            if test_run_id is None:
                raise Exception(APP_ERROR.MISSING_RUN_ID)

            query = {"run_id": test_run_id}
            test_cases = self.tcms_client.get_test_cases(query)

            for each in test_cases:
                if test_ids.get(each.case_id, None) is None:
                    each.set_test_link(TCMS_CONFIG.HOST)
                    result.append(each)
                    test_ids[each.case_id] = 1

        return result

    def get_bugs_from_tcms(self, test_cases: List[TestCase]) -> List[str]:
        bugs: List[str] = []

        for each in test_cases:
            bugs.extend(self.tcms_client.get_bugs(case_id=each.case_id))

        return bugs

    def count_all_bugs(self, jira_tickets: ResultList[Issue], tcms_issue_link: List[str]) -> int:
        link_map = {}

        for each in tcms_issue_link:
            link_map[each] = 1

        for each in jira_tickets:
            if link_map.get(each.permalink(), None) == 1:
                link_map.pop(each.permalink())

        return len(jira_tickets) + len(link_map.keys())

    def __del__(self):
        print("==================")
        print("Stopping report...")

    def __format_line_changed(self, line_changed):
        mr_changes = ""
        if isinstance(line_changed, dict):
            for k, v in line_changed.items():
                for i in v:
                    mr_changes += "[%s_%s](%s): %s" % (
                        k.split("/")[-1],
                        i["mr_link"].split("/")[-1],
                        i["mr_link"],
                        i["change_lines"],
                    )

                    mr_changes += "<br>"
        else:
            mr_changes = line_changed
        return mr_changes

    def run(self) -> None:

        if self.cmd_input.project_name == ProjectName.ANDROID_SDK:
            tasks, bugs = self.jira_client.get_task_and_bug_in_epics(search_type="android")
        elif self.cmd_input.project_name == ProjectName.IOS_SDK:
            tasks, bugs = self.jira_client.get_task_and_bug_in_epics(search_type="ios")
        else:
            tasks, bugs = self.jira_client.get_task_and_bug_in_epics()

        logger.info("collect tickets %s" % tasks)
        logger.info("collect bugs %s" % bugs)

        opened_mrs, mr_changes = self.jira_client.get_mr_changes_from_ticket([i.key for i in tasks])

        if len(opened_mrs) > 0:
            raise Exception("PLEASE CHECK STILL OPENED MR: %s" % opened_mrs)

        line_changed = self.__format_line_changed(mr_changes)

        self.issue_history.generate_new_version(bugs_during_test=len(bugs), line_changed=line_changed)

        md = MarkdownGenerator(
            unique_id=self.cmd_input.epic_ticket,
            md_file_path=md_file_path(project_name=self.cmd_input.project_name, epic_ticket=self.cmd_input.epic_ticket),
        )
        md.add_testing_conclusion(self.cmd_input.testing_conclusion)
        md.add_features(tasks)
        md.add_issue_history(self.issue_history.versions)
        md.add_test_cases(self.get_test_cases(test_run_ids=self.cmd_input.test_run_ids))

        md.save()
