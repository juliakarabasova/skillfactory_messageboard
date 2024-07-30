import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone

from board_posts.models import Post

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_weekly_update():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)

    posts_last_week = Post.objects.filter(Q(post_date__gte=start_date, post_date__lte=end_date))

    if not posts_last_week:
        return

    subject = f'Новые объявления за неделю'

    html_content = render_to_string(
        'weekly_update.html',
        {
            'posts': posts_last_week,
        }
    )

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email='Skillfactory MessageBoard <juliakarabasova@yandex.ru>',
        to=User.objects.all().values_list('email', flat=True)
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_weekly_update,
            trigger=CronTrigger(second="0", day_of_week="mon", hour="10"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="send_weekly_update",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_update'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down successfully!")
