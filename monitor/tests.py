from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from monitor.utils import MonitoringInterval, MonitorStatus


class Monitor(models.Model):
    user = models.ForeignKey(
        verbose_name=_("User"), to=settings.AUTH_USER_MODEL, related_name='monitors', on_delete=models.CASCADE,
        null=True)
    url = models.URLField(verbose_name=_("URL"))
    interval = models.PositiveSmallIntegerField(
        verbose_name=_("Monitoring interval"), choices=MonitoringInterval.get_choices(),
        default=MonitoringInterval.get_default())
    status = models.CharField(verbose_name=_("Status"), max_length=9, choices=MonitorStatus.get_choices(), blank=True)
    is_active = models.BooleanField(verbose_name=_("Is active?"), blank=True, default=True)
    checked_at = models.DateTimeField(verbose_name=_("Checked at"), null=True, editable=False)
    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Monitor")
        verbose_name_plural = _("Monitors")
        ordering = ('-created_at',)
        unique_together = ('user', 'url')

    def __str__(self):
        return self.url