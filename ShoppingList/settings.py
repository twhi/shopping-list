import os
is_prod = os.environ.get('IS_PROD')

if is_prod:
    try:
        from .settings_prod import *
    except Exception as e:
        print(e)
    print('Using production environment settings.')
else:
    try:
        from .settings_dev import *
    except Exception as e:
        print(e)
    print('Using development environment settings.')
