#
#   Copyright © 2022 Josep Maria Viñolas Auquer
#
#   This file is part of IsardVDI.
#
#   IsardVDI is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#
#   IsardVDI is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#   details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with IsardVDI. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from api import app

from .. import socketio
from .quotas import Quotas

quotas = Quotas()


def notify_user(user_id, type, msg_code, params={}):
    data = {
        "type": type,
        "msg_code": msg_code,
        "params": params,
    }
    socketio.emit(
        "msg",
        json.dumps(data),
        namespace="/userspace",
        room=user_id,
    )


def notify_desktop(desktop_id, type, msg_code, params={}):
    data = {
        "type": type,
        "msg_code": msg_code,
        "params": params,
    }
    socketio.emit(
        "msg",
        json.dumps(data),
        namespace="/userspace",
        room=desktop_id,
    )
