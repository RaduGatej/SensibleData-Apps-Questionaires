from backend.install_survey import *

from django.core.management.base import BaseCommand

class Command(BaseCommand):
        def handle(self, *args, **options):
		print install_survey(args[0])
