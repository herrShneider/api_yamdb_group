"""Файл настроек."""

import string

USERNAME_LENGTH = 150
USERNAME_VALID_PATTERN = r'[\w.@+-]'
EMAIL_FIELD_LENGTH = 254
URL_PROFILE_PREF = 'me'
MIN_RATING = 1
MAX_RATING = 10

HTTP_METHODS = ('get', 'post', 'patch', 'delete')
NOT_APPLICABLE_CONF_CODE = 'N/A'
CONF_CODE_LENGTH = 16
CONF_CODE_PATTERN = string.ascii_letters + string.digits
SERVER_EMAIL = 'from@example.com'
