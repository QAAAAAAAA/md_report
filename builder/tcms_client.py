#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from typing import Dict, List, Set
from tcms_api import TCMS
from builder.const import APP_ERROR
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# querying all test cases from a testRun/testPlan
class TestCase:
    case_id: int
    status_code: int
    status: str
    summary: str
    link: str

    def __init__(self, **args):
        self.case_id = args["case"]
        self.status_code = args["status"]
        self.status = args["status__name"]
        self.summary = args["case__summary"]
        self.assignee = args["assignee__username"]

    def set_test_link(self, host):
        self.link = "%s/case/%s" % (host, self.case_id)


class TCMS_Client:
    rpc: TCMS

    def __init__(self):
        self.rpc = TCMS()

    def get_test_cases(self, query: Dict) -> List[TestCase]:
        if query is None:
            raise Exception(APP_ERROR.MISSING_RUN_ID)

        test_cases = self.rpc.exec.TestExecution.filter(query)

        parsed_tc = list(map(lambda item: TestCase(**item), test_cases))
        return parsed_tc

    def get_bugs(self, case_id: int) -> List[str]:
        result = self.rpc.exec.TestExecution.get_links({"execution__case": case_id, "is_defect": True})
        links: Set[str] = set()

        for each in result:
            links.add(each.get("url", ""))

        return list(links)
