from django.core.management.base import NoArgsCommand
from render.form_processor import *

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
#		myvalidation()
		survey_to_db()
