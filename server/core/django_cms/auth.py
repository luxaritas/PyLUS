"""
Auth
"""

from django.contrib.auth import authenticate

from cms.game.models import Account
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
            Action('auth:login_user', self.login_user, 10),
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
        ]

    def create_game_account(self, username, password, lego_club=False):
        """
        Creates a game account for a user
        """
        user = authenticate(username=username, password=password)

        if not user:
            return None

        account = Account.objects.create(user=user,
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

    def login_user(self, username, password):
        """
        Checks credentials
        """
        user = authenticate(username=username, password=password)

        if not user:
            return None

        try:
            Account.objects.get(user=user)
        except Account.DoesNotExist:
            self.create_game_account(username, password)

        return user.id

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
