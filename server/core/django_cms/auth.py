import secrets, base64
from datetime import datetime, timedelta
import bcrypt

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from cms.game.models import Session, Account

from plugin import Plugin, Action

class DjangoAuthentication(Plugin):
    def actions(self):
        return [
            Action('auth:check_credentials', self.check_credentials, 10),
            Action('auth:token', self.get_new_token, 10),
            Action('auth:check_token', self.check_token, 10),
            Action('auth:get_user_id', self.get_user_id, 10)
            Action('auth:get_address', self.get_address, 10),
            Action('auth:set_address', self.set_address, 10),
            #Action('auth:check_banned', self.check_banned, 10),
            #Action('auth:check_permission', self.check_permission, 10),
            #Action('auth:check_locked', self.check_locked, 10),
            #Action('auth:check_activated', self.check_activated, 10),
            #Action('auth:check_schedule', self.check_schedule, 10),
            Action('auth:new_subscriber', self.get_new_subscriber, 10),
            Action('auth:free_to_play', self.get_lego_club, 10),
            Action('auth:lego_club', self.get_lego_club, 10),
        ]

    def check_credentials(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            return True
        else:
            return False
        
    def get_new_token(self, uid):
        account = Account.objects.get(user__pk=uid)
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
        account.session.token = hashed
        account.save()
        return token

    def check_token(self, uid, token):
        account = Account.objects.get(user__uid=uid)
        session = account.session

        # Session expired
        if datetime.utcnow() - session.created > timedelta(days=1):
            session.delete()
            return False

        if bcrypt.checkpw(token, session.token):
            return True

        return False

    def set_address(self, uid, address):
        account = Account.objects.get(user__pk=uid)
        account.session.address = address
        account.save()

    def get_address(self, uid):
        account = Account.objects.get(user__pk=uid)
        return account.session.address

    def get_user_id(self, address):
        account = Account.objects.get(session__address=address)
        return account.user.pk

    def get_lego_club(self, uid):
        account = Account.objects.get(user__pk=uid)
        return account.lego_club

    def get_free_to_play(self, uid):
        account = Account.objects.get(user__pk=uid)
        return account.free_to_play

    def get_new_subscriber(self, uid):
        account = Account.objects.get(user__pk=uid)
        
        if account.new_subscriber = True
            account.new_subscriber = False
            account.save()
            return True
        
        return False
