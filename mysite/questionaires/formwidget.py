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
		answers = answers.split(";");
		self.answers = [];
		for answer in answers:
			self.answers.append(answer.strip());
		self.extra_param = extra_param;
		self.data = [];
	def render(self):
		return "<p></p>";

	def to_html(self):
		return '<div class="formwidget">\n' + self.render() + '\n</div>';

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
		for answer in self.answers:
			resp += '<input type="radio" name="' + self.variable_name + \
					'" value="' + htmlize(answer) + '"/>' + answer + '<br />\n'
		return resp;

class ListQuestion(Question):
	def render(self):
		resp = self.prerender() + '\n<select>\n';
		for answer in self.answers:
	 		resp += '\t<option value="' + htmlize(answer) + '">' + answer + '</option>\n'
		resp += '<select>\n';
		
class NumberQuestion(Formwidget):
	def render(self):
		resp = self.prerender() + '\n<input type="number" name="' + htmlize(self.variable_name) + '" />'

class SubQuestion(Formwidget):
	def render(self):
		resp = '\n<tr>\n\t<td>' + self.secondary_content + '</td>\n'
		if self.answer_type == 'radio':
			for answer in self.answers:
				resp += '\t<td><input type="radio" name="' + htmlize(self.variable_name) + '" value="' + htmlize(answer) + '"></td>\n'
		
		elif self.answer_type == 'number':
			for answer in self.answers:
				resp += '\t<td><input type="number" name="' + self.variable_name + '_' + htmlize(answer) + '" /></td>\n'

		resp += '</tr>';
		return resp;
		
		
class GridQuestion(Question):

	def add_subquestion(self, subquestion):
		self.data.append(subquestion)


	def render(self):
		resp = self.prerender() + '\n<table>\n';
		resp += '<tr>\n\t<th></th>';
		for answer in self.answers:
			resp +='\n\t<th>' + answer + '</th>';
		resp += '\n</tr>\n'
		for sub in self.data:
			resp += sub.render();

		resp += '\n</table>';

		return resp
		
