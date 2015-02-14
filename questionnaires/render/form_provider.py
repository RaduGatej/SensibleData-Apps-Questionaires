import json
import formwidget as fw
from render.models import Response, Survey
from django.conf import settings
import pdb
from LOCAL_surveys import SURVEYS
import simplecrypt
import datetime
from django.utils import timezone

#SURVEY_PATH = settings.SURVEY_DIR + settings.SURVEY_FILE

_DEBUG = False
def DEBUG():
	if _DEBUG:
		pdb.set_trace()

def get_first_question(user_id, survey_version):
	questions = get_questions_list(survey_version);
	return return_question(user_id, survey_version, questions[0]);

def get_previous_question(user_id, survey_version, current_name):
	#pdb.set_trace()
	questions = get_questions_list(survey_version);
	if current_name == '__goodbye':
		for i in range(1,len(questions)):
			conditioned_question = get_conditioned_question(user_id, survey_version, questions[-i])
			if conditioned_question != None:
				return return_question(user_id, survey_version, conditioned_question)
			#if check_condition(user_id, survey_version, questions[-i].inclusion_condition):
			#	if isinstance(questions[-i], fw.GridQuestion):
			#		for ii in range(len(questions[-i].data)-1, -1, -1):
			#			sub = questions[-i].data[ii]
			#			if not check_condition(user_id, survey_version, sub.inclusion_condition):
			#				questions[-i].data.remove(sub)
			#	return return_question(user_id, survey_version, questions[-i])
	previous = None;
	for question in questions:
		if question.variable_name == current_name:
			if previous == None:
				return return_question(user_id, survey_version, questions[0])
			else:
				return return_question(user_id, survey_version, previous);
		else:
			conditioned_question = get_conditioned_question(user_id, survey_version, question)
			if conditioned_question != None:
				#if isinstance(question, fw.GridQuestion):
				#	for ii in range(len(question.data)-1, -1, -1):
				#		sub = question.data[ii]
				#		if not check_condition(user_id, survey_version, sub.inclusion_condition):
				#			question.data.remove(sub)
				previous = question
	raise NameError(current_name + ' is not a valid question name');

def get_next_question(user_id, survey_version, current_name):
	
	questions = get_questions_list(survey_version);
	now_is_the_time = False;
	for question in questions:	
		if now_is_the_time:
			#pdb.set_trace()
			#if check_condition(user_id, survey_version, question.inclusion_condition):
			#	if isinstance(question, fw.GridQuestion):
			#		for ii in range(len(question.data)-1, -1, -1):
			#			sub = question.data[ii]
			#			if not check_condition(user_id, survey_version, sub.inclusion_condition):
			#				question.data.remove(sub)
			conditioned_question = get_conditioned_question(user_id, survey_version, question)
			if conditioned_question != None:
				return return_question(user_id, survey_version, conditioned_question)
			else:
				pass
		elif question.variable_name == current_name:
			if needs_answer(user_id, survey_version, question):
				return return_question(user_id, survey_version, get_conditioned_question(user_id, survey_version, question))
			now_is_the_time = True
		else:
			pass
	if now_is_the_time:
		return None;
	else:
		raise NameError(current_name + ' is not a valid question name');
			

def get_next_unanswered_question(user_id,survey_version):
	for question in get_questions_list(survey_version):
		if needs_answer(user_id, survey_version, question):
			return return_question(user_id, survey_version, get_conditioned_question(user_id, survey_version, question))
	#pdb.set_trace()
	#entries = Response.objects.filter(user=user_id,\
	#			form_version=survey_version);
	#if len(entries) > 0:
	#	answers = {};
	#	for e in entries:
	#		answers[e.variable_name] = e.response;
	#	for question in questions:
			#if check_condition(user_id, survey_version, question.inclusion_condition):
			#	if isinstance(question, fw.GridQuestion):
			#		for ii in range(len(question.data)-1, -1, -1):
			#			sub = question.data[ii]
			#			if not check_condition(user_id, survey_version, sub.inclusion_condition):
			#				question.data.remove(sub)
			#		for sub in question.data:
			#			if sub.variable_name not in answers.keys():
			#				return return_question(user_id, survey_version, question)
	#		conditioned_question = get_conditioned_question(question)
	#		if conditioned_question != None:
	#			elif question.variable_name not in answers.keys():
	#				# if q.inclusion_condition != '':
	#				return return_question(user_id, survey_version, question)
	#else:
	#	return return_question(user_id, survey_version, questions[0]);

def get_autocomplete_data_for_user_from_source(user_id, source_type, source_link):
	autocomplete_data = {}
	if source_type == 'file':
		try:
			autocomplete_data = json.loads(open(settings.ROOT_DIR + source_link, "r").read())
		except Exception, e:
			print "Error accessing autocomplete items source file: " + str(e)
	return autocomplete_data.get(unicode(user_id), [])


def pseudonyms_to_facebook_names(response):
	facebook_names_to_pseudonyms = {}
	try:
		facebook_names_to_pseudonyms = json.loads(open(settings.ROOT_DIR + settings.FACEBOOK_NAMES_FILE).read())
	except Exception, e:
		print "Error accessing pseudonyms file: " + str(e)
	pseudonyms_to_facebook_names_dict = {v: k for k, v in facebook_names_to_pseudonyms.items()}
	response_pseudonyms = response.split(";")
	facebook_names = []
	for pseudonym in response_pseudonyms:
		facebook_name = pseudonyms_to_facebook_names_dict.get(pseudonym)
		if not facebook_name:
			facebook_name = simplecrypt.decrypt(settings.FACEBOOK_NAMES_ENCRYPTION_PASSWORD, pseudonym.decode("hex"))
		facebook_names.append(facebook_name)
	return "\r\n".join(facebook_names)


def return_question(user_id, survey_version, question):
	#set_current_question(user_id, survey_version, question.variable_name)
	DEBUG()
	if isinstance(question, fw.GridQuestion):
		for sub in question.data:
			var_name = sub.variable_name
			response = get_response(user_id, survey_version, var_name)
			if response != None:
				sub.set_answer(response)	
	elif isinstance(question, fw.Header):
		pass
	elif isinstance(question, fw.AutocompleteItemsQuestion):
		data_source_type, data_source_link = question.get_data_source_link()
		question.set_autocomplete_items(get_autocomplete_data_for_user_from_source(user_id, data_source_type, data_source_link))
		response = get_response(user_id, survey_version, question.variable_name)
		if response is not None:
			if question.variable_name == "friends_name":
				response = pseudonyms_to_facebook_names(response)
			question.set_answer(response)
	else:
		response = get_response(user_id, survey_version, question.variable_name)
		if response != None:
			question.set_answer(response)
	return question

def get_user_progress(user_id, survey_version):
	# check how many answers already given
	entries = Response.objects.filter(user = user_id, form_version=survey_version)
	variables = get_ordered_variable_names(survey_version)
	max_index = 0;
	#pdb.set_trace()
	for entry in entries:
		varname = ''
		#if entry.variable_name.endswith('[]'):
		#	varname = entry.variable_name[:-2]
		#else:
		varname = entry.variable_name
		try:
			curr_index = variables.index(varname)
			if curr_index > max_index:
				max_index = curr_index
		except ValueError:
			print "ERROR: " + entry.variable_name + " is in the DB but not in the survey!";
	
	answered = len(entries);
	
	#check how many questions in total
	total = get_survey_length(survey_version);
	#print "answered " + str(answered) + '/' + str(total);
	#print "at " + str(max_index) + '/' + str(len(variables));
	#return answered*100/total;
	return float(max_index)*100/len(variables)

def get_survey_length(survey_version):
	#TODO change to checking in the DB instead
	#return len(open(settings.ROOT_DIR + 'render/data/sample_new.txt').readlines());
	resp = 0;
	previous = ''
	s = Survey.objects.get(form_version = survey_version)
	content = json.loads(s.content)
	for question in content:
		try:
			if len(question['data']) > 0: resp += len(question['data'])
			else: resp +=1
		except Exception: resp +=1 #headers don't have data
	return resp
	#for line in open(SURVEY_PATH):
	#	if line.startswith('header') | line.startswith('question'):
	#		resp +=1
	#	elif line.startswith('subquestion'):
	#		if previous.startswith('subquestion'):
	#			resp +=1
	#	previous = line
	#	
	#return resp
	
def get_ordered_variable_names(survey_version):
	resp = [];
	s = Survey.objects.get(form_version = survey_version)
	content = json.loads(s.content)
	for q in content:
		try:
			if len(q['data']) > 0:
				for sq in q['data']:
					resp.append(sq['variable_name'])
			else: resp.append(q['variable_name'])
		except Exception: resp.append(q['variable_name']) # headers don't have data
	#for line in open(SURVEY_PATH):
	#	if line.startswith('header') | line.startswith('question') | line.startswith('subquestion'):
	#		resp.append(line.split('\t')[fw.VARIABLE_LABEL].strip())
	#	
	return resp	

'''
def set_current_question(user_id, survey_version, variable_name):
	entries = Progress.objects.filter(user=user_id,\
                   form_version=survey_version);
	if len(entries) > 0:
		entries[0].question_variable_name = variable_name;
		entries[0].save();
	else:
		e = Progress(user_id=user_id,\
                     form_version=survey_version, question_variable_name = variable_name);
		e.save();
	

def get_current_question(user_id, survey_version):
	entries = Progress.objects.filter(user=user_id,\
                 form_version=survey_version);
	questions = get_questions_list();
	if len(entries) > 0:
		for question in questions:
			if question.variable_name == entries[0].question_variable_name:
				return question
	else:
		return questions[0]
'''


def process_facebook_names_response(response):
	names = response.split("\r\n")
	names = [name for name in names if len(name) > 0]
	facebook_names_to_pseudonyms = {}
	try:
		facebook_names_to_pseudonyms = json.loads(open(settings.ROOT_DIR + settings.FACEBOOK_NAMES_FILE).read())
	except Exception, e:
		print "Error accessing facebook names file: " + str(e)

	friends_pseudonyms = []
	for name in names:
		pseudonym = facebook_names_to_pseudonyms.get(name)
		if not pseudonym:
			pseudonym = simplecrypt.encrypt(settings.FACEBOOK_NAMES_ENCRYPTION_PASSWORD, name).encode("hex")
		friends_pseudonyms.append(pseudonym)
	return ";".join(friends_pseudonyms)


def set_answer(user_id, survey_version, variable_name, response, human_readable_question, human_readable_response):
	#saving the question index
	#entries = Progress.objects.filter(user_id = user_id, form_version=survey_version, question_index=question_index);
	#if len(entries) > 0:
	#	entries[0].question_index = question_index;
	#	entries[0].save()
	#else:
	#	r = Progress(user_id = user_id, form_version=survey_version, question_index=question_index);
	#	r.save();

	#saving the actual answer
	print user_id
	entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if variable_name == 'friends_name':
		response = process_facebook_names_response(response)
	if len(entries) > 0:
		entries[0].response = response
		entries[0].human_readable_response = human_readable_response
		entries[0].save()
	else:
		r = Response(user = user_id, form_version=survey_version, \
				variable_name = variable_name, response=response,\
				human_readable_question = human_readable_question,\
				human_readable_response = human_readable_response);
		r.save()

def get_response(user_id, survey_version, variable_name):
	entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if len(entries) > 0:
		return entries[0].response;
	else:
		return None
		
def needs_answer(user_id, survey_version, question):
	#pdb.set_trace()
	question = get_conditioned_question(user_id, survey_version, question)
	if question != None:
		if isinstance(question, fw.GridQuestion):
			entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name__in = question.get_subquestion_variables())
			responses = [x.variable_name for x in entries]
			if len(intersect(question.get_subquestion_variables(), responses)) < len(question.get_subquestion_variables()):
				return True
			else:
				return False  
		else:
			entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name = question.variable_name)
			if len(entries) == 0:
				return True
			else:
				return False
	else:
		return False
		
def intersect(a, b):
     return list(set(a) & set(b))

def get_conditioned_question(user_id, survey_version, question):
	if check_condition(user_id, survey_version, question.inclusion_condition):
		if isinstance(question, fw.GridQuestion):
			for ii in range(len(question.data)-1, -1, -1):
				sub = question.data[ii]
				if not check_condition(user_id, survey_version, sub.inclusion_condition):
					question.data.remove(sub)
			if len(question.data) > 0:
				return question
			else:
				return None
		else:
			return question
	else:
		return None

def check_condition(user_id, survey_version, mcondition):
	#pdb.set_trace()
	
	if (mcondition == None) | (mcondition == ''):
		return True;
	#pdb.set_trace()
	equal = False;
	parts = mcondition.split('==')
	if len(parts) > 1: # condition equal
		equal = True;
	else:
		parts = mcondition.split('!=')
		
	for i, part in enumerate(parts):
		parts[i] = part.strip();
	
	parts[1] = parts[1].split("|")
	
	# left hand side is the var name, right hand side is the value
	answer = get_response(user_id, survey_version, parts[0])
	for part in parts[1]:
		if answer == fw.htmlize(part):
			return equal

	return not equal;

# to be implemented correctly
def get_survey_version(user):
	submit_responses = Response.objects.filter(user=user, variable_name='_submitted')
	response_dates = {}
	for response in submit_responses:
		response_dates[response.form_version] = response.last_answered
	if SURVEYS[0] not in response_dates.keys(): return SURVEYS[0]
	return None

	# if they already answered the second questionnaire, return none
#	return SURVEYS[3]
#	if SURVEYS[1] in response_dates.keys(): return None
	# if they answered none, return the first one
#	if SURVEYS[0] not in response_dates.keys(): return SURVEYS[0]
	# if they answered first one, but not the second one, check if they did it before October 25th
#	if response_dates[SURVEYS[0]] < timezone.make_aware(datetime.datetime(2013, 10, 25), timezone.get_default_timezone()):
#		return SURVEYS[1]
	# add handling the date of giving the questionnaire to other users


	return None
#	try:
#		a = Response.objects.get(user=user, variable_name='_submitted', form_version='90920167766cb9d5d5767b692b9d3acb')
#		# if answered before November 1st, return new questionniare
#		answered = a.last_answered;
#		if answered.year < 2014 and answered.month < 12:
#			return 'c6107a28c3651190fc77b36785e49a43'
#		else:
#			# TODO add comparison to todays date - if it's after second deployment date, serve the new one
#			return None
#		#return 'f3a9ec5005dd1fb3ccbc9432ad8a731f' 
#		return None
#	except Response.DoesNotExist:
#		return '90920167766cb9d5d5767b692b9d3acb'
	

def get_questions_list(survey_version):
	try:
		s = Survey.objects.get(form_version = survey_version)
		return fw.parse_json(s.content)
	except Survey.DoesNotExist:
		return []
	
				

