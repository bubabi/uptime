import argparse
from datetime import timedelta

from celery.utils.log import get_task_logger

import requests
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Q
from django.utils import timezone
from requests.exceptions import SSLError

from monitor.models import Monitor
from monitor.utils import MonitorStatus, MonitoringInterval
from uptime import settings


class Command(BaseCommand):
    help = "Checks the urls for monitors"

    def add_arguments(self, parser):
        # Komutumuz çoklu parametre alıyor ve zorunlu. URL'leri komut satırında yazacağız.
        parser.add_argument('urls', nargs=argparse.ZERO_OR_MORE, type=str)
        parser.add_argument('--mail_clients', action='store_true', dest='mail_clients')

    def handle(self, *args, **options):
        # Komutumuz çalıştırıldığında bu fonksiyonu çalıştıracak. Parametrelerimize de buradan erişebileceğiz.
        now = timezone.now()
        offline_urls = []
        available_monitors = Monitor.objects.filter(is_active=True).filter(
            (
                    Q(interval=MonitoringInterval.MIN_5) &
                    (
                            Q(checked_at__lt=now - timedelta(seconds=MonitoringInterval.MIN_5)) |
                            Q(checked_at__isnull=True)
                    )
            ) |
            (
                Q(interval=MonitoringInterval.MIN_30) &
                (
                        Q(checked_at__lt=now - timedelta(seconds=MonitoringInterval.MIN_30)) |
                        Q(checked_at__isnull=True)
                )
            ) |

            (
                    Q(interval=MonitoringInterval.HOUR_1) &
                    (
                            Q(checked_at__lt=now - timedelta(seconds=MonitoringInterval.HOUR_1)) |
                            Q(checked_at__isnull=True)
                    )
            )

            |

            (
                    Q(interval=MonitoringInterval.HOUR_6) &
                    (
                            Q(checked_at__lt=now - timedelta(seconds=MonitoringInterval.HOUR_6)) |
                            Q(checked_at__isnull=True)
                    )
            )

        )

        urls = options['urls']

        if urls:
            available_monitors = available_monitors.filter(url__in=urls)
        urls = available_monitors.values_list('url', flat=True).distinct().order_by('url')

        for url in urls:
            monitors = Monitor.objects.filter(is_active=True, url=url)
            self.stdout.write(self.style.WARNING("{} - {} monitor(s)".format(url, monitors.count())), ending=': ')

            try:
                response = requests.get(url)
                status = MonitorStatus.ONLINE if response.status_code == 200 else MonitorStatus.OFFLINE
            except Exception:
                status = MonitorStatus.OFFLINE

            monitors.update(status=status, checked_at=now)
            status_style = self.style.ERROR if status == MonitorStatus.OFFLINE else self.style.SUCCESS
            self.stdout.write(status_style(status))

            if status == MonitorStatus.OFFLINE:
                offline_urls.append(url)

        if options['mail_clients'] and offline_urls:
            for url in offline_urls:
                self.mail_clients(url, available_monitors)

    def mail_clients(self, url, available_monitors):
        logger = get_task_logger(__name__)
        subject = "[Uptime] Monitor is DOWN: {}".format(url)
        for monitor in available_monitors.filter(url=url, user__isnull=False):
            message_list = [
                "Hi {},".format(monitor.user.get_full_name()),
                "The monitor ({}) is currently DOWN.".format(url),
            ]

            logger.info("send mail")

            send_mail(
                subject, '\n'.join(message_list),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[monitor.user.email],
                fail_silently=False
            )
        # for url in urls:
        #     monitors = Monitor.objects.filter(is_active=True, url=url)
        #     # Komut satırından ekranlar hakkında bilgi almak için birkaç satır ekliyoruz.
        #     self.stdout.write(self.style.WARNING("{} - {} monitor(s)".format(url, monitors.count())), ending=': ')
        #
        #     try:
        #         response = requests.get(url)
        #         status = MonitorStatus.ONLINE if response.status_code == 200 else MonitorStatus.OFFLINE
        #     except SSLError:
        #         status = MonitorStatus.OFFLINE
        #
        #     monitors.update(status=status, checked_at=timezone.now())  # Sonucu saklıyoruz.
        #     status_style = self.style.ERROR if status == MonitorStatus.OFFLINE else self.style.SUCCESS
        #     self.stdout.write(status_style(status))