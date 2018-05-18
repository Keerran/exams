from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Subject(models.Model):
	name = models.CharField(primary_key=True, max_length=100)
	verbose_name = models.CharField(max_length=100)
	colour = models.CharField(max_length=6)

	def natural_key(self):
		return self.verbose_name, self.colour

	def __str__(self):
		return self.verbose_name


class Exam(models.Model):
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	paper = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField()
	duration = models.PositiveSmallIntegerField()

	def __str__(self):
		return self.subject.name + " " + self.paper

	class Meta:
		ordering = ("date",)
