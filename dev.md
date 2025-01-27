### Params explanation

- `-epic_tickets`: Epic ticket for SDK Release (e.g. `ABC`)
- `-test_run_ids`: Test run id from `tcms` platform (e.g. `44,45,46`)
- `-version`: This is used for comparing previous version and releasing version
- `-project_name`: Identification for which project to run release report

## API Documentation

### `ReportManager`

This class can be inherited to have quick access to these methods and attributes such as `Jira`, `Gitlab`, `TCMS` and `Markdown` </br>

| public method                                          | description                                                             |
| :----------------------------------------------------- | :---------------------------------------------------------------------- |
| `ReportManager()`                                      | init function                                                           |
| `get_test_cases([test_run_id])`                        | query test cases from `tcms` platform and build a URL to with TCMS host |
| `get_bugs_from_tcms([tcms_test_case])`                 | query issues attached in each test case from `tcms`                     |
| `count_all_bugs([jira_issue],[issue_from_test_cases])` | count all bugs from each platform and handle duplicate bugs tickets     |

| attribute     | description                                                          |
| :------------ | :------------------------------------------------------------------- |
| `jira_client` | connection to `jira` service with predefined host/token/projectid    |
| `tcms_client` | connection to `tcms` platform with predefined host/username/password |
| `cmd_input`   | all command line arguments when starting report release script       |

### `IssueHistory`

Please use this class to create your own issue history section by providing correct `Gitlab` project id with version matches the tag from `Gitlab`. Refer to `tms/issue_histories` for example. </br>
For project that doesn't release by tag, we don't support it for now because it's hard to get line changes from different commit (will support it later).

| public method                                                                                                      | description                                                             |
| :----------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| `IssueHistory(project_id, json_file, new_version)`                                                                 | init function                                                           |
| `generate_new_version(bugs_during_test, bugs_staging, bugs_live, line_covered, test_coverage, non_live_bug_ratio)` | query test cases from `tcms` platform and build a URL to with TCMS host |

| attribute          | description                                                                                              |
| :----------------- | :------------------------------------------------------------------------------------------------------- |
| `project_id`       | project id from `Gitlab`                                                                                 |
| `project_data`     | project data (`http_url`, `repo_name`) will be queried after init instance                               |
| `gitlab_client`    | connection to `Gitlab` platform with predefined host                                                     |
| `versions`         | all version that is found in `issue_history.json` file                                                   |
| `new_version`      | current releasing version. This need to match with `Gitlab` tag and it's used for comparing line changes |
| `json_file_path`   | a file path to existing `issue_history.json` file (if exist)                                             |
| `prev_version`     | previous version that is used to comparing line changed                                                  |
| `is_version_exist` | if there is a same version in `issue_history.json` then the script will skip generating new version      |

A `.json` file for all issue history will be created and written using the value of `json_file` during initialisation.

### `MarkdownGenerator`

Please add this class into your project file when generating new release report.

| public method                                  | description                                                                                                                                                       |
| :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MarkdownGenerator(epic_ticket, md_file_path)` | init function. `epic_ticket` is used to generate markdown file name                                                                                               |
| `add_features(jira_features)`                  | create `Features Released and Tested` section.                                                                                                                    |
| `add_issue_history(issue_history)`             | create `Issues history` section                                                                                                                                   |
| `add_test_cases(tcms_test_cases)`              | create `Test Details` section                                                                                                                                     |
| `add_section(title, callback)`                 | create a custom section with title. `callback(file)` will be executed with a reference of current markdown file and `title` will be combined with `section_count` |
| `save()`                                       | call this function to save file after you finish editing                                                                                                          |

| attribute       | description                                                                                                                                              |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file`          | current editing markdown file                                                                                                                            |
| `section_count` | keeping track of section number. It will be auto incremented when use these methods `add_features`, `add_issue_history`, `add_test_cases`, `add_section` |
| `md_file_path`  | markdown file path when saving                                                                                                                           |
