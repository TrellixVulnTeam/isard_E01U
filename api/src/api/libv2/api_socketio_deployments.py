#!/usr/bin/env python
# coding=utf-8
# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3
import os
import time
from datetime import datetime, timedelta
from pprint import pprint

from rethinkdb import RethinkDB

from api import app

r = RethinkDB()
import json
import traceback

from rethinkdb.errors import ReqlDriverError, ReqlTimeoutError

from .flask_rethink import RDB
from .log import log

db = RDB(app)
db.init_app(app)

import threading

from flask import request
from flask_socketio import (
    SocketIO,
    close_room,
    disconnect,
    emit,
    join_room,
    leave_room,
    rooms,
    send,
)

from .. import socketio

threads = {}

from flask import Flask, _request_ctx_stack, jsonify, request

from ..auth.tokens import AuthError, get_token_payload
from .helpers import _parse_desktop

# from flask_cors import cross_origin


## deployments Threading
class DeploymentsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while True:
            try:
                with app.app_context():
                    for c in (
                        r.table("deployments")
                        .changes(include_initial=False)
                        .run(db.conn)
                    ):
                        if self.stop == True:
                            break
                        if c["new_val"] == None:
                            event = "delete"
                            user = c["old_val"]["user"]
                            deployment = {"id": c["old_val"]["id"]}
                        elif c["old_val"] == None:
                            event = "add"
                            user = c["new_val"]["user"]
                            deployment = {
                                "id": c["new_val"]["id"],
                                "name": c["new_val"]["name"],
                                "user": user,
                                "totalDesktops": r.table("domains")
                                .get_all(c["new_val"]["id"], index="tag")
                                .count()
                                .run(db.conn),
                                "startedDesktops": 0,
                            }
                        else:
                            continue
                        socketio.emit(
                            "deployment_" + event,
                            json.dumps(deployment),
                            namespace="/userspace",
                            room="deployments_" + user,
                        )

            except ReqlDriverError:
                print("DeploymentsThread: Rethink db connection lost!")
                log.error("DeploymentsThread: Rethink db connection lost!")
                time.sleep(0.5)
            except Exception:
                print("DeploymentsThread internal error: restarting")
                log.error("DeploymentsThread internal error: restarting")
                log.error(traceback.format_exc())
                time.sleep(2)

        print("DeploymentsThread ENDED!!!!!!!")
        log.error("DeploymentsThread ENDED!!!!!!!")


def start_deployments_thread():
    global threads
    if "deployments" not in threads:
        threads["deployments"] = None
    if threads["deployments"] == None:
        threads["deployments"] = DeploymentsThread()
        threads["deployments"].daemon = True
        threads["deployments"].start()
        log.info("DeploymentsThread Started")


# # deployments namespace
# @socketio.on('connect', namespace='/deployments')
# def socketio_deployments_connect():
#     try:
#         payload = get_token_payload(request.args.get('jwt'))
#         if payload['role_id'] == 'advanced':
#             join_room(payload['user_id'])
#             log.debug('User '+payload['user_id']+' joined deployments ws')
#     except:
#         log.debug('Failed attempt to connect so socketio: '+traceback.format_exc())

# @socketio.on('disconnect', namespace='/deployments')
# def socketio_deployments_disconnect():
#     try:
#         payload = get_token_payload(request.args.get('jwt'))
#         leave_room(payload['user_id'])
#     except:
#         pass
