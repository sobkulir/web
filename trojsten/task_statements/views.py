# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from .tasks import compile_task_statements
from trojsten.regal.tasks.models import Task
from trojsten.regal.contests.models import Round, Competition
from .helpers import get_rounds_by_year
from sendfile import sendfile
import os
from django.conf import settings


def notify_push(request, uuid):
    compile_task_statements.delay(uuid)
    return HttpResponse('')


def _statement_view(request, task_id, solution=False):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user) or (solution and not task.solutions_visible(request.user)):
        raise Http404
    try:
        path = task.get_path(solution=solution)
        template_data = {
            'task': task,
            'path': path
        }
        return render(
            request,
            'trojsten/task_statements/view_{}_statement.html'.format(
                'solution' if solution else 'task'
            ),
            template_data,
        )
    except IOError:
        raise Http404


def task_statement(request, task_id):
    return _statement_view(request, task_id, solution=False)


def solution_statement(request, task_id):
    return _statement_view(request, task_id, solution=True)


def task_list(request, round_id):
    round = get_object_or_404(Round.visible_rounds(request.user), pk=round_id)
    competitions = Competition.objects.all()  # Todo: filter by site
    template_data = {
        'round': round,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_tasks.html',
        template_data,
    )


def latest_task_list(request):
    rounds = Round.get_latest_by_competition(request.user)
    competitions = Competition.objects.all()  # Todo: filter by site
    template_data = {
        'rounds': rounds,
        'competitions': competitions,
    }
    return render(
        request,
        'trojsten/task_statements/list_latest_tasks.html',
        template_data,
    )


def view_pdf(request, round_id):
    round = get_object_or_404(Round.visible_rounds(request.user), pk=round_id)
    try:
        path = round.get_pdf_path()
        return sendfile(request, path)
    except IOError:
        raise Http404


def show_picture(request, type, task_id, picture):
    task = get_object_or_404(Task, pk=task_id)
    if not task.visible(request.user):
        raise Http404
    _, ext = os.path.splitext(picture)
    if not ext in settings.ALLOWED_PICTURE_EXT:
        raise Http404
    try:
        path = os.path.join(
            task.round.get_pictures_path(),
            picture,
        )
        return sendfile(request, path)
    except IOError:
        raise Http404