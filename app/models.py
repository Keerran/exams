import datetime

import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import make_naive
from timezone_field import TimeZoneField


class User(AbstractUser):
    timezone = TimeZoneField()

    def natural_key(self):
        return self.id, self.timezone.zone

    def save(self, *args, **kwargs):
        create = not self.pk
        super().save(*args, **kwargs)
        if create:
            s = Subject.objects.create(name="Results Day", verbose_name="Results Day", colour="757575", user=self)
            s.save()
            Exam.objects.create(subject=s,
                                date=datetime.datetime(2018, 8, 16, 8, 15),
                                paper="",
                                duration=90,
                                max_score=0
                                ).save()


# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=100)
    verbose_name = models.CharField(max_length=100)
    colour = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def natural_key(self):
        return self.verbose_name, self.colour, self.user.natural_key()

    def __str__(self):
        return self.verbose_name


class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    paper = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.subject.name + " " + self.paper

    class Meta:
        ordering = ("date",)

    @classmethod
    def get_user_subjects(cls, user):
        return cls.objects.filter(subject__user=user).exclude(subject__name="Results Day")


class Test(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    minutes_left = models.SmallIntegerField()
    date = models.DateField(auto_now_add=True)
