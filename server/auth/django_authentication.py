import secrets, base64
from datetime import datetime, timedelta
import bcrypt

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from cms.game.models import Session

from plugin import Plugin

class DjangoAuthentication(Plugin):
    def actions(self):
        return {
            'auth:check_credentials': (self.check_credentials, 10),
            #'auth:check_banned': (self.check_banned, 10),
            #'auth:check_permission': (self.check_permission, 10),
            #'auth:check_locked': (self.check_locked, 10),
            #'auth:check_activated': (self.check_activated, 10),
            #'auth:check_schedule': (self.check_schedule, 10),
            'auth:token': (self.get_token, 10),
            'auth:check_token': (self.check_token, 10),
        }
    
    def check_credentials(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            return True
        else:
            return False
        
    def get_token(self, username):
        user = User.objects.get(username=username)
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
        Session.objects.update_or_create(user=user, defaults={'token': hashed})
        return token
        
    def check_token(self, username, token):
        session = Session.objects.get(user__username=username)
        
        # Session expired
        if datetime.utcnow() - session.created > timedelta(days=1):
            session.delete()
            return False
        
        if bcrypt.checkpw(token, session.token):
            return True
        
        return False
        
