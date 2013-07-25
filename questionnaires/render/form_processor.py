from django.conf import settings
#from render.models import Formelement
#from render.models import Survey
import pdb

import codecs

def preprocess_survey(filename):
	pdb.set_trace()
	path = settings.SURVEY_DIR + filename;
	# Step 1: read the "straight from excel file and remove carriage returns in quotes"
	raw = codecs.open(path, 'r','utf-16').read();
	prepreprocessed = []
	parts = raw.split('"');
	for idx, part in enumerate(parts):
		if idx/2*2 == idx: # if even, do nothing
			prepreprocessed.append(part)
		else: #if odd, remove carriage returns
			prepreprocessed.append(part.replace("\r",""));
	prepreprocessed = " ".join(prepreprocessed);
	pdb.set_trace()
	
	# Step 2: add our questions two questions before the end
	lines = prepreprocessed.split("\r\n");
	ourquestions = codecs.open(settings.SURVEY_DIR + settings.OUR_QUESTIONS,'r','utf-16').readlines();
	processed_lines = lines[:-2] + ourquestions + lines[-2:]
	
	# Step 3: save to the final output file
	output = "\r\n".join(processed_lines);
	outfile = codecs.open(settings.SURVEY_DIR + settings.SURVEY_FILE,'w','utf-8');
	outfile.write(output);
	outfile.close();

def myvalidation():
	Formelement.objects.create().full_clean()
	Survey.objects.create().full_clean()
	Response.objects.create().full_clean()



def survey_to_db():
	# path to be hard coded in the settings
	path = settings.ROOT_DIR + '/render/data/sample_new.txt';
	index = -1;
	survey_version = ''
	question_count = 0
	survey_extra = ''
	survey = []
	
	for line in open(path):
		if line.startswith('META'):
			# meta data
			parts = line.split(':')
			for part in parts:
				part = part.strip()
			if len(parts) > 2:
				parts[1] = ':'.join(parts[1:])
			if parts[0] == 'META-VERSION':
				survey_version = parts[1]
			elif parts[0] == 'META-EXTRA':
				survey_extra = parts[1]
		elif line.startswith('Type'):
			#header line, create Survey with meta data
			survey = Survey(version=survey_version,location=path,\
				question_count = 0, extra=survey_extra)
			survey.save();
			continue
		elif line.strip() == '':
			print 'skipping empty line'
			continue
		else:
			question_count += 1;
			parts = parseline(line.replace('"',''))
			if parts[0] != 'subquestion':
				index +=1
			o = Formelement.objects.create(survey = survey, \
				screen_id = index, \
				element_type = str(parts[0]), \
				primary_content = parts[1], \
				secondary_content = parts[2], \
				additional_content = parts[3], \
				inclusion_condition = parts[4], \
				answer_type = parts[5], \
				variable_name = parts[6], \
				answers = parts[7], \
				extra_param = parts[8])		
			o.save()
	
	survey.question_count = question_count
	survey.save()
		
def parseline(string):
	#pdb.set_trace()	
	parts = string.strip().split('\t');
	#print (parts)
	if len(parts) < 9:
		parts += ['' for e in xrange(9-len(parts))]
	print parts
	if parts[0] not in ['header','question','subquestion']:
		raise NameError(parts[0] + ' is not a right Type; in ' + string)
	return parts
