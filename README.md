# Release Report

## Requirements

`tcms_api` package need a `tcms.conf` file. This file should be placed in either `/etc/tcms.conf` or `~/.tcms.conf`. Please check their [doc](https://tcms-api.readthedocs.io/en/stable/modules/tcms_api.html#module-tcms_api) for detail. </br>
An example of `tcms.conf` can be found in `release_report/tcms.conf`.

## Setup

Please install all necessary packages with

```shell
$ pip3 install -r requirements.txt
$ python3 main.py -epic_ticket SPDE-43239 -test_run_ids 32,33,34,36 -testing_conclusion pass -project_name tms
```

### Params explanation

- `-epic_ticket`: Epic ticket for SDK Release (e.g. `SPDE-A,SPDE-B,SPDE-C`)
- `-test_run_ids`: Test run id from `tcms` platform (e.g. `44,45,46`)
- `-project_name`: Identification for which project to run release report
- `-testing_conclusion`: Indicates whether testing passes or fails



## Change list

### 2.0

> 1. remove multiple epic_tasks in single command
> 2. remove version and use epic key instead of it
> 3. support collect line changes from multiple repos