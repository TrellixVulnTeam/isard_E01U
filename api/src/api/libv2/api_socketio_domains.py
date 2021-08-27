#!/usr/bin/env python
# coding=utf-8
# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3
import time, os
from api import app
from datetime import datetime, timedelta
from pprint import pprint

from rethinkdb import RethinkDB; r = RethinkDB()
from rethinkdb.errors import ReqlTimeoutError

from .log import log
import json
import traceback

from rethinkdb.errors import ReqlDriverError
from .flask_rethink import RDB
db = RDB(app)
db.init_app(app)

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect, send
import threading

from flask_socketio import SocketIO

from .. import socketio

threads = {}

from flask import Flask, request, jsonify, _request_ctx_stack
# from flask_cors import cross_origin

from ..auth.tokens import get_token_payload, AuthError

from .helpers import (
    _parse_desktop,
    _parse_deployment_desktop,
)

## Domains Threading
class DomainsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        last_deployment=None
        while True:
            try:
                with app.app_context():
                    for c in r.table('domains').pluck(
                                [
                                    "id",
                                    "name",
                                    "icon",
                                    "image",
                                    "user",
                                    "status",
                                    "description",
                                    "parents",
                                    "persistent",
                                    "os",
                                    "tag_visible",
                                    "viewer",
                                    "options",
                                    {"create_dict": {"hardware": ["interfaces", "videos"]}},
                                    "kind",
                                    "tag",
                                ]
                            ).changes(include_initial=False).run(db.conn):
                        if self.stop==True: break

                        if c['new_val'] == None:
                            # Delete
                            if not c['old_val']['id'].startswith('_'): continue
                            event='delete'
                            if c['old_val']['kind'] != 'desktop':
                                item='template'
                            else:
                                item='desktop'
                            data=c['old_val']
                        else:
                            if not c['new_val']['id'].startswith('_'): continue
                            if c['new_val']['status'] not in ['Creating','Shutting-down','Stopping','Stopped','Starting','Started','Failed']: continue
                            if c['new_val']['kind'] != 'desktop':
                                item='template'
                            else:
                                item='desktop'

                            if c['old_val'] == None:
                                # New
                                event='add'
                            else:
                                # Update
                                event='update'
                            data=c['new_val']

                        socketio.emit(item+'_'+event, 
                                        json.dumps(data if item != 'desktop' else _parse_desktop(data)),
                                        namespace='/userspace', 
                                        room=item+'s_'+data['user'])

                        # Event delete for users when tag becomes hidden
                        if not data.get("tag_visible", True):
                            if c["old_val"] is None or c["old_val"].get("tag_visible"):
                                socketio.emit('desktop_delete', 
                                                json.dumps(data if item != 'desktop' else _parse_desktop(data)), 
                                                namespace='/userspace', 
                                                room=item+'s_'+data['user'])

                        ## Tagged desktops to advanced users
                        if data['kind']=='desktop' and data.get("tag", False):
                            deployment_id = data.get("tag")
                            data=_parse_deployment_desktop(data)
                            data.pop('name')
                            data.pop('description')
                            socketio.emit('deploymentdesktop_'+event, 
                                            json.dumps(data),
                                            namespace='/userspace', 
                                            room='deploymentdesktops_'+deployment_id)

                            ## And then update deployments to user owner (if the deployment still exists)
                            try:
                                deployment = r.table('deployments').get(deployment_id).pluck('id','name','user').merge(lambda d:
                                                                {
                                                                    "totalDesktops": r.table('domains').get_all(d['id'],index='tag').count(),
                                                                    "startedDesktops": r.table('domains').get_all(d['id'],index='tag').filter({'status':'Started'}).count()
                                                                }
                                                            ).run(db.conn)
                                if last_deployment == deployment: 
                                    continue
                                else:
                                    last_deployment = deployment
                                socketio.emit('deployment_update', 
                                                json.dumps(deployment),
                                                namespace='/userspace', 
                                                room='deployments_'+deployment['user'])
                            except:
                                None


            except ReqlDriverError:
                print('DomainsThread: Rethink db connection lost!')
                log.error('DomainsThread: Rethink db connection lost!')
                time.sleep(.5)
            except Exception:
                print('DomainsThread internal error: restarting')
                log.error('DomainsThread internal error: restarting')
                log.error(traceback.format_exc())
                time.sleep(2)

        print('DomainsThread ENDED!!!!!!!')
        log.error('DomainsThread ENDED!!!!!!!')     

def start_domains_thread():
    global threads
    if 'domains' not in threads: threads['domains']=None
    if threads['domains'] == None:
        threads['domains'] = DomainsThread()
        threads['domains'].daemon = True
        threads['domains'].start()
        log.info('DomainsThread Started')

# Domains namespace
@socketio.on('connect', namespace='/userspace')
def socketio_users_connect():
    try:
        payload = get_token_payload(request.args.get('jwt'))

        room = request.args.get('room')
        ## Rooms: desktop, deployment, deploymentdesktop
        if room == 'deploymentdesktops':
            with app.app_context():
                if r.table('deployments').get(request.args.get('deploymentId')).run(db.conn)['user'] != payload['user_id']: raise
            deployment_id = request.args.get('deploymentId')
            join_room('deploymentdesktops_'+deployment_id)
        else:
            join_room(room+'_'+payload['user_id'])
        log.debug('User '+payload['user_id']+' joined room: '+room)
    except:
        log.debug('Failed attempt to connect so socketio: '+traceback.format_exc())

@socketio.on('disconnect', namespace='/userspace')
def socketio_domains_disconnect():
    try:
        payload = get_token_payload(request.args.get('jwt'))
        for room in ['desktops','deployments','deployment_deskstop']:
            leave_room(room+'_'+payload['user_id'])
    except:
        pass