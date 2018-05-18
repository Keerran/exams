import datetime

import arrow
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Min, Max
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from app.models import Subject, Exam


class Signup(View):
	def get(self, request):
		form = UserCreationForm()
		return render(request, 'registration/signup.html', {'form': form})

	def post(self, request):
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('home')
		return render(request, 'registration/signup.html', {'form': form})


def get_exam_data(exam):
	arr = arrow.get(exam.date)
	now = arrow.now()
	if now > arr:
		offset = 1
		relative = " ago"
		delta = (now - arr)
	else:
		offset = -1
		relative = " until"
		delta = (arr - now)
	if delta.days != 0:
		relative = "{0} days".format(delta.days) + relative
		delta = "{d} days, {h} hours".format(
			h=round(delta.seconds / 3600), d=delta.days
		)
	else:
		h, seconds = divmod(delta.seconds, 3600)
		relative = "{0} hours".format(h+offset) + relative
		delta = "{h} hours, {m} minutes".format(
			h=h+offset, m=round(seconds / 60)
		)
	relative = "<span><b>" + relative.replace(" ", "</b></span><br>", 1)
	arr = arr.format("D MMMM YYYY HH:mm")
	return exam, arr, relative, delta


def home(request):
	if not request.user.is_authenticated:
		return render(request, "base.html")
	e = Exam.objects.filter(user=request.user).order_by("date")
	pending = e.filter(date__gt=datetime.datetime.now())
	done = e.filter(date__lte=datetime.datetime.now())
	d = []
	for exam in done:
		data = get_exam_data(exam)
		d.append(data)
	p = []
	for exam in pending:
		data = get_exam_data(exam)
		p.append(data)

	json_serializer = serializers.get_serializer("json")()
	exams = json_serializer.serialize(e, ensure_ascii=False, use_natural_foreign_keys=True, use_natural_primary_keys=True)
	return render(request, template_name="home.html", context={
		"exams": exams,
		"done": d,
		"pending": p,
	})


@method_decorator(login_required, name='dispatch')
class Timetable(View):
	def get(self, request):
		e = Exam.objects.filter(user=request.user).exclude(subject__name="Results Day")
		start_date = e.aggregate(Min("date"))["date__min"].date()
		end_date = e.aggregate(Max("date"))["date__max"].date()
		padding = (start_date.weekday() + 1) % 6
		days = []
		for x in range(padding, 0, -1):
			background = "transparent"  # 131318"
			date = start_date - datetime.timedelta(days=x)
			today = date == datetime.date.today()
			days.append((date.day, background, today))
		delta = end_date - start_date
		for day in range(delta.days+1):
			date = (start_date + datetime.timedelta(days=day))
			background = "background: transparent"
			today = date == datetime.date.today()
			exams = Exam.objects.filter(date__date=date)
			if exams.exists():
				if len(exams) == 2:
					background = """background: linear-gradient(
					to right, 
					#{0} 0%, 
					#{0} 50%, 
					#{1} 50%, 
					#{1} 100%
					);""".format(exams[0].subject.colour, exams[1].subject.colour)
				else:
					background = "background: #{0}".format(exams[0].subject.colour)
			exam_list = exams.values_list("pk", flat=True)
			is_exam = "exam_day" if len(exam_list) != 0 else "empty"
			exams_js = ",".join(map(str, exam_list))
			days.append((date.day, background, str(today), exams_js, is_exam))
		json_serializer = serializers.get_serializer("json")()
		exams = json_serializer.serialize(e, ensure_ascii=False, use_natural_foreign_keys=True, use_natural_primary_keys=True)
		return render(request, "timetable.html", context={
			"days": days,
			"exams": exams,
		})


class Add(View):
	def get(self, request):
		return render(request, "add.html", context={
			"subjects": Subject.objects.all(),
		})

	def post(self, request):
		subject = Subject.objects.get(pk=request.POST["subject"])
		paper = request.POST["paper"]
		user = request.user
		dt = request.POST["date"] + " " + request.POST["time"]
		dt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
		Exam.objects.create(subject=subject, paper=paper, user=user, date=dt).save()
		return redirect("home")
