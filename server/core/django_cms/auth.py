"""
Auth
"""

import secrets

from datetime import datetime, timedelta

import bcrypt
from django.contrib.auth import authenticate

from cms.game.models import Session, Account
from plugin import Plugin, Action

class DjangoAuthentication(Plugin):
    """
    Django auth plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('auth:check_credentials', self.check_credentials, 10),
            Action('auth:token', self.get_new_token, 10),
            Action('auth:check_token', self.check_token, 10),
            Action('auth:get_user_id', self.get_user_id, 10),
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
            Action('auth:create_game_account', self.create_game_account, 10),
            Action('auth:has_game_account', self.has_game_account, 10),
            Action('auth:get_user_id_by_login', self.get_user_id_by_login, 10),
        ]

    def create_game_account(self, username, password, address, lego_club=False):
        """
        Creates a game account for a user
        """
        user = authenticate(username=username, password=password)

        if not user:
            return None

        token = secrets.token_urlsafe(24).encode('UTF-8')

        session = Session.objects.create(token=bcrypt.hashpw(token, bcrypt.gensalt()).decode(),
                                         address=address[0],
                                         port=address[1],
                                         objid=0)

        account = Account.objects.create(user=user,
                                         session=session,
                                         lego_club=lego_club,
                                         free_to_play=False,
                                         new_subscriber=True,
                                         front_character=0)

        return account

    def has_game_account(self, uid):
        """
        Returns a game account linked to a user
        """
        try:
            Account.objects.get(user__id=uid)
            return True
        except Account.DoesNotExist:
            return False

    def check_credentials(self, username, password, address):
        """
        Checks credentials
        """
        user = authenticate(username=username, password=password)

        if not user:
            return False

        try:
            Account.objects.get(user=user)
        except Account.DoesNotExist:
            self.create_game_account(username, password, address)

        return True

    def get_new_token(self, uid):
        """
        Returns a new token
        """
        account = Account.objects.get(user__pk=uid)
        token = secrets.token_urlsafe(24)

        hashed = bcrypt.hashpw(token.encode('latin1'), bcrypt.gensalt())

        account.session.token = hashed.decode('latin1')
        account.session.save()
        account.save()
        return token

    def check_token(self, username, token):
        """
        Checks a token
        """
        account = Account.objects.get(user__username=username)
        session = account.session

        # Session expired
        if datetime.utcnow() - session.created > timedelta(days=1):
            session.delete()
            return False

        if bcrypt.checkpw(token.encode('latin1'), session.token.encode('latin1')):
            return True

        return False

    def set_address(self, uid, address):
        """
        Sets a session address
        """
        account = Account.objects.get(user__pk=uid)
        account.session.address = address[0]
        account.session.port = address[1]
        account.session.save()
        account.save()

    def get_address(self, uid):
        """
        Returns a session address
        """
        account = Account.objects.get(user__pk=uid)
        return account.session.address

    def get_user_id_by_login(self, username, password):
        """
        Returns a user ID
        """
        user = authenticate(username=username, password=password)

        return user.pk if user else None

    def get_user_id(self, address):
        """
        Returns a session user ID
        """
        try:
            account = Account.objects.get(session__address=address[0], session__port=address[1])
            return account.user.pk
        except Account.DoesNotExist:
            return None

    def get_lego_club(self, uid):
        """
        Returns if the users is in the lego club(?)
        """
        account = Account.objects.get(user__pk=uid)
        return account.lego_club

    def get_free_to_play(self, uid):
        """
        Returns if the user is free to play
        """
        account = Account.objects.get(user__pk=uid)
        return account.free_to_play

    def get_new_subscriber(self, uid):
        """
        Returns if the user is a new subscriber
        """
        account = Account.objects.get(user__pk=uid)

        if account.new_subscriber:
            account.new_subscriber = False
            account.save()
            return True

        return False
