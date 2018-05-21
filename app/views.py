import datetime

import pytz
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Min, Max
from django.shortcuts import render, redirect

# Create your views here.
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, is_naive, make_naive
from django.views import View

from app.forms import SignUpForm
from app.models import Subject, Exam


class Signup(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        return render(request, 'registration/signup.html', {'form': form})


def get_exam_data(exam):
    # arr = arrow.get(exam.date)
    date = exam.date
    now = timezone.now()
    if now > date:
        offset = 1
        relative = " ago"
        delta = (now - date)
    else:
        offset = -1
        relative = " until"
        delta = (date - now)
    if delta.days != 0:
        relative = "<span><b>{0}</b></span><br> days".format(delta.days) + relative
        delta = "{d} days, {h} hours".format(
            h=round(delta.seconds / 3600), d=delta.days
        )
    else:
        h, seconds = divmod(delta.seconds, 3600)
        relative = "<span><b>{0}</b></span><br> hours".format(h + offset) + relative
        delta = "{h} hours, {m} minutes".format(
            h=h + offset, m=round(seconds / 60)
        )
    date = make_naive(date, exam.user.timezone).strftime("%d %B %Y %H:%M")
    return exam, date, relative, delta


def home(request):
    if not request.user.is_authenticated:
        return render(request, "base.html")
    e = Exam.objects.filter(user=request.user).order_by("date")
    pending = e.filter(date__gt=timezone.now())
    done = e.filter(date__lte=timezone.now())

    d = [get_exam_data(exam) for exam in done]
    p = [get_exam_data(exam) for exam in pending]

    json_serializer = serializers.get_serializer("json")()
    exams = json_serializer.serialize(e, ensure_ascii=False,
                                      use_natural_foreign_keys=True,
                                      use_natural_primary_keys=True)
    return render(request, template_name="home.html", context={
        "exams": exams,
        "done": d,
        "pending": p,
    })


@method_decorator(login_required, name='dispatch')
class Timetable(View):
    def get(self, request):
        e = Exam.objects.filter(user=request.user).exclude(subject__name="Results Day")
        start_date = (e.aggregate(Min("date"))["date__min"] or timezone.now()).date()
        end_date = (e.aggregate(Max("date"))["date__max"] or timezone.now()).date()
        padding = (start_date.weekday() + 1) % 6
        days = []
        for x in range(padding, 0, -1):
            background = "transparent"  # 131318"
            date = start_date - datetime.timedelta(days=x)
            today = date == datetime.date.today()
            days.append((date.day, background, today))
        delta = end_date - start_date
        for day in range(delta.days + 1):
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
            exams_js = list(exam_list)
            days.append((date.day, background, str(today), exams_js, is_exam))
        json_serializer = serializers.get_serializer("json")()
        exams = json_serializer.serialize(e, ensure_ascii=False,
                                          use_natural_foreign_keys=True,
                                          use_natural_primary_keys=True)
        return render(request, "timetable.html", context={
            "days": days,
            "exams": exams,
        })


@method_decorator(login_required, name="dispatch")
class AddExam(View):
    def get(self, request):
        return render(request, "addexam.html", context={
            "subjects": Subject.objects.all(),
        })

    def post(self, request):
        subject = Subject.objects.get(pk=request.POST["subject"])
        paper = request.POST["paper"]
        user = request.user
        print(request.POST)
        dt = "{0} {1}".format(request.POST["date"], request.POST["time"])
        dt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
        Exam.objects.create(subject=subject, paper=paper, user=user, date=dt).save()
        return redirect("home")


@method_decorator(login_required, name="dispatch")
class AddSubject(View):
    def get(self, request):
        return render(request, "addsubject.html")

    def post(self, request):
        name = request.POST["name"]
        verbose_name = request.POST["v_name"]
        colour = request.POST["colour"].strip("#")
        x = Subject.objects.create(name=name,
                                   verbose_name=verbose_name,
                                   colour=colour)
        print(x)
        return redirect("home")
