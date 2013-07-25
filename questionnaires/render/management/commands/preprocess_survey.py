from django.core.management.base import BaseCommand
from render.form_processor import *

class Command(BaseCommand):
	args = "<filename>"

	def handle(self, *args, **options):
		for arg in args:
			preprocess_survey(arg)

	#def handle_noargs(self, **options):
#		myvalidation()
	#	survey_to_db()
