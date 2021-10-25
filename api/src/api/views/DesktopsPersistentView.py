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

from flask import request

#!flask/bin/python
# coding=utf-8
from api import app

from ..libv2.apiv2_exc import *
from ..libv2.quotas import Quotas
from ..libv2.quotas_exc import *

quotas = Quotas()

from ..libv2.api_desktops_persistent import ApiDesktopsPersistent

desktops = ApiDesktopsPersistent()

from .decorators import (
    allowedTemplateId,
    has_token,
    is_admin,
    ownsCategoryId,
    ownsDomainId,
    ownsUserId,
)


@app.route("/api/v3/desktop/start/<desktop_id>", methods=["GET"])
@has_token
def api_v3_desktop_start(payload, desktop_id=False):
    if desktop_id == False:
        log.error("Incorrect access parameters. Check your query.")
        return (
            json.dumps(
                {"code": 8, "msg": "Incorrect access parameters. Check your query."}
            ),
            401,
            {"Content-Type": "application/json"},
        )

    if not ownsDomainId(payload, desktop_id):
        return (
            json.dumps({"code": 10, "msg": "Forbidden: "}),
            403,
            {"Content-Type": "application/json"},
        )
    try:
        user_id = desktops.UserDesktop(desktop_id)
    except UserNotFound:
        log.error("Desktop user not found")
        return (
            json.dumps({"code": 1, "msg": "DesktopStart user not found"}),
            404,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps({"code": 9, "msg": "DesktopStart general exception: " + error}),
            401,
            {"Content-Type": "application/json"},
        )

    try:
        quotas.DesktopStart(user_id)
    except QuotaUserConcurrentExceeded:
        log.error("Quota for user " + user_id + " to start a desktop is exceeded")
        return (
            json.dumps(
                {"code": 11, "msg": "DesktopStart user quota CONCURRENT exceeded"}
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaGroupConcurrentExceeded:
        log.error(
            "Quota for user " + user_id + " to start a desktop in his group is exceeded"
        )
        return (
            json.dumps(
                {"code": 11, "msg": "DesktopStart user limits CONCURRENT exceeded"}
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaCategoryConcurrentExceeded:
        log.error(
            "Quota for user " + user_id + " to start a desktop is his category exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user category limits CONCURRENT exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )

    except QuotaUserVcpuExceeded:
        log.error("Quota for user " + user_id + " to allocate vCPU is exceeded")
        return (
            json.dumps(
                {"code": 11, "msg": "DesktopStart user quota vCPU allocation exceeded"}
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaGroupVcpuExceeded:
        log.error(
            "Quota for user " + user_id + " to allocate vCPU in his group is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user group limits vCPU allocation exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaCategoryVcpuExceeded:
        log.error(
            "Quota for user "
            + user_id
            + " to allocate vCPU in his category is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user category limits vCPU allocation exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )

    except QuotaUserMemoryExceeded:
        log.error("Quota for user " + user_id + " to allocate MEMORY is exceeded")
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user quota MEMORY allocation exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaGroupMemoryExceeded:
        log.error(
            "Quota for user " + user_id + " for creating another desktop is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user group limits MEMORY allocation exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaCategoryMemoryExceeded:
        log.error(
            "Quota for user "
            + user_id
            + " category for desktop MEMORY allocation is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 11,
                    "msg": "DesktopStart user category limits MEMORY allocation exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )

    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps(
                {
                    "code": 9,
                    "msg": "DesktopStart quota check general exception: " + error,
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )

    # So now we have checked if desktop exists and if we can create and/or start it

    try:
        now = time.time()
        desktop_id = desktops.Start(desktop_id)
        return json.dumps({"id": desktop_id}), 200, {"Content-Type": "application/json"}
    except DesktopActionTimeout:
        log.error("Desktop " + desktop_id + " for user " + user_id + " start timeout.")
        return (
            json.dumps({"code": 2, "msg": "DesktopStart start timeout"}),
            408,
            {"Content-Type": "application/json"},
        )
    except DesktopActionFailed:
        log.error("Desktop " + desktop_id + " for user " + user_id + " start failed.")
        return (
            json.dumps({"code": 3, "msg": "DesktopStart start failed"}),
            500,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps({"code": 9, "msg": "DesktopStart general exception: " + error}),
            401,
            {"Content-Type": "application/json"},
        )


@app.route("/api/v3/desktop/stop/<desktop_id>", methods=["GET"])
@has_token
def api_v3_desktop_stop(payload, desktop_id=False):
    if desktop_id == False:
        log.error("Incorrect access parameters. Check your query.")
        return (
            json.dumps(
                {"code": 8, "msg": "Incorrect access parameters. Check your query."}
            ),
            401,
            {"Content-Type": "application/json"},
        )

    if not ownsDomainId(payload, desktop_id):
        return (
            json.dumps({"code": 10, "msg": "Forbidden: "}),
            403,
            {"Content-Type": "application/json"},
        )
    try:
        user_id = desktops.UserDesktop(desktop_id)
    except UserNotFound:
        log.error("Desktop stop user not found")
        return (
            json.dumps({"code": 1, "msg": "DesktopStop user not found"}),
            404,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps({"code": 9, "msg": "DesktopStop general exception: " + error}),
            401,
            {"Content-Type": "application/json"},
        )

    try:
        desktop_id = desktops.Stop(desktop_id)
        return json.dumps({"id": desktop_id}), 200, {"Content-Type": "application/json"}
    except DesktopActionTimeout:
        log.error("Desktop " + desktop_id + " for user " + user_id + " stop timeout.")
        return (
            json.dumps({"code": 2, "msg": "DesktopStop stop timeout"}),
            408,
            {"Content-Type": "application/json"},
        )
    except DesktopActionFailed:
        log.error("Desktop " + desktop_id + " for user " + user_id + " start failed.")
        return (
            json.dumps({"code": 3, "msg": "DesktopStop stop failed"}),
            500,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps({"code": 9, "msg": "DesktopStop general exception: " + error}),
            401,
            {"Content-Type": "application/json"},
        )


@app.route("/api/v3/persistent_desktop", methods=["POST"])
@has_token
def api_v3_persistent_desktop_new(payload):
    try:
        desktop_name = request.form.get("desktop_name", type=str)
        desktop_description = request.form.get("desktop_description", type=str)
        template_id = request.form.get("template_id", False)
        forced_hyp = request.form.get("forced_hyp", False)
        user_id = payload["user_id"]
    except Exception as e:
        return (
            json.dumps({"code": 8, "msg": "Incorrect access. exception: " + e}),
            401,
            {"Content-Type": "application/json"},
        )

    if desktop_name == None or not template_id:
        log.error("Incorrect access parameters. Check your query.")
        return (
            json.dumps(
                {"code": 8, "msg": "Incorrect access parameters. Check your query."}
            ),
            401,
            {"Content-Type": "application/json"},
        )

    if not allowedTemplateId(payload, template_id):
        return (
            json.dumps({"code": 10, "msg": "Forbidden: "}),
            403,
            {"Content-Type": "application/json"},
        )
    try:
        quotas.DesktopCreate(user_id)
    except QuotaUserNewDesktopExceeded:
        log.error(
            "Quota for user " + user_id + " for creating another desktop is exceeded"
        )
        return (
            json.dumps(
                {"code": 1, "msg": "PersistentDesktopNew user quota CREATE exceeded"}
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaGroupNewDesktopExceeded:
        log.error(
            "Quota for user "
            + user_id
            + " group for creating another desktop is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 2,
                    "msg": "PersistentDesktopNew user group quota CREATE exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except QuotaCategoryNewDesktopExceeded:
        log.error(
            "Quota for user "
            + user_id
            + " category for creating another desktop is exceeded"
        )
        return (
            json.dumps(
                {
                    "code": 3,
                    "msg": "PersistentDesktopNew user category quota CREATE exceeded",
                }
            ),
            507,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps(
                {
                    "code": 9,
                    "msg": "PersistentDesktopNew quota check general exception: "
                    + error,
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )

    try:
        now = time.time()
        # desktop_id = app.lib.DesktopNewPersistent(name, user_id,memory,vcpus,xml_id=xml_id, disk_size=disk_size)

        desktop_id = desktops.NewFromTemplate(
            desktop_name=desktop_name,
            desktop_description=desktop_description,
            template_id=template_id,
            payload=payload,
            forced_hyp=forced_hyp,
        )
        return json.dumps({"id": desktop_id}), 200, {"Content-Type": "application/json"}
    except UserNotFound:
        log.error(
            "Desktop for user "
            + user_id
            + " from template "
            + template_id
            + ", user not found"
        )
        return (
            json.dumps({"code": 1, "msg": "PersistentDesktopNew user not found"}),
            404,
            {"Content-Type": "application/json"},
        )
    except TemplateNotFound:
        log.error(
            "Desktop for user "
            + user_id
            + " from template "
            + template_id
            + " template not found."
        )
        return (
            json.dumps({"code": 2, "msg": "PersistentDesktopNew template not found"}),
            404,
            {"Content-Type": "application/json"},
        )
    except DesktopExists:
        log.error(
            "Desktop " + desktop_name + " for user " + user_id + " already exists"
        )
        return (
            json.dumps(
                {"code": 3, "msg": "PersistentDesktopNew desktop already exists"}
            ),
            404,
            {"Content-Type": "application/json"},
        )
    except DesktopNotCreated:
        log.error(
            "Desktop for user "
            + user_id
            + " from template "
            + template_id
            + " creation failed."
        )
        return (
            json.dumps({"code": 4, "msg": "PersistentDesktopNew not created"}),
            404,
            {"Content-Type": "application/json"},
        )
    ### Needs more!
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps(
                {"code": 9, "msg": "PersistentDesktopNew general exception: " + error}
            ),
            401,
            {"Content-Type": "application/json"},
        )

    # except DesktopActionTimeout:
    #    log.error("Desktop delete "+desktop_id+", desktop stop timeout")
    #    return json.dumps({"code":2,"msg":"Desktop delete stopping timeout"}), 404, {'Content-Type': 'application/json'}
    # except DesktopActionFailed:
    #    log.error("Desktop delete "+desktop_id+", desktop stop failed")
    #    return json.dumps({"code":3,"msg":"Desktop delete stopping failed"}), 404, {'Content-Type': 'application/json'}
    # except DesktopDeleteTimeout:
    #    log.error("Desktop delete "+desktop_id+", desktop delete timeout")
    #    return json.dumps({"code":4,"msg":"Desktop delete deleting timeout"}), 404, {'Content-Type': 'application/json'}


@app.route("/api/v3/desktop/from/scratch", methods=["POST"])
@has_token
def api_v3_desktop_from_scratch(payload):
    try:
        name = request.form.get("name", type=str)
        # Optionals but some required (check after)
        if payload["role_id"] == "admin":
            user_id = payload.get("user_id", "local-default-admin-admin")
        else:
            user_id = payload["user_id"]

        ## TODO: If role is manager can create in his category
        ##      If role is teacher can create in his deployment?

        description = request.form.get("description", "")
        disk_user = request.form.get("disk_user", False)
        disk_path = request.form.get("disk_path", False)
        disk_path_selected = request.form.get("disk_path_selected", "/isard/groups")
        disk_bus = request.form.get("disk_bus", "virtio")
        disk_size = request.form.get("disk_size", False)
        disks = request.form.get("disks", False)
        isos = request.form.get("isos", [])
        boot_order = request.form.get("boot_order", ["disk"])
        vcpus = request.form.get("vcpus", 2)
        memory = request.form.get("memory", 4096)
        graphics = request.form.get("graphics", ["default"])
        videos = request.form.get("videos", ["default"])
        interfaces = request.form.get("interfaces", ["default"])
        opsystem = request.form.get("opsystem", ["windows"])
        icon = request.form.get("icon", ["fa-desktop"])
        image = request.form.get("image", "")
        forced_hyp = request.form.get("forced_hyp", False)
        hypervisors_pools = request.form.get("hypervisors_pools", ["default"])
        server = request.form.get("server", False)
        virt_install_id = request.form.get("virt_install_id", False)
        xml = request.form.get("xml", False)

    except Exception as e:
        return (
            json.dumps({"code": 8, "msg": "Incorrect access. exception: " + e}),
            401,
            {"Content-Type": "application/json"},
        )

    if name == None:
        log.error("Incorrect access parameters. Check your query.")
        return (
            json.dumps(
                {
                    "code": 8,
                    "msg": "Incorrect access parameters. At least desktop name parameter is required.",
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )

    if not virt_install_id and not xml:
        return (
            json.dumps(
                {
                    "code": 8,
                    "msg": "Incorrect access parameters. We need virt_install_id or xml.",
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )
    if not disk_user and not disk_path and not disks:
        return (
            json.dumps(
                {
                    "code": 8,
                    "msg": "Incorrect access parameters. We need disk_user or disk_path or disks.",
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )
    if not boot_order not in ["disk", "iso", "pxe"]:
        return (
            json.dumps(
                {
                    "code": 8,
                    "msg": "Incorrect access parameters. Boot order items should be disk, iso or pxe.",
                }
            ),
            401,
            {"Content-Type": "application/json"},
        )

    # try:
    #     quotas.DesktopCreate(user_id)
    # except QuotaUserNewDesktopExceeded:
    #     log.error("Quota for user "+user_id+" for creating another desktop is exceeded")
    #     return json.dumps({"code":11,"msg":"PersistentDesktopNew user category quota CREATE exceeded"}), 507, {'Content-Type': 'application/json'}
    # except QuotaGroupNewDesktopExceeded:
    #     log.error("Quota for user "+user_id+" group for creating another desktop is exceeded")
    #     return json.dumps({"code":11,"msg":"PersistentDesktopNew user category quota CREATE exceeded"}), 507, {'Content-Type': 'application/json'}
    # except QuotaCategoryNewDesktopExceeded:
    #     log.error("Quota for user "+user_id+" category for creating another desktop is exceeded")
    #     return json.dumps({"code":11,"msg":"PersistentDesktopNew user category quota CREATE exceeded"}), 507, {'Content-Type': 'application/json'}
    # except Exception as e:
    #     error = traceback.format_exc()
    #     return json.dumps({"code":9,"msg":"PersistentDesktopNew quota check general exception: " + error }), 401, {'Content-Type': 'application/json'}

    try:
        desktop_id = desktops.NewFromScratch(
            name=name,
            user_id=user_id,
            description=description,
            disk_user=disk_user,
            disk_path=disk_path,
            disk_path_selected=disk_path_selected,
            disk_bus=disk_bus,
            disk_size=disk_size,
            disks=disks,
            isos=isos,  # ['_local-default-admin-admin-systemrescue-8.04-amd64.iso']
            boot_order=boot_order,
            vcpus=vcpus,
            memory=memory,
            graphics=graphics,
            videos=videos,
            interfaces=interfaces,
            opsystem=opsystem,
            icon=icon,
            image=image,
            forced_hyp=forced_hyp,
            hypervisors_pools=hypervisors_pools,
            server=server,
            virt_install_id=virt_install_id,
            xml=xml,
        )
        return json.dumps({"id": desktop_id}), 200, {"Content-Type": "application/json"}
    ## TODO: Control all exceptions and return correct code
    except Exception as e:
        error = traceback.format_exc()
        return (
            json.dumps(
                {"code": 9, "msg": "PersistentDesktopNew general exception: " + error}
            ),
            401,
            {"Content-Type": "application/json"},
        )
