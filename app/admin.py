from django.contrib import admin

# Register your models here.
from app.models import Subject, Exam

admin.site.register(Subject)
admin.site.register(Exam)
