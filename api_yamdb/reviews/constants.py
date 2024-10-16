from django.conf import settings

MAX_CODE_LENGHT = 6
MAX_FIELD_LENGTH = 256
MAX_NAME_LENGHT = 20
MAX_SLUG_LENGTH = 50
MAX_VALUE_VALIDATOR = 10
MIN_VALUE_VALIDATOR = 1

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'
USERNAME_ME = 'me'

REGULAR_CHECK_LOGIN_VALID = r'^[\w.@+-]+\Z'

DATA_PATH = f'{settings.BASE_DIR}/static/data'
