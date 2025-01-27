#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from requests import Session, Request
from http import HTTPStatus
from datetime import datetime
from builder.logger import logger
from time import perf_counter
from typing import Dict, Any, Optional, Tuple, Union, Callable


class Api:
    def __init__(self, host):
        self.host = host
        self.headers = {"content-type": "application/json;charset=UTF-8"}
        self.session = Session()

    def request_2(
        self,
        uri: str,
        headers: Optional[Dict[str, str]] = {},
        files: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: Union[Tuple[str, str], Callable] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Union[bytes, Dict[str, Any], str]:
        url = self.host + "/" + uri

        req = Request(method, url, headers, files, data, params, auth, json=json_payload)
        prepped = self.session.prepare_request(req)
        start_time = perf_counter()
        try:
            with self.session.send(prepped, timeout=120) as r:
                elapsed_time = "{} ms".format(str((perf_counter() - start_time) * 1000))
                logger.info(
                    """
                    *****
                    REQUEST: %s
                    METHOD: %s
                    JSON_PAYLOAD: %s
                    DATA: %s
                    CODE: %s
                    RESPONSE: %s
                    RESPONSE TIME: %s
                    *****
                    """
                    % (url, method, json_payload, data, r.status_code, r.text, elapsed_time)
                )
                if r.status_code in [HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT]:
                    content_type = r.headers.get("Content-Type")
                    if content_type is not None and "application/json" not in content_type:
                        return r.content
                    else:
                        try:
                            return json.loads(r.text)
                        except ValueError:
                            return r.text
                else:
                    logger.error(
                        """
                            *****
                            REQUEST: %s
                            METHOD: %s
                            JSON_PAYLOAD: %s
                            DATA: %s
                            CODE: %s
                            RESPONSE: %s
                            RESPONSE TIME: %s
                            *****
                        """
                        % (url, method, json_payload, data, r.status_code, r.text, elapsed_time)
                    )
                    raise Exception(
                        datetime.strftime(datetime.now(), "%d-%b-%y %H:%M:%S"), url, r.status_code, r.text, json_payload
                    )
        except Exception as e:
            logger.error(
                """
                *****
                ERROR: %s %s %s
                ***** 
                """
                % (e, url, json_payload)
            )
            raise
