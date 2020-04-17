from django.apps import AppConfig
from datetime import date, datetime
from django.db.utils import IntegrityError
import logging


class FEIConfig(AppConfig):
    name = 'fei'

    def ready(self):
        # Commented out since makemigrations are unable to be exectued
        # self.update_period_active_status()
        pass

    """
    Helper function which looks at today's
    date and compares it to the start_date
    and end_date of semester period which
    gives the client information whether
    specific period is active or not right now.
    """
    def update_period_active_status(self):
        from fei.models import Period
        logger = logging.getLogger(__name__)
        logger.info('Checking periods active flags...')
        updated = False
        periods = Period.objects.all()
        today = datetime.today().date()
        for period in periods:
            start_date = date.fromisoformat(str(period.start_date))
            end_date = date.fromisoformat(str(period.end_date))
            try:
                if (start_date <= today and
                    today <= end_date and
                    period.active == False):
                    period.active = True
                    period.save()
                    updated = True
                elif ((today < start_date or
                      today > end_date) and period.active is True):
                    period.active = False
                    period.save()
                    updated = True
            except IntegrityError:
                logger.error('Failed to update periods', exc_info=1)
        logger.info('Periods have been updated!') if updated is True else logger.info('Periods are OK. Nothing to update.')
