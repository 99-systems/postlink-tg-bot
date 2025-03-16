from aiogram import Router



OTP_CODE_LENGTH = 4

router = Router()

def import_handlers():
    from . import login
    from . import registration
    from . import common

import_handlers()

print("Auth handler module initialized, router:", router)
print("Auth router has registered handlers:", router.message.handlers)