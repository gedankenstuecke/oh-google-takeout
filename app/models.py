import os
import ohapi
import arrow
from django.db import models
from django.contrib.auth.models import User


class OpenHumansMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='oh_member')
    oh_id = models.CharField(max_length=16, primary_key=True)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expiration_time = models.DateTimeField()

    def get_access_token(self):
        if arrow.utcnow() >= self.expiration_time:
            self.refresh_tokens()
        return self.access_token

    def refresh_tokens(self):
        res = ohapi.api.oauth2_token_exchange(
            client_id=os.getenv('OHAPI_CLIENT_ID'),
            client_secret=os.getenv('OHAPI_CLIENT_SECRET'),
            refresh_token=self.refresh_token,
            redirect_uri='http://localhost:8000/authenticate'
        )
        self.access_token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expiration_time: arrow.utcnow().shift(
            seconds=res['expires_in']
        ).datetime
        self.save()
