"""
Auth
"""

import secrets

import bcrypt
from django.contrib.auth import authenticate
from django.utils.timezone import now

from cms.game.models import Account, Session
from server.plugin import Plugin, Action

class DjangoAuthentication(Plugin):
    """
    Django auth plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('auth:login_user', self.login_user, 10),
            Action('session:new_session', self.new_session, 10),
            #Action('auth:check_banned', self.check_banned, 10),
            #Action('auth:check_permission', self.check_permission, 10),
            #Action('auth:check_locked', self.check_locked, 10),
            #Action('auth:check_activated', self.check_activated, 10),
            #Action('auth:check_schedule', self.check_schedule, 10),
            Action('auth:new_subscriber', self.get_new_subscriber, 10),
            Action('auth:free_to_play', self.get_lego_club, 10),
            Action('auth:lego_club', self.get_lego_club, 10),
        ]

    def login_user(self, username, password):
        """
        Checks credentials
        """
        user = authenticate(username=username, password=password)

        if not user:
            return None

        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            account = Account.objects.create(user=user,
                                             lego_club=False,
                                             free_to_play=False,
                                             new_subscriber=True)

        return account
    
    def new_session(self, account, address):
        """
        Creates a new session
        """
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token.encode('latin1'), bcrypt.gensalt())

        session = Session(account=account, ip=address[0], port=address[1], token=hashed, created=now())
        session.save()

        return token

    def get_lego_club(self, account):
        """
        Returns if the users is in the lego club(?)
        """
        return account.lego_club

    def get_free_to_play(self, account):
        """
        Returns if the user is free to play
        """
        return account.free_to_play

    def get_new_subscriber(self, account):
        """
        Returns if the user is a new subscriber
        """
        if account.new_subscriber:
            account.new_subscriber = False
            account.save()
            return True

        return False
