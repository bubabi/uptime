from django.utils.translation import ugettext_lazy as _

USER_MONITOR_LIMIT = 10


class MonitoringInterval(object):
    MIN_5 = 5 * 60
    MIN_30 = 30 * 60
    HOUR_1 = 60 * 60
    HOUR_6 = 6 * 60 * 60

    @classmethod
    def get_choices(cls):
        choices = (
            (cls.MIN_5, _("5 minutes")),
            (cls.MIN_30, _("Half an hour")),
            (cls.HOUR_1, _("1 hour")),
            (cls.HOUR_6, _("6 hours")),
        )
        return choices

    @classmethod
    def get_default(cls):
        return cls.MIN_30


class MonitorStatus(object):
    ONLINE = 'online'
    OFFLINE = 'offline'

    @classmethod
    def get_choices(cls):
        choices = (
            (cls.ONLINE, _("Online")),
            (cls.OFFLINE, _("Offline")),
        )
        return choices