from gevent import monkey

monkey.patch_all()

import logging
import os

from api.libv2 import (
    api_socketio_deployments,
    api_socketio_domains,
    api_socketio_secrets,
)
from api.libv2.maintenance import Maintenance

from api import app, socketio

debug = os.environ.get("USAGE", "production") == "devel"

if __name__ == "__main__":
    Maintenance.initialization()
    api_socketio_domains.start_domains_thread()
    api_socketio_secrets.start_secrets_thread()
    api_socketio_deployments.start_deployments_thread()
    socketio.run(app, host="0.0.0.0", port=5000, debug=debug, log_output=debug)
