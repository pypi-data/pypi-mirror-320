django-j2fa
===========

2-factor SMS authentication for Django projects. Supports Django 3.x and 4.x.


Install
=======

1. Add 'j2fa' to project settings INSTALLED_APPS
2. Add j2fa.middleware.Ensure2FactorAuthenticatedMiddleware to project settings MIDDLEWARE (after session middleware)
3. Make sure user.profile.phone resolves to phone number and user.profile.require_2fa resolves to True/False. Alternatively, you can override Ensure2FactorAuthenticatedMiddleware.is_2fa_required
4. Set project settings SMS_TOKEN and SMS_SENDER_NAME
5. Add TwoFactorAuth.as_view() to urls with name='j2fa-obtain-auth'


Supported Settings
==================

in ``settings``:
* ``SMS_TOKEN``: Kajala Group (https://kajala.com) SMS API token. Contact info@kajala.com for access
* ``SMS_SENDER_NAME``: SMS sender name, max 13 characters
* ``J2FA_ENABLED``: Enabled/disable 2FA system-wide. Default is True
* ``J2FA_SEND_TO_EMAIL``: Send 2FA codes also to email. Default is False.
* ``J2FA_FALLBACK_TO_EMAIL``: Send 2FA codes to email if SMS sending fails. Default is False.


Static Code Analysis
====================

The library passes both prospector and mypy checking. To install:

pip install prospector
pip install mypy

To analyze:

prospector
mypy .
