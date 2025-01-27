#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builder import AppInput, ReportManager
from builder.utils import parsed_args, ProjectName


if __name__ == "__main__":
    cmd_input = AppInput(**parsed_args())

    if cmd_input.project_name in ProjectName.values():
        ReportManager().run()
    else:
        print("currnet only support project %s" % ProjectName.values())
        import sys

        sys.exit(0)
