#!/usr/bin/env python
# coding=utf-8
# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

import traceback

from rethinkdb import RethinkDB

from api import app

from ..auth.authentication import *
from .api_exceptions import Error
from .flask_rethink import RDB

r = RethinkDB()


db = RDB(app)
db.init_app(app)


class ApiAllowed:
    def get_table_term(self, table, field, value, pluck=False):
        with app.app_context():
            return list(
                r.table(table)
                .filter(lambda doc: doc[field].match("(?i)" + value))
                .pluck(pluck)
                .run(db.conn)
            )

    def get_allowed(self, allowed):
        for k, v in allowed.items():
            if v != False and len(v):
                with app.app_context():
                    allowed[k] = list(
                        r.table(k)
                        .get_all(r.args(v), index="id")
                        .pluck("id", "name", "uid", "parent_category")
                        .run(db.conn)
                    )
        return allowed

    def get_items_allowed(
        self,
        payload,
        table,
        query_pluck=[],
        query_filter={},
        index="",
        index_value="",
        order=False,
        query_merge=True,
    ):
        try:
            query = r.table(table)
            if index and index_value:
                query = query.get_all(index_value, index=index)
            if query_filter:
                query = query.filter(query_filter)
            if query_merge:
                query = query.merge(
                    lambda d: {
                        "category_name": r.table("categories").get(d["category"])[
                            "name"
                        ],
                        "group_name": r.table("groups").get(d["group"])["name"],
                        "user_name": r.table("users").get(d["user"])["name"],
                    }
                )
                if len(query_pluck) > 0:
                    query = query.pluck(
                        query_pluck
                        + [
                            "id",
                            "allowed",
                            "category",
                            "category_name",
                            "group",
                            "group_name",
                            "user",
                            "user_name",
                        ]
                    )
            else:
                if len(query_pluck) > 0:
                    query = query.pluck(query_pluck)
            if order:
                query = query.order_by(order)
            with app.app_context():
                items = list(query.run(db.conn))

            allowed = []
            for item in items:

                item["editable"] = False

                if payload["role_id"] == "admin":
                    item["editable"] = True
                    allowed.append(item)
                    continue
                if (
                    payload["role_id"] == "manager"
                    and payload["category_id"] == item["category"]
                ):
                    item["editable"] = True
                    allowed.append(item)
                    continue
                if not payload.get("user_id", False):
                    continue
                if item["user"] == payload["user_id"]:
                    item["editable"] = True
                    allowed.append(item)
                    continue
                if item["allowed"]["roles"] is not False:
                    if len(item["allowed"]["roles"]) == 0:
                        allowed.append(item)
                        continue
                    else:
                        if payload["role_id"] in item["allowed"]["roles"]:
                            allowed.append(item)
                            continue
                if item["allowed"]["categories"] is not False:
                    if len(item["allowed"]["categories"]) == 0:
                        allowed.append(item)
                        continue
                    else:
                        if payload["category_id"] in item["allowed"]["categories"]:
                            allowed.append(item)
                            continue
                if item["allowed"]["groups"] is not False:
                    if len(item["allowed"]["groups"]) == 0:
                        allowed.append(item)
                        continue
                    else:
                        if payload["group_id"] in item["allowed"]["groups"]:
                            allowed.append(item)
                            continue
                if item["allowed"]["users"] is not False:
                    if len(item["allowed"]["users"]) == 0:
                        allowed.append(item)
                        continue
                    else:
                        if payload["user_id"] in item["allowed"]["users"]:
                            allowed.append(item)
                            continue
            return allowed
        except Exception:
            raise Error(
                "internal_server",
                "Internal server error",
                traceback.format_exc(),
            )

    def get_domain_reservables(self, domain_id):
        with app.app_context():
            reservables = (
                r.table("domains")
                .get(domain_id)
                .pluck({"create_dict": "reservables"})
                .run(db.conn)
            )
        return reservables.get("create_dict", {})
