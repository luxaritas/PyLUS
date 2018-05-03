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
            #Action('auth:check_banned', self.check_banned, 10),
            #Action('auth:check_permission', self.check_permission, 10),
            #Action('auth:check_locked', self.check_locked, 10),
            #Action('auth:check_activated', self.check_activated, 10),
            #Action('auth:check_schedule', self.check_schedule, 10),
            Action('auth:front_character', self.get_front_character, 10),
            Action('auth:new_subscriber', self.get_new_subscriber, 10),
            Action('auth:free_to_play', self.get_lego_club, 10),
            Action('auth:lego_club', self.get_lego_club, 10),
            Action('auth:get_address', self.get_front_character, 10),
            Action('auth:set_address', self.get_new_subscriber, 10),
            Action('auth:token', self.get_token, 10),
            Action('auth:check_token', self.check_token, 10),
        ]

    def check_credentials(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            return True
        else:
            return False

    def set_address(self, username, address):
        account = Account.objects.get(user__username=username)
        account.session.address = address
        account.save()

    def get_address(self, username):
        account = Account.objects.get(user__username=username)
        return account.session.address

    def get_username(self, address):
        account = Account.objects.get(session__address=address)
        return account.user.username

    def get_token(self, username):
        account = Account.objects.get(user__username=username)
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
        account.session.token = hashed
        account.save()
        return token

    def check_token(self, username, token):
        account = Account.objects.get(user__username=username)
        session = account.session

        # Session expired
        if datetime.utcnow() - session.created > timedelta(days=1):
            session.delete()
            return False

        if bcrypt.checkpw(token, session.token):
            return True

        return False

    def get_front_character(self, username):
        account = Account.objects.get(user__username=username)
        return account.front_character

    def get_lego_club(self, username):
        account = Account.objects.get(user__username=username)
        return account.lego_club

    def get_free_to_play(self, username):
        account = Account.objects.get(user__username=username)
        return account.free_to_play

    def get_new_subscriber(self, username):
        account = Account.objects.get(user__username=username)
        return account.new_subscriber
