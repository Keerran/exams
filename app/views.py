import datetime

import pytz
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import Min, Max, Avg, StdDev
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, is_naive, make_naive
from django.views import View
from django.views.generic import DetailView

from app.forms import SignUpForm
from app.models import Subject, Exam, Test


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
    date = make_naive(date, exam.subject.user.timezone).strftime("%d %B %Y %H:%M")
    return exam, date, relative, delta


def home(request):
    if not request.user.is_authenticated:
        return render(request, "base.html")
    e = Exam.objects.filter(subject__user=request.user).order_by("date")
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
        e = Exam.get_user_subjects(request.user)
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
            "subjects": Subject.objects.filter(user=request.user),
        })

    def post(self, request):
        subject = Subject.objects.get(name=request.POST["subject"], user=request.user)
        paper = request.POST["paper"]
        dt = "{0} {1}".format(request.POST["date"], request.POST["time"])
        dt = datetime.datetime.strptime(dt, "%Y/%m/%d %H:%M")
        max_score = request.POST["max_score"]
        duration = request.POST["duration"]
        Exam.objects.create(subject=subject, paper=paper, date=dt, duration=duration, max_score=max_score).save()
        return redirect("home")


@method_decorator(login_required, name="dispatch")
class AddSubject(View):
    def get(self, request):
        return render(request, "addsubject.html")

    def post(self, request):
        colour = request.POST["colour"].strip("#")
        Subject.objects.create(name=request.POST["name"],
                               verbose_name=request.POST["v_name"],
                               colour=colour,
                               user=request.user).save()
        return redirect("home")


class Tests(View):
    def get(self, request):
        exams = Exam.get_user_subjects(request.user).order_by()\
                    .values_list("subject", "subject__verbose_name", "subject__colour")\
                    .distinct()
        return render(request, "tests.html", context={
            "papers": exams,
        })


class SubjectTests(DetailView):
    model = Subject
    slug_field = "id"
    template_name = "subject.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["papers"] = Exam.objects.filter(subject=self.object, subject__user=self.request.user)
        return context


class ExamTests(DetailView):
    model = Exam
    slug_field = "id"
    template_name = "exam.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tests = Test.objects.filter(exam__subject__user=self.request.user)

        context["tests"] = tests
        context = {**context, **tests.aggregate(avg_score=Coalesce(Avg("score"), 0),
                                                avg_time=Coalesce(Avg("minutes_left"), 0))}
        return context

    def post(self, request, slug):
        obj = get_object_or_404(Exam, pk=slug)
        score = int(request.POST["score"])
        minutes_left = int(request.POST["minutes_left"])
        t = Test.objects.create(exam=obj, score=score, minutes_left=minutes_left)
        t.save()
        percentage = round((t.score / t.exam.max_score) * 100)
        tests = Test.objects.filter(exam__subject__user=self.request.user)
        avgs = tests.aggregate(avg_score=Coalesce(Avg("score"), 0),
                               avg_time=Coalesce(Avg("minutes_left"), 0))
        return JsonResponse({
            "pk": t.pk,
            "score": t.score,
            "percentage": percentage,
            "minutes_left": t.minutes_left,
            "max_score": obj.max_score,
            **avgs
        })


class DeleteTest(View):
    def post(self, request):
        obj = Test.objects.get(pk=self.request.POST["pk"])
        obj.delete()
        tests = Test.objects.filter(exam__subject__user=self.request.user)
        avgs = tests.aggregate(avg_score=Avg("score"), avg_time=Avg("minutes_left"))
        avgs["max_score"] = obj.exam.max_score
        return JsonResponse(avgs)
