import re



#### Utility methods
def debug(widgets):
	f = open('dummy.html','w')
	f.write('<html><body><form>')
	for w in widgets:
		f.write(w.to_html() + '\n')
	f.write('</form></body></html>')
	f.close()

def parsefile(filename):
	widgets = [];
	idx = 0;
	for line in open(filename):
		if idx == 0:
			idx +=1
			continue
		print line

		widget = parseline(line);
		if widget is None:
			print 'Error in line: ' + str(idx)
			return
		idx +=1;
		if isinstance(widget, SubQuestion):
			widgets[-1].add_subquestion(widget)
		else:
			widgets.append(widget);
	if idx == 1:
		# excel did not append new lines at the end
		f = open(filename + '.tmp','w')
		for line in open(filename):
			f.write(line.replace('\r','\r\n'))
		f.close();
		widgets = parsefile(filename + '.tmp')
	return widgets
				



def parseline(string):
	parts = string.strip().split('\t');
	print (parts)
	if len(parts) < 9:
		parts += ['' for e in xrange(9-len(parts))]
	if parts[0] == 'header':
		return Header(parts[1])
	elif parts[0] == 'question':
		return makequestion(parts[1], parts[2], parts[3], \
							parts[4], parts[5], parts[6], parts[7], parts[8])
	elif parts[0] == 'subquestion':
		return SubQuestion(parts[1], parts[2], parts[3], \
                            parts[4], parts[5], parts[6], parts[7], parts[8])
	else:
		return None
		

def makequestion(primary_content, secondary_content, additional_content,\
				inclusion_condition, answer_type, variable_name, answers, extra_param):
	if answer_type == 'radio':
		return RadioQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'number':
		return NumberQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'dropdown':
		return ListQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'grid':
		return GridQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	else:
		return None

def htmlize(string):
    return re.sub('[^a-z_]','',string.strip().lower().replace(' ','_'));
#### Class definitions
class Formwidget:
	def __init__(self, primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param):
		self.primary_content = primary_content;
		self.secondary_content = secondary_content;
		self.additional_content = additional_content;
		self.inclusion_condition = inclusion_condition;
		self.answer_type = answer_type;
		self.answer = [];
		self.variable_name = variable_name;
		answers = answers.split(";");
		self.answers = [];
		for answer in answers:
			ans = answer.strip();
			if ans != '':
				self.answers.append(answer.strip());
		self.extra_param = extra_param;
		self.data = [];
	def render(self):
		return "<p></p>";

	def to_html(self):
		#return '<div class="formwidget">\n' + self.render() + '\n</div>';
		resp = '<input type="hidden" name="__question_name" value="' + self.variable_name + '" />\n';
		return resp + self.render();

	def set_answer(self, answer):
		self.answer = answer;

		
class Question(Formwidget):
	def prerender(self):
		if len(self.primary_content) > 0:
			resp = '<legend>' + self.primary_content + '</legend>\n';
		else:
			resp = '';

		if len(self.secondary_content) > 0:
			resp += '<label>' + self.secondary_content + '</label>\n';

		return resp + self.list_required_vars();

	def list_required_vars(self):
		resp = '<input type="hidden" name="__required_vars" value="' + self.variable_name + '" />\n'
		return resp;


class Header(Formwidget):
	def __init__(self, primary_content, secondary_content):
		self.primary_content = primary_content;
		self.secondary_content = secondary_content;

	def render(self):
		resp = '<legend>' + self.primary_content + "<legend>\n"
		resp += '<label>' + self.secondary_content + '</label>\n'
		#resp += '<input type="hidden" name="require_answer" value="no"/>\n'
		resp += '<input type="hidden" name="' + self.variable_name + '" value="1"/>\n'
		return resp 

class RadioQuestion(Question):
	def render(self):
		resp = self.prerender();
		for answer in self.answers:
			resp += '<label class="radio">\n';
			resp += '\t<input type="radio" name="' + self.variable_name + \
					'" value="' + htmlize(answer) + '"/>' + answer + '\n'
			resp += '</label>\n';
		return resp;

class ListQuestion(Question):
	def render(self):
		resp = self.prerender() + '\n<select name="' + self.variable_name + '">\n';
		# add empty answer as default
		resp += '\t<option value=""></option>\n';
		for answer in self.answers:
	 		resp += '\t<option value="' + htmlize(answer) + '">' + answer + '</option>\n'
		resp += '<select>\n';

		return resp
		
class NumberQuestion(Question):
	def render(self):
		resp = self.prerender() + '<input type="number" name="' + htmlize(self.variable_name) + '"'
		resp += 'min=0 max=' + str(self.extra_param);
		if (self.answer != []):
			resp += 'value=' + self.answer + ' '
		else:
			resp += 'placeholder="0-' + str(self.extra_param) + '" '
		resp += 'class="input-mini" ';
		resp += ' />'
		return resp

class SubQuestion(Formwidget):
	def render(self):
		resp = '\n<tr>\n\t<td>' + self.secondary_content + '</td>\n'
		if self.answer_type == 'radio':
			for answer in self.answers:
				resp += '\t<td><input type="radio" name="' + htmlize(self.variable_name) + '" value="' + htmlize(answer) + '"></td>\n'
		
		elif self.answer_type == 'number':
			for answer in self.answers:
				resp += '\t<td><input type="number" name="' + self.variable_name + '_' + htmlize(answer) + '" max=' + str(self.extra_param) + ' min=0'
				resp += ' placeholder="0-' + str(self.extra_param) + '" '
				resp += 'class="input-mini"'
				resp += '/></td>\n'

		resp += '</tr>';
		return resp;

		
		
class GridQuestion(Question):

	def add_subquestion(self, subquestion):
		self.data.append(subquestion)

	def get_subquestion_variables(self):
		resp = [];
		for sub in self.data:
			if sub.answer_type == 'radio':
				resp.append(sub.variable_name)
			elif sub.answer_type == 'number':
				for answer in sub.answers:
					resp.append(sub.variable_name + '_' + htmlize(answer));
		return resp

	def render(self):
		resp = self.prerender();
		resp += '\n<table class="table table-bordered table-hover">\n';
		resp += '<tr>\n\t<th></th>';
		for answer in self.answers:
			resp +='\n\t<th>' + answer + '</th>';
		resp += '\n</tr>\n'
		for sub in self.data:
			resp += sub.render();

		resp += '\n</table>';

		return resp
	
	def list_required_vars(self):
		resp = '<input type="hidden" name="__required_vars" value="';
		resp += ','.join(self.get_subquestion_variables());
		resp +='" />\n';
		return resp

