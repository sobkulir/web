from django import template
from django.conf import settings
from trojsten.regal.tasks.models import Task, Category
from ..helpers import get_result_rounds, get_rounds_by_year,\
    get_latest_submits_for_user, get_points_from_submits

from datetime import datetime
import pytz


register = template.Library()


@register.inclusion_tag('trojsten/task_statements/parts/task_list.html', takes_context=True)
def show_task_list(context, round):
    tasks = Task.objects.filter(
        round=round
    ).order_by(
        'number'
    ).select_related(
        'round', 'round__series', 'round__series__competition'
    )
    categories = Category.objects.filter(competition=round.series.competition)

    data = {
        'round': round,
        'tasks': tasks,
        'categories': categories,
        'solutions_visible': round.solutions_are_visible_for_user(context['user']),
    }
    if context['user'].is_authenticated():
        submits = get_latest_submits_for_user(tasks, context['user'])
        results = get_points_from_submits(tasks, submits)
        data['points'] = results
    context.update(data)
    return context


@register.inclusion_tag('trojsten/task_statements/parts/buttons.html')
def show_buttons(round):
    result_rounds = get_result_rounds(round)
    categories = Category.objects.filter(
        competition=round.series.competition
    ).select_related(
        'competition'
    )
    data = {
        'round': round,
        'result_rounds': result_rounds,
        'categories': categories,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/round_list.html')
def show_round_list(user, competition):
    all_rounds = get_rounds_by_year(user, competition)
    data = {
        'all_rounds': all_rounds,
    }
    return data


@register.inclusion_tag('trojsten/task_statements/parts/progress.html', takes_context=True)
def show_progress(context, round):
    start = round.start_time
    end = round.end_time
    full = end - start
    remaining = end - datetime.now(pytz.utc)
    elapsed = full - remaining
    if remaining.days <= settings.ROUND_PROGRESS_DANGER_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_DANGER_CLASS
    elif remaining.days <= settings.ROUND_PROGRESS_WARNING_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_WARNING_CLASS
    else:
        progressbar_class = settings.ROUND_PROGRESS_DEFAULT_CLASS
    context.update({
        'start': start,
        'end': end,
        'full': full,
        'remaining': remaining,
        'elapsed': elapsed,
        'percent': 100 * elapsed.days // full.days if full.days > 0 else 100,
        'progressbar_class': progressbar_class
    })
    return context
