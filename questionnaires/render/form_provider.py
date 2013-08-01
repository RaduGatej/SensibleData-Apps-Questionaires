import formwidget as fw
from render.models import Response
from django.conf import settings
import pdb

SURVEY_PATH = settings.SURVEY_DIR + settings.SURVEY_FILE

_DEBUG = False
def DEBUG():
	if _DEBUG:
		pdb.set_trace()

def get_first_question(user_id, survey_version):
	questions = get_questions_list();
	return return_question(user_id, survey_version, questions[0]);

def get_previous_question(user_id, survey_version, current_name):
	#pdb.set_trace()
	questions = get_questions_list();
	if current_name == '__goodbye':
		for i in range(1,len(questions)):
			if check_condition(user_id, survey_version, questions[-i].inclusion_condition):
				return return_question(user_id, survey_version, questions[-i])
	previous = None;
	for q in questions:
		if q.variable_name == current_name:
			if previous == None:
				return return_question(user_id, survey_version, questions[0])
			else:
				return return_question(user_id, survey_version, previous);
		else:
			if check_condition(user_id, survey_version, q.inclusion_condition):
				previous = q
	raise NameError(current_name + ' is not a valid question name');

def get_next_question(user_id, survey_version, current_name):
	
	questions = get_questions_list();
	now_is_the_time = False;
	for question in questions:	
		if now_is_the_time:
			#pdb.set_trace()
			if check_condition(user_id, survey_version, question.inclusion_condition):
				return return_question(user_id, survey_version, question)
			else:
				pass
		elif question.variable_name == current_name:
			#pdb.set_trace()
			# it is a grid question it might still be unanswered, verify
			if isinstance(question, fw.GridQuestion):
				#pdb.set_trace();
				entries = Response.objects.filter(user=user_id,\
						form_version=survey_version,\
						variable_name__in = question.get_subquestion_variables());
				if len(entries) != len(question.get_subquestion_variables()):
					return return_question(user_id, survey_version, question)
			now_is_the_time = True
		else:
			pass
	if now_is_the_time:
		return None;
	else:
		raise NameError(current_name + ' is not a valid question name');
			

def get_next_unanswered_question(user_id,survey_version):
	questions = get_questions_list();
	#pdb.set_trace()
	entries = Response.objects.filter(user=user_id,\
				form_version=survey_version);
	if len(entries) > 0:
		answers = {};
		for e in entries:
			answers[e.variable_name] = e.response;
		for question in questions:
			if check_condition(user_id, survey_version, question.inclusion_condition):
				if isinstance(question, fw.GridQuestion):
					for sub in question.get_subquestion_variables():
						if sub not in answers.keys():
							return return_question(user_id, survey_version, question)
				elif question.variable_name not in answers.keys():
					# if q.inclusion_condition != '':
					return return_question(user_id, survey_version, question)
	else:
		return return_question(user_id, survey_version, questions[0]);


def return_question(user_id, survey_version, question):
	#set_current_question(user_id, survey_version, question.variable_name)
	DEBUG();
	if isinstance(question, fw.GridQuestion):
		for sub in question.data:
			var_name = sub.variable_name;
			response = get_response(user_id, survey_version, var_name)
			if response != None:
				sub.set_answer(response)	
	elif isinstance(question, fw.Header):
		pass
	else:
		response = get_response(user_id, survey_version, question.variable_name)
		if response != None:
			question.set_answer(response)
	return question

def get_user_progress(user_id, survey_version):
	# check how many answers already given
	entries = Response.objects.filter(user = user_id, form_version=survey_version);
	variables = get_ordered_variable_names(survey_version)
	max_index = 0;
	#pdb.set_trace()
	for entry in entries:
		varname = ''
		if entry.variable_name.endswith('[]'):
			varname = entry.variable_name[:-2]
		else:
			varnname = entry.variable_name
		try:
			curr_index = variables.index(entry.variable_name)
			if curr_index > max_index:
				max_index = curr_index
		except ValueError:
			print "ERROR: " + entry.variable_name + " is in the DB but not in the survey!";
	
	answered = len(entries);
	
	#check how many questions in total
	total = get_survey_length(survey_version);
	#print "answered " + str(answered) + '/' + str(total);
	print "at " + str(max_index) + '/' + str(len(variables));
	#return answered*100/total;
	return float(max_index)*100/len(variables)

def get_survey_length(survey_version):
	#TODO change to checking in the DB instead
	#return len(open(settings.ROOT_DIR + 'render/data/sample_new.txt').readlines());
	resp = 0;
	previous = ''
	for line in open(SURVEY_PATH):
		if line.startswith('header') | line.startswith('question'):
			resp +=1
		elif line.startswith('subquestion'):
			if previous.startswith('subquestion'):
				resp +=1
		previous = line
		
	return resp
	
def get_ordered_variable_names(survey_version):
	resp = [];
	for line in open(SURVEY_PATH):
		if line.startswith('header') | line.startswith('question') | line.startswith('subquestion'):
			resp.append(line.split('\t')[fw.VARIABLE_LABEL].strip())
		
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

def set_answer(user_id, survey_version, variable_name, response):
	#saving the question index
	#entries = Progress.objects.filter(user_id = user_id, form_version=survey_version, question_index=question_index);
	#if len(entries) > 0:
	#	entries[0].question_index = question_index;
	#	entries[0].save()
	#else:
	#	r = Progress(user_id = user_id, form_version=survey_version, question_index=question_index);
	#	r.save();
	

	#saving the actual answer
	entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if len(entries) > 0:
		entries[0].response = response;
		entries[0].save();
	else:
		r = Response(user = user_id, form_version=survey_version, \
				variable_name = variable_name, response=response);
		r.save();

def get_response(user_id, survey_version, variable_name):
	entries = Response.objects.filter(user = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if len(entries) > 0:
		return entries[0].response;
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

def get_questions_list():
	return fw.parsefile(SURVEY_PATH)
	
				

