# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from fei.core import FEI

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
	args = '<filename filename ...>'
	help = 'Import filename(s) csv data from FEI.'

	def handle(self, *args, **options):

		logger.info("FILES TO IMPORT:\n\t%s", "\n\t".join(args))

		fei = FEI()
		fei.csv_import(args)