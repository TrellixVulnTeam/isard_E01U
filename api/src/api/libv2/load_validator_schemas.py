# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

import os

import yaml
from cerberus import Validator, rules_set_registry, schema_registry

from api import app

from .helpers import _parse_string


class IsardValidator(Validator):
    def _normalize_default_setter_genid(self, document):
        return _parse_string(document["name"])

    def _normalize_default_setter_genidlower(self, document):
        return _parse_string(document["name"]).lower()

    def _normalize_default_setter_gengroupid(self, document):
        return _parse_string(
            document["parent_category"] + "-" + document["uid"]
        ).lower()

    def _normalize_default_setter_gendomainid(self, document):
        return _parse_string(
            "_" + document["user_id"] + "-" + _parse_string(document["name"])
        )

    def _normalize_default_setter_genmediaid(self, document):
        return _parse_string("_" + document["user"] + "-" + document["name"])

    def _normalize_default_setter_genuserid(self, document):
        return _parse_string(
            document["provider"]
            + "-"
            + document["category"]
            + "-"
            + document["uid"]
            + "-"
            + document["username"]
        )

    def _normalize_default_setter_gendeploymentid(self, document):
        return _parse_string(document["uid"] + "=" + document["name"])

    def _normalize_default_setter_mediaicon(self, document):
        if document["kind"] == "iso":
            return _parse_string("fa-circle-o")
        else:
            return _parse_string("fa-floppy-o")

    def _check_with_validate_vlan(self, field, value):
        """
        Value should be a string with a numeric value >= 1 and <= 4094
        """
        if not (value.isnumeric() and 1 <= int(value) <= 4094):
            self._error(
                field, "Value should be a string with a numeric value >= 1 and <= 4094"
            )

    def _check_with_validate_vlan_range(self, field, value):
        """
        Value should be a string with a numeric range like 55-33 and range should be >= 1 and <= 4094
        """
        range = value.split("-")
        if len(range) != 2 or not range[0].isnumeric() or not range[1].isnumeric():
            self._error(
                field, 'Value should be a string with a numeric range like "55-33"'
            )
        elif int(range[0]) > int(range[1]):
            self._error(
                field, "Last range number cannot be less than first range number"
            )
        elif not 1 <= int(range[0]) <= 4094 or not 1 <= int(range[1]) <= 4094:
            self._error(field, "Range limits should be >= 1 and <= 4094")


def load_validators(purge_unknown=True):
    snippets_path = os.path.join(app.root_path, "schemas/snippets")
    for snippets_filename in os.listdir(snippets_path):
        with open(os.path.join(snippets_path, snippets_filename)) as file:
            snippet_schema_yml = file.read()
            snippet_schema = yaml.load(snippet_schema_yml, Loader=yaml.FullLoader)
            schema_registry.add(snippets_filename.split(".")[0], snippet_schema)

    validators = {}
    schema_path = os.path.join(app.root_path, "schemas")
    for schema_filename in os.listdir(schema_path):
        try:
            with open(os.path.join(schema_path, schema_filename)) as file:
                schema_yml = file.read()
                schema = yaml.load(schema_yml, Loader=yaml.FullLoader)
                validators[schema_filename.split(".")[0]] = IsardValidator(
                    schema, purge_unknown=purge_unknown
                )
                validators[schema_filename.split(".")[0] + ".schema"] = schema
        except IsADirectoryError:
            None
    return validators
