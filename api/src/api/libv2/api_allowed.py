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
    def get_table_term(self, table, field, value, pluck=False, query_filter={}):
        with app.app_context():
            query = r.table(table)
            if query_filter:
                query = query.filter(query_filter)
            return list(
                query.filter(lambda doc: doc[field].match("(?i)" + value))
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
                    query = query.pluck(["allowed"] + query_pluck)
            if order:
                query = query.order_by(order)
            with app.app_context():
                items = list(query.run(db.conn))

            allowed = []
            for item in items:
                if (
                    payload["role_id"] == "admin"
                    or (
                        payload["role_id"] == "manager"
                        and payload["category_id"] == item.get("category")
                    )
                    or item.get("user") == payload["user_id"]
                ):
                    item["editable"] = True
                else:
                    item["editable"] = False
                if self.is_allowed(payload, item, table):
                    allowed.append(item)

            return allowed
        except Exception:
            raise Error(
                "internal_server",
                "Internal server error",
                traceback.format_exc(),
            )

    def is_allowed(self, payload, item, table):
        if not payload.get("user_id", False):
            return False
        if item.get("user") == payload["user_id"]:
            return True
        if item["allowed"]["roles"] is not False:
            if len(item["allowed"]["roles"]) == 0:
                return True
            else:
                if payload["role_id"] in item["allowed"]["roles"]:
                    return True
        if item["allowed"]["categories"] is not False:
            if len(item["allowed"]["categories"]) == 0:
                return True
            else:
                if payload["category_id"] in item["allowed"]["categories"]:
                    return True
        if item["allowed"]["groups"] is not False:
            if len(item["allowed"]["groups"]) == 0:
                if table in ["domains", "media"]:
                    if item.get("category") == payload["category_id"]:
                        return True
                else:
                    return True
            else:
                if payload["group_id"] in item["allowed"]["groups"]:
                    return True
        if item["allowed"]["users"] is not False:
            if len(item["allowed"]["users"]) == 0:
                if table in ["domains", "media"]:
                    if item.get("category") == payload["category_id"]:
                        return True
                else:
                    return True
                return False
            else:
                if payload["user_id"] in item["allowed"]["users"]:
                    return True

    def get_domain_reservables(self, domain_id):
        with app.app_context():
            reservables = (
                r.table("domains")
                .get(domain_id)
                .pluck({"create_dict": "reservables"})
                .run(db.conn)
            )
        return reservables.get("create_dict", {})
