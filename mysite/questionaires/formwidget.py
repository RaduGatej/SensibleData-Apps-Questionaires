import re

class Formwidget:
	def __init__(self, mtype, primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param):
		self.mtype = mtype;
		self.primary_content = primary_content;
		self.secondary_content = secondary_content;
		self.additional_content = additional_content;
		self.inclusion_condition = inclusion_condition;
		self.answer_type = answer_type;
		self.variable_name = variable_name;
		self.answers = answers;
		self.extra_param = extra_param;

	def render(self):
		return "<p></p>";

def htmlize(string):
	return re.sub('[^a-z_]','',string.strip().lower().replace(' ','_'));
		
class Question(Formwidget):
	def prerender(self):
		if len(self.primary_content) > 0:
			resp = '<div class="question_title">' + self.primary_content + '</div>\n';
		else:
			resp = '';

		if len(self.secondary_content) > 0:
			resp += '<div class="question_content">' + self.secondary_content + '</div>\n';

		return resp;


class Header(Formwidget):
	def render(self):
		return '<div class="formheader">' + self.primary_content + "</div>\n"

class RadioQuestion(Question):
	def render(self):
		resp = self.prerender();
		answers_parts = self.answers.split(";");
		for answer in answers_parts:
			resp += '<input type="radio" name="' + self.variable_name + \
					'" value="' + htmlize(answer) + '"/>' + answer.strip() + '<br />\n'
		return resp;

class ListQuestion(Question):
	def render(self):
		resp = self.prerender() + '\n<select>\n';
		answers_parts = self.answers.split(";");
		for answer in answers_parts:
	 		resp += '\t<option value="' + htmlize(answer) + '">' + answer.strip() + '</option>\n'
		resp += '<select>\n';
		
class NumberQuestion(Formwidget):
	def render(self):
		resp = self.prerender() + '\n<input type="number" name="' + htmlize(self.variable_name) + '" />'
