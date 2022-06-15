import os

DEBUG = os.environ.get('DEBUG_MODE', 'enabled') == 'enabled'

bind = '0.0.0.0:' + os.environ.get('PORT', '5000')
log_level = 'debug' if DEBUG else 'info'
proc_name = 'gunicorn'
