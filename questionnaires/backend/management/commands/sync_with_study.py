from backend.sync_with_study import *

from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
        def handle_noargs(self, **options):
		sync_with_study()
