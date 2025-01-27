#!/usr/bin/env python
# -*- coding: utf-8 -*-


class APP_ERROR:
    MISSING_RUN_ID = "missing run_id when querying test cases"
    MISSING_CONF_FILE = "missing config file (report.conf)"
    MISSING_JSON_FILE = "missing JSON file for Issue History section (issue_history.json)"
    MISSING_ISSUE_KEY = "missing issue key when querying"
    MISSING_MD_FILE = "missing markdown file path"
    MISSING_FILE_FOR_PARSER = "missing file in parser function"
    GITLAB_LINE_CHANGE = "error while fetching [line change] from gitlab"
    GITLAB_PREV_BRANCH_MISSING = "cannot get previous tag version from gitlab"
    GITLAB_INFO_QUERY = "fail to query for project info"
    INVALID_PROJECT_DIR = "Could not find the director with this project name"
    MISSING_IDENTIFIER = "missing identifier ticket. Please provide an unique value such as version/epic ticket"
    MISSING_OUPUT_FOLDER = "missing output folder"


class JIRA_CONFIG:
    HOST = "https://xxx.com"
    TOKEN = "MzgxMjM2OTY4ODkyOsKaHmEG7Etmhx1Z41octAV2Ftqn"


class GITLAB_CONFIG:
    BASE_URL = "https://xx.com"
    HOST = "https://xx.com/api/v1"


class TCMS_CONFIG:
    HOST = "https://xx.com"


class MARKDOWN:
    LIST_LIMIT = 10
    ISSUE_HISTORY_LIMIT = 3
