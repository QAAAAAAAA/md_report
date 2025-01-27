#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from typing import List
from mdutils.mdutils import MdUtils
from jira.resources import Issue
from builder.tcms_client import TestCase
from builder.const import APP_ERROR, MARKDOWN, JIRA_CONFIG
from definitions import ROOT_DIR
from builder.utils import IssueHistoryItems, format_item_name


def collapsible_list(summary="Collapsible list", limit=MARKDOWN.LIST_LIMIT):
    def decorator_func(function):
        def inner(*args, **kwargs):
            list_length = 0
            md_file: MdUtils

            for each in args:
                if isinstance(each, List):
                    list_length = len(each)
                    continue

                if isinstance(each, MarkdownGenerator):
                    md_file = each.file
                    continue

            if list_length > limit:
                md_file.write("<details>\n")
                md_file.write("<summary>%s</summary>\n" % summary)

            function(*args, **kwargs)

            if list_length > limit:
                md_file.write("</details>\n")

        return inner

    return decorator_func


class MarkdownGenerator:
    file: MdUtils
    section_count = 1
    md_file_path: str

    def __init__(
        self,
        unique_id: str,
        md_file_path,
    ):
        if unique_id == "":
            raise Exception(APP_ERROR.MISSING_IDENTIFIER)

        # title = "%s_TestingReport" % unique_id

        if md_file_path == "" or md_file_path is None:
            md_file_path = "ReleaseReport.md"

        self.md_file_path = md_file_path

        self.file = MdUtils(file_name=md_file_path)

    def save(self):
        print("MD ➡️  %s/%s" % (ROOT_DIR, self.md_file_path))
        self.file.create_md_file()

    def add_testing_conclusion(self, testing_conclusion: str) -> None:
        if testing_conclusion.upper() == "PASS":
            self.file.new_header(
                1,
                '%s. Conclusion: <span style="color:green">%s</span>'
                % (self.section_count, testing_conclusion.upper()),
            )
        elif testing_conclusion.upper() == "FAIL":
            self.file.new_header(
                1,
                '%s. Conclusion: <span style="color:red">%s</span>' % (self.section_count, testing_conclusion.upper()),
            )
        else:
            self.file.new_header(
                1,
                '%s. Conclusion: <span style="color:grey">%s</span>' % (self.section_count, testing_conclusion.upper()),
            )

        self.section_count += 1

    def add_features(self, jira_features: List[Issue] = []) -> None:
        self.file.new_header(1, "%s. Features Released" % self.section_count)
        self.__generate_jira_feature_table(jira_features)
        self.section_count += 1

    def add_issue_history(self, issue_history) -> None:
        self.file.new_header(1, "%s. Feature Testing Details with History" % self.section_count)
        self.__generate_issue_history(issue_history)
        self.section_count += 1

    def add_test_cases(self, tcms_test_cases: List[TestCase] = []) -> None:
        self.file.new_header(1, "%s. Testcase and Automation Details" % self.section_count)
        self.__generate_tcms_table(tcms_test_cases)
        self.section_count += 1

    def add_section(self, title: str, callback) -> None:
        self.file.new_header(1, "%s. %s" % (self.section_count, title))

        callback(self.file)

        self.section_count += 1

    @collapsible_list("Feature List", MARKDOWN.LIST_LIMIT)
    def __generate_jira_feature_table(self, jira_features: List[Issue]):
        features_table = ["NO.", "JIRA"]
        columns = len(features_table)
        for i, feature in enumerate(jira_features):
            item = [str(i + 1), "[%s](%s)" % (feature.fields.summary, feature.permalink())]
            features_table.extend(item)

        self.file.new_table(columns=columns, rows=len(jira_features) + 1, text=features_table, text_align="left")

    def __generate_issue_history(self, issue_history):
        issue_history_table = [
            format_item_name(IssueHistoryItems.VERSION),
            format_item_name(IssueHistoryItems.BUGS_DURING_TEST),
            format_item_name(IssueHistoryItems.LINE_CHANGED),
            format_item_name(IssueHistoryItems.LINE_COVERED),
            format_item_name(IssueHistoryItems.TEST_COVERAGE),
        ]
        columns = len(issue_history_table)

        for each_repo in issue_history:
            version = str(each_repo[IssueHistoryItems.VERSION])
            version = version if not "SPDE" in version else "[%s](%s/browse/%s)" % (version, JIRA_CONFIG.HOST, version)
            issue_history_table.extend(
                [
                    version,
                    str(each_repo[IssueHistoryItems.BUGS_DURING_TEST]),
                    str(each_repo[IssueHistoryItems.LINE_CHANGED]),
                    str(each_repo[IssueHistoryItems.LINE_COVERED]),
                    str(each_repo[IssueHistoryItems.TEST_COVERAGE]),
                ]
            )

        self.file.new_table(columns=columns, rows=len(issue_history) + 1, text=issue_history_table, text_align="left")

    @collapsible_list("TCMS TestCases", MARKDOWN.LIST_LIMIT)
    def __generate_tcms_table(self, tcms_test_cases: List[TestCase]):
        tcms_table = [
            "TCMS",
            "Summary",
            "Author",
        ]

        for each in tcms_test_cases:
            tcms_table.extend(
                [
                    "[TC-%s](%s)" % (each.case_id, each.link),
                    str(each.summary),
                    str(each.assignee),
                ]
            )

        self.file.new_table(columns=3, rows=len(tcms_test_cases) + 1, text=tcms_table, text_align="left")
