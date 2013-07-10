import formwidget as fw
from render.models import Response
from django.conf import settings

def get_first_question(user_id, survey_version):
	questions = get_questions_list();
	return return_question(user_id, survey_version, questions[0]);

def get_previous_question(user_id, survey_version, current_name):
	questions = get_questions_list();
	if current_name == '__goodbye':
		return return_question(user_id, survey_version, questions[-1])
	previous = None;
	for q in questions:
		if q.variable_name == current_name:
			# TODO add support for conditional inclusion
			if previous == None:
				return return_question(user_id, survey_version, questions[0])
			else:
				return return_question(user_id, survey_version, previous);
		else:
			previous = q;
	raise NameError(current_name + ' is not a valid question name');

def get_next_question(user_id, survey_version, current_name):
	questions = get_questions_list();
	now_is_the_time = False;
	for q in questions:	
		if now_is_the_time:
			# TODO add support for conditional inclusion
			return q
		elif q.variable_name == current_name:
			now_is_the_time = True
		else:
			pass
	if now_is_the_time:
		# TODO change to return last page
		return None;
	else:
		raise NameError(current_name + ' is not a valid question name');
			

def get_next_unanswered_question(user_id,survey_version):
<<<<<<< HEAD
	#pdb.set_trace();
=======
>>>>>>> 0d3dcd11d846cb81e8f6109db6107331ce03fa25
	questions = get_questions_list();
	entries = Response.objects.filter(user=user_id,\
				form_version=survey_version);
	if len(entries) > 0:
		answers = {};
		for e in entries:
			answers[e.variable_name] = e.response;
<<<<<<< HEAD
		#pdb.set_trace();	
=======
>>>>>>> 0d3dcd11d846cb81e8f6109db6107331ce03fa25
		for question in questions:
			if isinstance(question, fw.GridQuestion):
				for sub in question.get_subquestion_variables():
					if sub not in answers.keys():
						return return_question(user_id, survey_version, question)
			elif question.variable_name not in answers.keys():
				# TODO add support for conditional inclusion
				# if q.inclusion_condition != '':
				return return_question(user_id, survey_version, question)
	else:
		return return_question(user_id, survey_version, questions[0]);


def return_question(user_id, survey_version, question):
	#set_current_question(user_id, survey_version, question.variable_name)
	return question

def set_current_question(user_id, survey_version, variable_name):
<<<<<<< HEAD
	#pdb.set_trace();
=======
>>>>>>> 0d3dcd11d846cb81e8f6109db6107331ce03fa25
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
<<<<<<< HEAD
	#pdb.set_trace();
=======
>>>>>>> 0d3dcd11d846cb81e8f6109db6107331ce03fa25
	entries = Progress.objects.filter(user=user_id,\
                 form_version=survey_version);
	questions = get_questions_list();
	if len(entries) > 0:
		for question in questions:
			if question.variable_name == entries[0].question_variable_name:
				return question
	else:
		return questions[0]
	

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


def get_questions_list():
	return fw.parsefile(settings.ROOT_DIR+'render/data/sample_new.txt')
	
				

