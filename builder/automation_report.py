#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


class AutomationReport:
    summary_data = []
    result_data = []

    def process_file(self, report_html):
        soup = BeautifulSoup(report_html, "html.parser")

        # Summary Section
        for element in soup.find_all("p"):
            if "check the boxes" not in element.get_text() and "tests ran in" in element.get_text():
                self.summary_data.append(["Summary", element.get_text()])
                break

        for element in soup.find_all("span"):
            if element.get_text()[0] != "E":
                self.summary_data.append([element.get("class")[0], element.get_text()])

        # Results section

        for results_table in soup.find_all("table", id="results-table"):
            for inner_table in results_table.find_all("tbody", recursive=False):
                result_temp_list = []

                for test_details_row in inner_table.find_all("tr"):
                    for test_details in test_details_row.find_all(
                        "td", ["col-result", "col-name", "col-duration", "col-links"]
                    ):
                        result_temp_list.append(test_details.get_text())

                    # Bulleted list API table
                    for api_details in test_details_row.find_all("ul"):
                        result_temp_list.append(str(api_details))

                    # Normal API table
                    if len(result_temp_list) == 4:
                        for api_details in test_details_row.find_all("table"):
                            result_temp_list.append(str(api_details))

                    for log_details in test_details_row.find_all("div", ["log", "empty-log"]):
                        # No API calls (No Api Table)
                        if len(result_temp_list) == 4:
                            result_temp_list.append("")
                        self.result_data.append(result_temp_list)
                        result_temp_list = []

        # sort by duration
        self.result_data.sort(key=lambda x: float(x[2]), reverse=True)
