import re
from django.conf import settings
import pdb

#indices of columns in the Excel file
ELEMENT_TYPE = 0;
PRIMARY_CONTENT = 1;
SECONDARY_CONTENT = 2;
ADDITIONAL_CONTENT = 3;
INCLUSION_CONDITION = 4;
ANSWER_TYPE = 5;
VARIABLE_NAME = 6;
VARIABLE_LABEL = 7;
ANSWERS = 8;
EXTRA_PARAM = 9;

NUMBER_OF_COLUMNS = 10;


#### Utility methods
def debug(widgets):
	f = open('dummy.html','w')
	f.write('<html><body><form>')
	for w in widgets:
		f.write(w.to_html() + '\n')
	f.write('</form></body></html>')
	f.close()
	
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def parsefile(filename):
	print filename
	widgets = [];
	idx = 0;
	line_idx = 0;
	for line in open(filename):
		line_idx +=1;
		print line_idx;
		line = line.replace('"','')
		if line.startswith('Type'):
			#header line, create Survey with meta data
			#survey = Survey(version=survey_version,location=path,\
			#	question_count = 0, extra=survey_extra)
			#survey.save();
			continue
		elif line.strip() == '':
			print 'skipping empty line'
			continue
		#print line
		
		widget = parseline(line);
		if widget is None:
			print ' ^^^^^^^^^^^^^^^^^^^^^^ Error in line: ' + str(line_idx)
			continue
		idx +=1;
		if isinstance(widget, SubQuestion) | isinstance(widget, NumberSubquestion):
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
	parts = validate(string)
	if parts == None:
		return None;
	
	if parts[ELEMENT_TYPE] == 'header':
		return Header(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], \
			parts[ADDITIONAL_CONTENT], parts[INCLUSION_CONDITION], parts[VARIABLE_LABEL])
	elif parts[ELEMENT_TYPE] == 'question':
		return makequestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], \
							parts[ADDITIONAL_CONTENT], \
							parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
							parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
	elif parts[ELEMENT_TYPE] == 'subquestion':
		if parts[ANSWER_TYPE] == 'radio':
			return SubQuestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
		elif parts[ANSWER_TYPE] == 'number':
			return NumberSubquestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
	else:
		#raise Exception('',parts[ELEMENT_TYPE] + ' is not a valid element type!');
		return None
		
def validate(string):
	parts = string.strip().split('\t');
	#pdb.set_trace()
	#print (parts)
	if len(parts) < NUMBER_OF_COLUMNS:
		parts += ['' for e in xrange(NUMBER_OF_COLUMNS-len(parts))]
	
	error = False;
	
	if parts[ELEMENT_TYPE] not in ['header','question','subquestion']:
		print 'ERROR: ' + parts[ELEMENT_TYPE] + ' is not a valid element type!';
		error = True;
	if parts[ELEMENT_TYPE] in ['question','subquestion']:
		if parts[ANSWER_TYPE] not in ['radio','number','checklist','grid','multi_number','scale','textarea', 'number;radio']:
			print 'ERROR: ' + parts[ANSWER_TYPE] + ' is not a valid answer type'
			error = True;
		if parts[ANSWER_TYPE] not in ['multi_number', 'textarea']:
			if parts[ANSWERS] == '':
				print 'ERROR: missing list of answers'
				error = True;
	if parts[ANSWER_TYPE] != 'grid':
		if parts[VARIABLE_NAME] == '':
			print 'ERROR: variable name is missing';
			error = True
		if parts[VARIABLE_LABEL] == '':
			print 'ERROR: variable label is missing';
			error = True
	
	if error:
		return None
	else:
		return parts
	
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
	elif answer_type == 'scale':
		return ScaleQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'number;radio':
		return NumberCheckQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'textarea':
		return FreeTextQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'multi_number':
		return MultiNumberQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'checklist':
		return ChecklistQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	elif answer_type == 'grid':
		return GridQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param);
	else:
		raise Exception('',answer_type + ' is not a valid answer type!');
		return None

def htmlize(string):
    return re.sub('[^a-z_0-9]','',string.strip().lower().replace(' ','_'));
    
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
			resp = '<h2>' + self.primary_content + '</h2>\n';
		else:
			resp = '';

		if len(self.secondary_content) > 0:
			resp += '<legend>' + self.secondary_content + '</legend>\n';
		
		if len(self.additional_content) > 0:
			resp += '<div class="alert alert-info">' + self.additional_content + '</div>';

		return resp + self.list_required_vars();

	def list_required_vars(self):
		resp = '<input type="hidden" name="__required_vars" value="' + self.variable_name + '" />\n'
		return resp;


class Header(Formwidget):
	def __init__(self, primary_content, secondary_content, additional_content, \
		inclusion_condition, variable_name):
		self.primary_content = primary_content;
		self.secondary_content = secondary_content;
		self.additional_content = additional_content;
		self.variable_name = variable_name;
		self.inclusion_condition = inclusion_condition;

	def render(self):
		resp = '<h2>' + self.primary_content + "<h2>\n"
		resp += '<legend>' + self.secondary_content + '</legend>\n'
		
		#resp += '<input type="hidden" name="require_answer" value="no"/>\n'
		resp += '<input type="hidden" name="' + self.variable_name + '" value="1"/>\n'
		return resp 

class RadioQuestion(Question):
	def render(self):
		resp = self.prerender();
		for answer in self.answers:
			resp += '<label class="radio">\n';
			resp += '\t<input type="radio" name="' + self.variable_name + \
					'" value="' + htmlize(answer) +'" '
			if self.answer != []:
				if self.answer == htmlize(answer):
					resp += ' checked="checked" '
			resp += 'onclick="document.getElementById(\'next_button\').click();" '
			resp += '/>' + answer + '\n'
			resp += '</label>\n';
		return resp;

class ListQuestion(Question):
	def render(self):
		resp = self.prerender() 
		resp += '\n<select name="' + self.variable_name + '" ' 
		resp += 'onchange="document.getElementById(\'next_button\').click();"' 
		resp += '>\n';
		# add empty answer as default
		resp += '\t<option value=""></option>\n';
		for answer in self.answers:
	 		resp += '\t<option value="' + htmlize(answer) + '" '
			if (self.answer != []):
				if self.answer == htmlize(answer):
					resp += 'selected="selected"' 
			resp += '>' + answer + '</option>\n'
		resp += '</select>\n';

		return resp
		
class ChecklistQuestion(Question):
	def render(self):
		resp = self.prerender();
		if self.answer != []:
			self.answer = self.answer.split(',');
		resp += '<input type="hidden" name="__required_answer_count" value="' + self.extra_param + '" />\n'
		for answer in self.answers:
			resp += '\t<label class="checkbox">\n'
			resp += '\t\t<input type="checkbox" name="' + self.variable_name + '[]" '
			resp += 'value="' + htmlize(answer) + '" '
			if self.answer != []:
				if htmlize(answer) in self.answer:
					resp += ' checked '
			resp +=' />'
			resp += answer + '\n'
			resp += '\t</label>\n'
    		
		return resp
		
class NumberQuestion(Question):
	def render(self):
		resp = self.prerender();
		self.answers = re.sub('_+','_',self.answers[0])
		parts = self.answers.split('_');
		if len(parts) > 0: #there was the underscore, so we prepend/append
			for i, part in enumerate(parts):
				parts[i] = part.strip();
			resp += '<div class="'
			if parts[0] != '':
				resp +='input-prepend '
			if parts[1] != '':
				resp += 'input append'
			resp +='">\n'
			if parts[0] != '':
				resp += '\t<span class="add-on">' + parts[0] + '</span>'
			resp += '<input type="number" name="' + htmlize(self.variable_name) + '"'
			resp += 'min=0 '
			#pdb.set_trace()
			if self.extra_param == 'time':
				resp += 'max="24" step="0.01" '
			else:
				resp += 'max="' + str(self.extra_param) + '" ';
			if (self.answer != []):
				resp += 'value=' + str(self.answer) + ' '
			else:
				if self.extra_param == 'time':
					resp+='placeholder="HH.MM" '
				else:
					resp += 'placeholder="0-' + str(self.extra_param) + '" '
			resp += 'class="input-mini span2" ';
			resp += 'id="'
			if parts[0] != '':
				if parts[1] != '':
					resp += 'appendedPrepended'
				else:
					resp += 'prepended'
			else:
				if parts[1] != '':
					resp += 'appended'

			resp +='Input"'
			resp += ' />'
		else: # there was no underscore, so we keep the simple number field
			resp += '<input type="number" name="' + htmlize(self.variable_name) + '"'
			resp += 'min=0 max=' + str(self.extra_param) + ' ';
			if (self.answer != []):
				resp += 'value=' + str(self.answer) + ' '
			else:
				resp += 'placeholder="0-' + str(self.extra_param) + '" />'
				
		return resp
		
#similar to grid question, but with different styling. There is a table with two rows and the number of columns
#equal to the number of answers +1. The only border in the table is the horizontal line between the notes
#and radio buttons.
class ScaleQuestion(Question):
	def prerender(self):
		resp = '';
		if len(self.primary_content) > 0:
			resp = '<h2>' + self.primary_content + '</h2>\n';

		if len(self.additional_content) > 0:
			resp += '<div class="alert alert-info">' + self.additional_content + '</div>';
			
		return resp + self.list_required_vars();
		
	def render(self):
		resp = self.prerender();
		resp += '<table class="table table-condensed">\n'
		resp += '\t<tr>\n\t\t<td></td>'
		for idx, answer in enumerate(self.answers):
			resp += '<td style="text-align:'
			if idx == 0:
				resp += 'right'
			elif idx == (len(self.answers)-1):
				resp += 'left'
			else:
				resp += 'center'
			resp += '">' + answer + '</td>'
			
		resp += '\n\t</tr>'
		resp += '\t<tr>\n\t\t<td>' + self.secondary_content + '</td>'
		for idx, answer in enumerate(self.answers):
			resp += '<td style="text-align:'
			if idx == 0:
				resp += 'right'
			elif idx == (len(self.answers)-1):
				resp += 'left'
			else:
				resp += 'center'
			resp += '">'
			resp += '<input type="radio" name="' + self.variable_name + '" value="' + answer + '" '
			if self.answer == answer:
				resp += ' checked '
			resp += 'onclick="document.getElementById(\'next_button\').click();" '
			resp += '/></td>'
			
		resp += '\n\t</tr>\n</table>\n'
		
		return resp

class FreeTextQuestion(Question):
	def render(self):
		resp = self.prerender();	
		resp += '<textarea name="' + self.variable_name + '" rows="4">' 
		if self.answer != []:
			resp += str(self.answer)
		else:
			resp += ' '
		resp += '</textarea>\n'
		return resp

# lets the user insert a number of tick a box that they don't want to insert the number
class NumberCheckQuestion(Question):
	def render(self):
		#pdb.set_trace()
		resp = self.prerender()
		resp += '<script type="text/javascript"> '
		resp += "function checkboxClicked() {var numberfield = document.getElementById('numberfield');var checkbox = document.getElementById('checkboxfield');if (checkbox.checked == true) {numberfield.value = 'fake';numberfield.disabled = true;} else {numberfield.value = '';numberfield.disabled = false;}}function numberEntered() {var element = document.getElementById('checkboxfield');element.checked=false;}"
		resp += '</script>\n'
		self.answers[0] = re.sub('_+','_',self.answers[0])
		parts = self.answers[0].split('_');
		for i, part in enumerate(parts):
			parts[i] = part.strip();
			
		numeric_answer = False;
		#pdb.set_trace();
		if self.answer !=[]:
			if is_number(self.answer):
				numeric_answer = True;
		
		
		resp += parts[0] + ' ';		
		resp += '<input type="number" name="' + self.variable_name + '" '
		resp += 'min="0" max="' + self.extra_param + '" '
		resp += 'id="numberfield" onchange="numberEntered();" onkeypress="this.onchange();" onpaste="this.onchange();" oninput="this.onchange();" '
		if self.answer != []:
			if numeric_answer:
				resp += 'value="' + str(self.answer) + '" '
			else:
				resp += 'disabled="true" '
		resp += '/>\n'
		if len(parts) > 1:
			resp += parts[1]
		resp += '<label class="checkbox">\n'
		resp += '<input type="checkbox" name="' + self.variable_name + '" '  
		resp += 'value="' + htmlize(self.answers[1]) + '" '
		if (self.answer != []) & (numeric_answer==False):
			resp += 'checked '
		resp += 'id="checkboxfield" onclick="checkboxClicked();"/>\n'
		resp += self.answers[1]
		resp += '</label>'
		return resp

class SubQuestion(Formwidget):
	def render(self):
		resp = '\n<tr>\n\t<td>' + self.secondary_content + '</td>\n'
		if self.answer_type == 'radio':
			for answer in self.answers:
				resp += '\t<td><input type="radio" name="' + htmlize(self.variable_name) + '" value="' + htmlize(answer) + '"'
				if self.answer == htmlize(answer):
					resp += ' checked="checked" '
				resp += '></td>\n'
		
		elif self.answer_type == 'number':
			for answer in self.answers:
				resp += '\t<td><input type="number" name="' + self.variable_name + '_' + htmlize(answer) + '" max=' + str(self.extra_param) + ' min=0'
				if isinstance(self.answer,dict):
					if (self.variable_name + '_' + htmlize(answer)) in self.answer.keys():
						resp += ' value=' + str(self.answer[self.variable_name + '_' + htmlize(answer)])
				resp += ' placeholder="0-' + str(self.extra_param) + '" '
				resp += 'class="input-mini"'
				resp += '/></td>\n'

		resp += '</tr>';
		return resp;

	#def get_variable_names(self):
	#	if self.answer_type == 'radio':
	#		return [self.variable_name]
	#	elif self.answer_type == 'number':
	#		resp = [];
	#		for answer in self.answers:
	#			resp.append(self.variable_name + '_' + htmlize(answer));
	#		return resp

		
		
class GridQuestion(Question):

	def add_subquestion(self, subquestion):
		self.data.append(subquestion)

	def get_subquestion_variables(self):
		resp = [];
		for sub in self.data:
			#if sub.answer_type == 'radio':
			resp.append(sub.variable_name)
			#elif sub.answer_type == 'number':
			#	for answer in sub.answers:
			#		resp.append(sub.variable_name + '_' + htmlize(answer));
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
		
class NumberSubquestion(NumberQuestion):
	def prerender(self):
		resp = '';
		if len(self.secondary_content) > 0:
			resp = self.secondary_content + ' ';
		return resp

class MultiNumberQuestion(GridQuestion):
	def render(self):
		resp = self.prerender()
		for sub in self.data:
			resp += '<div class="form-inline">' + sub.render() + '</div><br />\n'
		
		return resp
