from arkhos.version import __version__

from arkhos.http import (
    HttpResponse as http,
    HttpResponse as html,
    JsonResponse as json,
    render,
    Request,
)

import os

if os.environ.get("ARKHOS_GLOBAL_DOMAIN"):
    from arkhos.arkhos_global import _global, get, set, sms, email
else:
    from arkhos.arkhos_local import _global, get, set, set_up_local, sms, email

    set_up_local()
