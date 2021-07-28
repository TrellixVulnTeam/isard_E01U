# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

#!flask/bin/python
# coding=utf-8
from api import app
import logging as log
import traceback

from uuid import uuid4
import time,json
import sys,os
from flask import request, jsonify
from ..libv2.apiv2_exc import *
from ..libv2.quotas_exc import *

#from ..libv2.telegram import tsend
def tsend(txt):
    None
from ..libv2.carbon import Carbon
carbon = Carbon()

from ..libv2.quotas import Quotas
quotas = Quotas()

from ..libv2.api_deployments import ApiDeployments
deployments = ApiDeployments()


@app.route('/api/v2/user/<user_id>/deployment/<deployment_id>', methods=['GET'])
def api_v2_deployment(user_id,deployment_id):

    try:
        deployment = deployments.Get(user_id,deployment_id)
        return json.dumps(deployment), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        error = traceback.format_exc()
        return json.dumps({"code":9,"msg":"DeploymentGet general exception: " + error }), 401, {'Content-Type': 'application/json'}

@app.route('/api/v2/user/<user_id>/deployments', methods=['GET'])
def api_v2_deployments(user_id):

    try:
        deployments_list = deployments.List(user_id)
        return json.dumps(deployments_list), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        error = traceback.format_exc()
        return json.dumps({"code":9,"msg":"DeploymentsList general exception: " + error }), 401, {'Content-Type': 'application/json'}
