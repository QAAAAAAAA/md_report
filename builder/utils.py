#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict
from sys import argv
from jira.resources import Issue
import datetime
import argparse


def parsed_args() -> Dict:
    parser = argparse.ArgumentParser(description="Generate test summary report")
    parser.add_argument(
        "-project_name",
        type=str,
        required=True,
        help="Project name must match with project folder %s" % ProjectName.values(),
    )

    parser.add_argument(
        "-epic_ticket", type=str, required=True, help="Epic key relate to this release or parent Epic ticket"
    )
    parser.add_argument(
        "-test_run_ids", type=str, required=True, help="all test run ids from tcms platform relate to this release"
    )
    parser.add_argument("-testing_conclusion", type=str, required=True, help="final test conclusion")

    parsed = parser.parse_args(argv[1:])
    return vars(parsed)


def is_bug_ticket(ticket: Issue) -> bool:
    if hasattr(ticket.fields, "issuetype") and ticket.fields.issuetype.name == "Bug":
        return True

    return False


def is_epic_ticket(ticket: Issue) -> bool:
    if hasattr(ticket.fields, "issuetype") and ticket.fields.issuetype.name == "Epic":
        return True

    return False


class EnumBase(object):
    _name_to_value_dict = None
    _value_to_name_dict = None

    @classmethod
    def _init_dicts(cls) -> None:
        cls._name_to_value_dict = dict(
            (k, getattr(cls, k)) for k in dir(cls) if (not k.startswith("_") and not callable(getattr(cls, k)))
        )

        cls._value_to_name_dict = dict((v, k) for k, v in cls._name_to_value_dict.items())

    @classmethod
    def name_to_value(cls, name: str, default=None) -> str:
        if cls._name_to_value_dict is None:
            cls._init_dicts()
        return cls._name_to_value_dict.get(name, default)

    @classmethod
    def value_to_name(cls, value, default=None):
        if cls._value_to_name_dict is None:
            cls._init_dicts()
        return cls._value_to_name_dict.get(value, default)

    @classmethod
    def lowercase_name(cls, value, default=None):
        name = cls.value_to_name(value, default)
        return name.lower() if name else default

    @classmethod
    def uppercase_name(cls, value, default=None):
        name = cls.value_to_name(value, default)
        return name.upper() if name else default

    @classmethod
    def titlecase_name(cls, value, default=None):
        name = cls.value_to_name(value, default)
        return name.replace("_", " ").title() if name else default

    @classmethod
    def values(cls):
        if cls._name_to_value_dict is None:
            cls._init_dicts()
        return list(cls._name_to_value_dict.values())

    @classmethod
    def names(cls):
        if cls._value_to_name_dict is None:
            cls._init_dicts()
        print(type(cls._value_to_name_dict.values()))
        return list(cls._value_to_name_dict.values())

    @classmethod
    def items(cls):
        if cls._name_to_value_dict is None:
            cls._init_dicts()
        return list(cls._name_to_value_dict.items())


class ProjectName(EnumBase):
    ANDROID_SDK = "Android_TrackingSDK"
    IOS_SDK = "iOS_TrackingSDK"
    TMS = "TMS"
    iOS_impression_kit = "iOS_impression_kit"
    TrackingHub = "TrackingHub"
    JS_SDK = "JS_TrackingSDK"


class IssueHistoryItems(EnumBase):
    VERSION = "version"
    BUGS_DURING_TEST = "bugs_during_test"
    LINE_CHANGED = "line_changed"
    LINE_COVERED = "line_covered"
    TEST_COVERAGE = "test_coverage"


def format_item_name(item):
    return " ".join([i.capitalize() for i in str(item).split("_")])


def md_file_path(project_name, epic_ticket):
    return "%s/%s_TestingReport_%s.md" % (project_name, epic_ticket, f"{datetime.datetime.now():%Y%m%d%H}")
