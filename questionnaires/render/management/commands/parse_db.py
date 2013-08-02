from django.core.management.base import NoArgsCommand
from render.db_formatter import *

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
#		myvalidation()
		dbToCsv()
