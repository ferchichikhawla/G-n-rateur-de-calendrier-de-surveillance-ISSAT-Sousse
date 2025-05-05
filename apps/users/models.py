from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    is_admin=models.BooleanField(default=False)
    email=models.EmailField(_('email address'),unique=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.email

    class Meta:
        permissions = [
            ("run_assignments", "Can execute supervisor assignments"),
            ("manage_constraints", "Can manage teacher constraints"),
        ]