#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from copy import deepcopy
from jira import JIRA
from builder.logger import logger
from builder.const import JIRA_CONFIG, GITLAB_CONFIG
from builder.utils import is_bug_ticket
from builder.gitlab_client import GitlabClient
from jira.resources import Issue
from jira.client import ResultList
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from os.path import join


class JiraClient:

    def __init__(self, epic_key: str) -> None:
        self.jr = JIRA(server=JIRA_CONFIG.HOST, token_auth=JIRA_CONFIG.TOKEN)
        self.gl = GitlabClient()
        self.epic_key = epic_key

    def __search_retry(self, search_sql, max_retry=5):
        res = []
        for _ in range(max_retry):
            while True:
                try:
                    res = self.jr.search_issues(search_sql, maxResults=1000)
                except:
                    continue
                break
        return res

    def __get_tasks_in_epic(self, search_type: str) -> ResultList[Issue]:
        jira_list: ResultList[Issue]
        jira_list = self.__search_retry(' "Epic Link" = %s AND type in (Bug, Task)' % self.epic_key)

        temp_jira_list = deepcopy(jira_list)

        for each in temp_jira_list:
            if (
                bool(search_type)
                and each.fields.summary.lower().find(search_type) == -1
                and not any(search_type in str(j).lower() for j in [i.name for i in each.fields.components])
            ):
                jira_list.remove(each)
            else:
                # search subtask
                for sub_task in self.__search_retry("parent=%s" % each.key):
                    lower_sub_task_summary = sub_task.fields.summary.lower()

                    if lower_sub_task_summary.find("[qa]") != -1 or lower_sub_task_summary.find("[qa sub task]") != -1:
                        continue

                    jira_list.append(sub_task)

            if "Bug" == str(each.fields.issuetype):
                for i in each.fields.issuelinks:
                    if (
                        ("inwardIssue" in i.__dict__ and i.inwardIssue in jira_list)
                        or ("outwardIssue" in i.__dict__ and i.outwardIssue in jira_list)
                    ) and each in jira_list:
                        jira_list.remove(each)

        return jira_list

    def __get_bugs_in_epic(self, search_type: str, jira_list: ResultList[Issue]) -> ResultList[Issue]:
        bug_list: ResultList[Issue]
        bug_list = self.__search_retry(' "Epic Link" = %s AND type in (Bug)' % self.epic_key)

        temp_bug_list = deepcopy(bug_list)

        for each in temp_bug_list:
            if (
                bool(search_type)
                and each.fields.summary.lower().find(search_type) == -1
                and not any(search_type in str(j).lower() for j in [i.name for i in each.fields.components])
            ):
                bug_list.remove(each)

        for each in jira_list:
            issue_link = self.__search_retry('issue in linkedIssues("%s")' % each.key)
            for issue in issue_link:
                if is_bug_ticket(issue) and issue not in bug_list:
                    bug_list.append(issue)

            if "Bug" == str(each.fields.issuetype):
                bug_list.remove(each)

        return bug_list

    def get_mr_changes_from_ticket(self, tasks):
        # some MR may bind the epic id to the title
        tasks.append(self.epic_key)

        res = defaultdict(list)
        task_mr_merge = defaultdict(set)
        opened_mrs = []
        for task in tasks:
            mrs = self.get_mr_by_commit(task)
            logger.info("collect task %s with mr info %s" % (task, mrs))
            for repo_with_namespace, mr_id_list in mrs.items():
                task_mr_merge[repo_with_namespace].update(list(mr_id_list))

        logger.info("final epic %s with mr info %s" % (self.epic_key, task_mr_merge))
        for repo_with_namespace, mr_id_list in task_mr_merge.items():
            project = self.gl.get_project_by_namespace(repo_with_namespace)
            for mr_id in mr_id_list:
                mr_and_change_lines = self.gl.get_mr_and_change_lines(project, mr_id)
                mr_url = join(GITLAB_CONFIG.BASE_URL, repo_with_namespace, "merge_requests", mr_id)
                if "merged" == mr_and_change_lines["mr_state"]:
                    res[repo_with_namespace].append(
                        {
                            "mr_link": mr_url,
                            "repo_with_namespace": repo_with_namespace,
                            "change_lines": mr_and_change_lines["change_lines"],
                        }
                    )
                elif "opened" == mr_and_change_lines["mr_state"]:
                    opened_mrs.append(mr_url)

        return opened_mrs, res

    def get_task_and_bug_in_epics(self, search_type: str = ""):
        tasks: ResultList[Issue]
        tasks = []
        bugs: ResultList[Issue]
        bugs = []

        issues = self.__get_tasks_in_epic(str(search_type).lower())
        tasks.extend(issues)
        bugs.extend(self.__get_bugs_in_epic(str(search_type).lower(), issues))

        return tasks, bugs

    def get_mr_by_commit(self, task):
        resp = requests.get(join(JIRA_CONFIG.HOST, "browse", task), auth=HTTPBasicAuth("xxx.com", "B9gpass123@"))
        soup = BeautifulSoup(resp.text, "html.parser")
        mydivs = soup.find_all("a", {"class": "link-title"})
        mr_urls = [i.get("href") for i in mydivs if GITLAB_CONFIG.BASE_URL in str(i)]
        return self.gl.get_mr_by_commits(mr_urls)
