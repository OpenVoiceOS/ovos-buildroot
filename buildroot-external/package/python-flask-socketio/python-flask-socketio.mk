################################################################################
#
# python-flask-socketio
#
################################################################################

PYTHON_FLASK_SOCKETIO_VERSION = 5.1.1
PYTHON_FLASK_SOCKETIO_SOURCE = Flask-SocketIO-$(PYTHON_FLASK_SOCKETIO_VERSION).tar.gz
PYTHON_FLASK_SOCKETIO_SITE = https://files.pythonhosted.org/packages/5f/a5/5c03d62fdbdf0343345c8cca19d4961d8958eba54449230df2b0080b7011
PYTHON_FLASK_SOCKETIO_SETUP_TYPE = setuptools
PYTHON_FLASK_SOCKETIO_LICENSE = FIXME: please specify the exact BSD version
PYTHON_FLASK_SOCKETIO_LICENSE_FILES = LICENSE docs/license.rst

$(eval $(python-package))
