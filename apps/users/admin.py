from django.contrib import admin
from apps.scheduler.models import Teacher,Constraint,Session

admin.site.register(Teacher)
admin.site.register(Constraint)
admin.site.register(Session)
