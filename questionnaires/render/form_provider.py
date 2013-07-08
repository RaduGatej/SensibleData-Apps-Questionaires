import formwidget as fw
from render.models import Response


def get_previous_question(current_name):
	questions = get_questions_list();
	previous = None;
	for q in questions:
		if q.variable_name == current_name:
			# TODO add support for conditional inclusion
			return previous;
		else:
			previous = q;
	raise NameError(current_name + ' is not a valid question name');

def get_next_question(current_name):
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

	raise NameError(current_name + ' is not a valid question name');
			

def get_next_unanswered_question(user_id,survey_version):
	questions = get_questions_list();
	entries = Response.objects.filter(user_id=user_id,\
				form_version=survey_version);
	if len(entries) > 0:
		answers = {};
		for e in entries:
			answers[e.variable_name] = e.response;
	
		for q in questions:
			if q.variable_name not in answers.keys():
				# TODO add support for conditional inclusion
				# if q.inclusion_condition != '':
				return q
	else:
		return questions[0];

def set_answer(user_id, survey_version, variable_name, response):
	entries = Response.objects.filter(user_id = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if len(entries) > 0:
		entries[0].response = response;
		entries[0].save();
	else:
		r = Response(user_id = user_id, form_version=survey_version, \
				variable_name = variable_name, response=response);
		r.save();

def get_response(user_id, survey_version, variable_name):
	entries = Response.objects.filter(user_id = user_id, form_version=survey_version, \
                variable_name = variable_name)
	if len(entries) > 0:
		return entries[0].response;
	else:
		return None


def get_questions_list():
	# TODO change it to something that makes more sense, please
	return fw.parsefile('/Users/piotr/SensibleData-Apps-Questionaires/questionnaires/render/data/sample_new.txt')
	
				

