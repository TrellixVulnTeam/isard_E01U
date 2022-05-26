# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

import json
import logging as log
import os
import sys
import time
import traceback
from uuid import uuid4

from flask import Response, redirect, request, url_for

#!flask/bin/python
# coding=utf-8
from api import app

from ..libv2.api_exceptions import Error
from ..libv2.quotas import Quotas
from .decorators import maintenance

quotas = Quotas()

from ..libv2.api_desktops_common import ApiDesktopsCommon

common = ApiDesktopsCommon()


@app.route("/api/v3/direct/<token>", methods=["GET"])
def api_v3_viewer(token):
    maintenance()
    viewers = common.DesktopViewerFromToken(token)
    if not viewers:
        return
    vmState = viewers.pop("vmState", None)
    return (
        json.dumps(
            {
                "desktopId": viewers.pop("desktopId", None),
                "jwt": viewers.pop("jwt", None),
                "vmName": viewers.pop("vmName", None),
                "vmDescription": viewers.pop("vmDescription", None),
                "vmState": vmState,
                "viewers": viewers,
            }
        ),
        200,
        {"Content-Type": "application/json"},
    )
