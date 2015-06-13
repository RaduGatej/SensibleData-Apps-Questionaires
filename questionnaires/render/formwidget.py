import re
from django.conf import settings
import pdb
import csv
import json
import xlrd
from utils import htmlize, escape
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
REQUIRED = 10;

NUMBER_OF_COLUMNS = 11;


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

def xls_to_csv(infile, outfile):
	wb = xlrd.open_workbook(infile)
	sheet = wb.sheet_by_index(0)
	
	csv_output = open(outfile,'wb')
		
	wr = csv.writer(csv_output, quoting=csv.QUOTE_MINIMAL)
	for r in xrange(sheet.nrows):
		wr.writerow([unicode(entry).encode('utf-8') for entry in sheet.row_values(r)])
	
	csv_output.close()
	return outfile

def parse_csv(filename):
	widgets = []
	idx = 0
	line_idx = 0
	with open(filename, 'rb') as mycsv:
		reader = csv.reader(mycsv, delimiter = ',')
		for row in reader:
			line_idx +=1
			print line_idx
			if row[0] == 'Type': continue # skipping header line
			elif row[0] == '': continue # skipping empty line
			widget = parserow(row)
			if widget is None:
				print ' ^^^^^^^^^^^^^^^^^^^^^^ Error in line: ' + str(line_idx)
				continue
			idx +=1
			if isinstance(widget, SubQuestion) | isinstance(widget, NumberSubquestion) | isinstance(widget, RadioSubquestion) | isinstance(widget, TextSubquestion):
				widgets[-1].add_subquestion(widget)
			else:
				widgets.append(widget)
	return widgets

def parse_xls(infile):
	outfile = infile + '.csv'
	return parse_csv(xls_to_csv(infile, outfile))

def parse_json(jsonstring):
	widgets = []
	obj = json.loads(jsonstring)
	for w in obj:
		widgets.append(makewidget_fromdict(w))
	return widgets
	
# reads a file and returns a list of widgets
def parse_file(infile):
	if infile.endswith('.xls'):
		return parse_xls(infile)
	elif infile.endswith('.csv'):
		return parse_csv(infile)

def parse_txt(filename):
	#print filename
	widgets = [];
	idx = 0;
	line_idx = 0;
	for line in open(filename):
		line_idx +=1;
		#print line_idx;
		line = line.replace('"','')
		if line.startswith('Type'):
			#header line, create Survey with meta data
			#survey = Survey(version=survey_version,location=path,\
			#	question_count = 0, extra=survey_extra)
			#survey.save();
			continue
		elif line.strip() == '':
			#print 'skipping empty line'
			continue
		#print line
		
		widget = parseline(line);
		if widget is None:
		#	print ' ^^^^^^^^^^^^^^^^^^^^^^ Error in line: ' + str(line_idx)
			continue
		idx +=1;
		#pdb.set_trace()
		if isinstance(widget, SubQuestion) | isinstance(widget, NumberSubquestion) | isinstance(widget, RadioSubquestion) | isinstance(widget, TextSubquestion):
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
	#for w in widgets:
	#	print w.to_dict()
	return widgets

def makewidget_fromdict(mdict):
	if mdict['type'] == 'header':
		return Header.fromdict(mdict)
	elif mdict['type'] == 'question':
		return makequestion_fromdict(mdict)
	elif mdict['type'] == 'subquestion':
		if mdict['answer_type'] == 'radio':
			return SubQuestion.fromdict(mdict)
		elif mdict['answer_type'] == 'time':
			return TimeSubquestion.fromdict(mdict)
		elif mdict['answer_type'] == 'multi_radio':
			return RadioSubquestion.fromdict(mdict)
		elif mdict['answer_type'] == 'number':
			return NumberSubquestion.fromdict(mdict)
		elif mdict['answer_type'] == 'string':
			return TextSubquestion.fromdict(mdict)
	else:
		return None	
				
def parserow(row):
	parts = validate_row(row)
	if parts == None:
		return None;
	
	if parts[ELEMENT_TYPE] == 'header':
		return Header(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], \
			parts[ADDITIONAL_CONTENT], parts[INCLUSION_CONDITION], parts[VARIABLE_LABEL])
	elif parts[ELEMENT_TYPE] == 'question':
		return makequestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], \
							parts[ADDITIONAL_CONTENT], \
							parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
							parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM], parts[REQUIRED])
	elif parts[ELEMENT_TYPE] == 'subquestion':
		if parts[ANSWER_TYPE] == 'radio':
			return SubQuestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
		elif parts[ANSWER_TYPE] == 'multi_radio':
			return RadioSubquestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
		elif parts[ANSWER_TYPE] == 'time':
			return TimeSubquestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
		elif parts[ANSWER_TYPE] == 'number':
			return NumberSubquestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
		elif parts[ANSWER_TYPE] == 'string':
			return TextSubquestion(parts[PRIMARY_CONTENT], parts[SECONDARY_CONTENT], 
							parts[ADDITIONAL_CONTENT], \
                            parts[INCLUSION_CONDITION], parts[ANSWER_TYPE], \
                            parts[VARIABLE_LABEL], parts[ANSWERS], parts[EXTRA_PARAM])
	else:
		#raise Exception('',parts[ELEMENT_TYPE] + ' is not a valid element type!');
		return None

def validate_row(parts):
	#pdb.set_trace()
	#print (parts)
	if len(parts) < NUMBER_OF_COLUMNS:
		parts += ['' for e in xrange(NUMBER_OF_COLUMNS-len(parts))]
	
	error = False;
	
	if parts[ELEMENT_TYPE] not in ['header','question','subquestion']:
		print 'ERROR: ' + parts[ELEMENT_TYPE] + ' is not a valid element type!';
		error = True;
	if parts[ELEMENT_TYPE] in ['question','subquestion']:
		if parts[ANSWER_TYPE] not in ['radio','number','time','checklist','grid','string','multi_text','multi_radio','multi_number','scale','textarea', 'autocomplete_item_list', 'number;radio','time']:
			print 'ERROR: ' + parts[ANSWER_TYPE] + ' is not a valid answer type'
			error = True;	
		if parts[ANSWER_TYPE] not in ['multi_number', 'multi_text','string','textarea', 'autocomplete_item_list']:
			if parts[ANSWERS] == '':
				if (parts[ANSWER_TYPE] != 'multi_radio') or (parts[ELEMENT_TYPE] != 'question'):
					print 'ERROR: missing list of answers'
					error = True;
	if parts[ANSWER_TYPE] != 'grid':
		if parts[VARIABLE_LABEL] == '':
			print 'ERROR: variable label is missing';
			error = True
		elif parts[VARIABLE_NAME] == '':
		#	print 'WARNING: variable name is missing, making it the same as label';
			parts[VARIABLE_NAME] = parts[VARIABLE_LABEL]
	if parts[REQUIRED] == '0.0': 
		parts[REQUIRED] = False
	else: 
		parts[REQUIRED] = True
		
	
	if error:
		return None
	else:
		return parts
		
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
		if parts[ANSWER_TYPE] not in ['radio','number','time','checklist','grid','multi_text','string',\
										'multi_radio','multi_number','scale','textarea', 'number;radio']:
			print 'ERROR: ' + parts[ANSWER_TYPE] + ' is not a valid answer type'
			error = True;
		if parts[ANSWER_TYPE] not in ['multi_number', 'textarea']:
			if parts[ANSWERS] == '':
				print 'ERROR: missing list of answers'
				error = True;
	if parts[ANSWER_TYPE] != 'grid':
		if parts[VARIABLE_LABEL] == '':
			print 'ERROR: variable label is missing';
			error = True
		elif parts[VARIABLE_NAME] == '':
		#	print 'WARNING: variable name is missing, making it the same as label';
			parts[VARIABLE_NAME] = parts[VARIABLE_LABEL]
		
	
	if error:
		return None
	else:
		return parts
	
def makequestion(primary_content, secondary_content, additional_content,\
				inclusion_condition, answer_type, variable_name, answers, extra_param, required=True):
	#print 'Inclusion condition: ' + inclusion_condition
	if answer_type == 'radio':
		return RadioQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'number':
		return NumberQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'dropdown':
		return ListQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'scale':
		return ScaleQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'number;radio':
		return NumberCheckQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'textarea':
		return FreeTextQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'autocomplete_item_list':
		return AutocompleteItemsQuestion(primary_content, secondary_content, additional_content,\
		 		inclusion_condition, answer_type, variable_name, answers, extra_param, required)
	elif answer_type == 'multi_number':
		return MultiNumberQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'multi_text':
		return MultiTextQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'checklist':
		return ChecklistQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	elif answer_type == 'multi_radio':
		return MultiRadioQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);		
	elif answer_type == 'grid':
		return GridQuestion(primary_content, secondary_content, additional_content,\
                inclusion_condition, answer_type, variable_name, answers, extra_param, required);
	else:
		raise Exception('',answer_type + ' is not a valid answer type!');
		return None

def makequestion_fromdict(mdict):
	answer_type = mdict['answer_type']
	if answer_type == 'radio':
		return RadioQuestion.fromdict(mdict);
	elif answer_type == 'number':
		return NumberQuestion.fromdict(mdict);
	elif answer_type == 'dropdown':
		return ListQuestion.fromdict(mdict);
	elif answer_type == 'scale':
		return ScaleQuestion.fromdict(mdict);
	elif answer_type == 'number;radio':
		return NumberCheckQuestion.fromdict(mdict);
	elif answer_type == 'textarea':
		return FreeTextQuestion.fromdict(mdict);
	elif answer_type == 'autocomplete_item_list':
		return AutocompleteItemsQuestion.fromdict(mdict)
	elif answer_type == 'multi_number':
		return MultiNumberQuestion.fromdict(mdict);
	elif answer_type == 'multi_text':
		return MultiTextQuestion.fromdict(mdict);
	elif answer_type == 'multi_radio':
		return MultiRadioQuestion.fromdict(mdict);
	elif answer_type == 'checklist':
		return ChecklistQuestion.fromdict(mdict);
	elif answer_type == 'grid':
		return GridQuestion.fromdict(mdict);
	else:
		raise Exception('',answer_type + ' is not a valid answer type!');
		return None

    
#### Class definitions
class Formwidget(object):
	def __init__(self, primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param, required=True):
		self.primary_content = primary_content;
		self.secondary_content = secondary_content;
		self.additional_content = additional_content;
		self.inclusion_condition = inclusion_condition;
		self.answer_type = answer_type;
		self.answer = [];
		self.variable_name = variable_name;
		self.required = required
		answers = answers.split(";");
		self.answers = [];
		for answer in answers:
			ans = answer.strip();
			if ans != '':
				self.answers.append({"raw":ans,"htmlized":htmlize(ans)});
		self.extra_param = extra_param;
		self.data = [];

		self.dynamic_content = {k:'' for k in re.findall('%%[^%]+%%', primary_content + ' ' + secondary_content)}

	@classmethod
	def fromdict(cls, mdict):
		o = cls(mdict['primary_content'],mdict['secondary_content'],mdict['additional_content'],\
			mdict['inclusion_condition'],mdict['answer_type'],mdict['variable_name'],'',mdict['extra_param'],mdict['required'])
		o.answers = mdict['answers']
		for d in mdict['data']:
			o.data.append(makewidget_fromdict(d))
		return o

	def set_dynamic_content(self, content):
		self.dynamic_content = content

	def render(self):
		return "<p></p>";

	def to_html(self):
		#return '<div class="formwidget">\n' + self.render() + '\n</div>';
		resp = '<input type="hidden" name="__question_name" value="' + self.variable_name + '" />\n';
		resp += self.render()
		#pdb.set_trace()
		for k in self.dynamic_content:
			if self.dynamic_content[k]: resp = resp.replace(k, self.dynamic_content[k])
		try:
			for sub in self.data:
				for k in sub.dynamic_content:
					if sub.dynamic_content[k]: resp = resp.replace(k, sub.dynamic_content[k])
		except AttributeError: pass # header doesn't have data 
		return resp
	
	def to_dict(self):
		resp = {}
		resp['type'] = self.__class__.__name__.lower()
		resp['primary_content'] = self.primary_content
		resp['secondary_content'] = self.secondary_content
		resp['additional_content'] = self.additional_content
		resp['inclusion_condition'] = self.inclusion_condition
		resp['answer_type'] = self.answer_type
		resp['variable_name'] = self.variable_name
		resp['answers'] = []
		for answer in self.answers:
			resp['answers'].append(answer)
		resp['extra_param'] = self.extra_param
		resp['required'] = self.required
		resp['data'] = []
		for d in self.data:
			resp['data'].append(d.to_dict())
		return resp	
	
	def set_answer(self, answer):
		self.answer = answer;

		
class Question(Formwidget):
	def prerender(self):
		if len(self.primary_content) > 0:
			resp = '<h2>' + self.primary_content + '</h2>\n';
		else:
			resp = '';

		if len(self.secondary_content) > 0:
			resp += '<p style="width:80%"><strong>' + self.secondary_content + '</strong></p>\n';
		
		if len(self.additional_content) > 0:
			resp += '<div class="alert alert-info">' + self.additional_content + '</div>';

		return resp + self.list_required_vars();

	def to_dict(self):
		o = super(Question, self).to_dict()
		o['type'] = 'question'
		return o

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

		self.dynamic_content = {k:'' for k in re.findall('%%[^%]+%%', primary_content + ' ' + secondary_content)}

	@classmethod
	def fromdict(cls, mdict):
		return cls(mdict['primary_content'],mdict['secondary_content'],mdict['additional_content'],\
			mdict['inclusion_condition'],mdict['variable_name'])
	
	def to_dict(self):
		resp = {}
		resp['type'] = self.__class__.__name__.lower()
		resp['primary_content'] = self.primary_content
		resp['secondary_content'] = self.secondary_content
		resp['additional_content'] = self.additional_content
		resp['variable_name'] = self.variable_name
		resp['inclusion_condition'] = self.inclusion_condition
		return resp

	def render(self):
		resp = '<h2>' + self.primary_content + "</h2>\n"
		resp += '<div style="width:85%;text-align: justify; text-justify: newspaper">' + self.secondary_content + '</div>\n'
		
		#resp += '<input type="hidden" name="require_answer" value="no"/>\n'
		resp += '<input type="hidden" name="' + self.variable_name + '" value="1"/>\n'
		return resp 

class RadioQuestion(Question):
	def render(self):
		resp = self.prerender();
		for answer in self.answers:
			resp += '<label class="radio">\n';
			resp += '\t<input type="radio" name="' + self.variable_name + \
					'" value="' + answer['htmlized'] +'" '
			if self.answer != []:
				if self.answer == answer['htmlized']:
					resp += ' checked="checked" '
			resp += 'onclick="document.getElementById(\'next_button\').click();" '
			resp += '/>' + answer['raw'] + '\n'
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
	 		resp += '\t<option value="' + answer['htmlized'] + '" '
			if (self.answer != []):
				if self.answer == answer['htmlized']:
					resp += 'selected="selected"' 
			resp += '>' + answer['raw'] + '</option>\n'
		resp += '</select>\n';

		return resp
		
class ChecklistQuestion(Question):
	def __init__(self, primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param, required = True):
		super( ChecklistQuestion, self).__init__(primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param, required)
		if not self.variable_name.endswith('[]'):
			self.variable_name = self.variable_name + '[]'
		if len(self.extra_param) == 0: self.extra_param = '1'
	
	def render(self):
		resp = self.prerender();
		if self.answer != []:
			self.answer = self.answer.split(',');
		resp += '<input type="hidden" name="__required_answer_count" value="' + self.extra_param + '" />\n'
		for answer in self.answers:
			resp += '\t<label class="checkbox">\n'
			resp += '\t\t<input type="checkbox" name="' + self.variable_name + '" '
			resp += 'value="' + answer['htmlized'] + '" '
			if self.answer != []:
				if answer['htmlized'] in self.answer:
					resp += ' checked '
			resp +=' />'
			resp += answer['raw'] + '\n'
			resp += '\t</label>\n'
    		
		return resp
		
class NumberQuestion(Question):
	
	def prerender(self):
		if len(self.primary_content) > 0:
			resp = '<h2>' + self.primary_content + '</h2>\n';
		else:
			resp = '';
		resp += '<div class="row">'
		
		if len(self.secondary_content) > 0:
			resp += '<div class=span8">' + self.secondary_content + '</div>\n';
		
		if len(self.additional_content) > 0:
			resp += '<div class="alert alert-info">' + self.additional_content + '</div>';

		return resp + self.list_required_vars();
		
	def render(self):
		
		resp = self.prerender();

		if self.secondary_content != '':
			resp += '<div class="span4">'
		else:
			resp += '<div class="span12">'
		self.answers[0]['raw'] = re.sub('_+','_',self.answers[0]['raw'])
		parts = self.answers[0]['raw'].split('_');
		#pdb.set_trace()
		if len(parts) > 1: #there was the underscore, so we prepend/append
			for i, part in enumerate(parts):
				parts[i] = part.strip();
			resp += '<div class="'
			if parts[0] != '':
				resp +='input-prepend '
			if parts[1] != '':
				resp += 'input-append '
			
			resp +='">\n'
			if parts[0] != '':
				resp += '\t<span class="add-on '
				resp += '">' + parts[0] + '</span>'
			
		resp += '<input name="' + self.variable_name + '" '
		resp += 'class="input-small ';
		extra_parts = str(self.extra_param).split(';')
		try:
			if extra_parts[2].strip() == 'sum':
				resp += ' sum_to_100 '
		except: pass
		if self.extra_param == 'time':
			resp += 'time" ';
			resp += 'type="text" '
			resp += 'isTime="true" '
			resp += 'placeholder="TT:MM" '
			resp += 'onblur="timeFieldChanged(this,24)" '
		else:
			mmin = '0'
			mmax = '0'
			
			if len(extra_parts) > 1:
				mmin = extra_parts[0].strip()
				mmax = extra_parts[1].strip()
			else:
				mmax = extra_parts[0].strip()
				
			resp += '" '
			resp += 'type="number" '
			resp += 'min="' + mmin + '" '
			resp += 'max="' + mmax + '" ';
			resp += 'placeholder="' + mmin + '-' + mmax + '" '
		if (self.answer != []):
			resp += 'value="' + str(self.answer) + '" '


		try:
			if extra_parts[2].strip() == 'sum':
				resp += ' onkeyup="sumto100()" onchange="sumto100()" '
		except: pass			
		if len(parts) > 1:
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
			if parts[1] != '':
				resp += '\t<span class="add-on">' + parts[1] + '</span>'
			resp += '\n</div>'
			
		else:
			resp += ' />'
			
		resp += '</div></div>\n'
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
			resp += '<th style="text-align:center">'
			#if idx == 0:
			#	resp += 'right'
			#elif idx == (len(self.answers)-1):
			#	resp += 'left'
			#else:
			#	resp += 'center'
			resp += answer['raw'] + '</th>'
			
		resp += '\n\t</tr>'
		resp += '\t<tr>\n\t\t<td>' + self.secondary_content + '</td>'
		for idx, answer in enumerate(self.answers):
			resp += '<td style="text-align:center;width:5%">'
			#if idx == 0:
			#	resp += 'right'
			#elif idx == (len(self.answers)-1):
			#	resp += 'left'
			#else:
			#	resp += 'center'
			#resp += '">'
			resp += '<input type="radio" name="' + self.variable_name + '" value="' + answer['htmlized'] + '" '
			if self.answer == answer['htmlized']:
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


class AutocompleteItemsQuestion(Question):
	def get_data_source_link(self):
		return self.extra_param.split(";")[0], self.extra_param.split(";")[1]

	def set_autocomplete_items(self, autocomplete_items):
		self.autocomplete_items = autocomplete_items


	def render(self):
		resp = self.prerender()

		htmlized_items = "'[" + ",".join(['"' + item.replace("'", "") + '"' for item in self.autocomplete_items]) + "]'"
		resp += '<textarea id = "autocomplete" autocomplete="off" data-provide="typeahead" data-source=' + htmlized_items + ' name="' + self.variable_name + '" rows="4">'
		if self.answer != []:
			resp += self.answer
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
		resp += "function checkboxClicked() {var numberfield = document.getElementById('numberfield');var checkbox = document.getElementById('checkboxfield');if (checkbox.checked == true) {numberfield.value = ',';numberfield.disabled = true;} else {numberfield.value = '';numberfield.disabled = false;}}function numberEntered() {var element = document.getElementById('checkboxfield');element.checked=false;}"
		resp += '</script>\n'
		self.answers[0]['raw'] = re.sub('_+','_',self.answers[0]['raw'])
		parts = self.answers[0]['raw'].split('_');
		for i, part in enumerate(parts):
			parts[i] = part.strip();
			
		numeric_answer = False;
		#pdb.set_trace();
		if self.answer !=[]:
			if is_number(self.answer):
				numeric_answer = True;
		
		
		resp += parts[0] + ' ';		
		resp += '<input type="number" name="' + self.variable_name + '" '
		mmin = '0'
		mmax = '0'
		extra_parts = str(self.extra_param).split(';')
		if len(extra_parts) > 1:
			mmin = extra_parts[0].strip()
			mmax = extra_parts[1].strip()
		else:
			mmax = extra_parts[0].strip()
			
		resp += '" '
		resp += 'type="number" '
		resp += 'min="' + mmin + '" '
		resp += 'max="' + mmax + '" ';
		resp += 'placeholder="' + mmin + '-' + mmax + '" '

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
		resp += 'value="' + self.answers[1]['htmlized'] + '" '
		if (self.answer != []) & (numeric_answer==False):
			resp += 'checked '
		resp += 'id="checkboxfield" onclick="checkboxClicked();"/>\n'
		resp += self.answers[1]['raw']
		resp += '</label>'
		return resp

class SubQuestion(Formwidget):
	def to_dict(self):
		o = super(SubQuestion, self).to_dict()
		o['type'] = 'subquestion'
		return o

	def render(self):
		resp = ''
		answered = False;
		if self.answer_type == 'radio':
			for answer in self.answers:
				resp += '\t<td style="text-align:center;">'
				resp += '<input type="radio" name="' + self.variable_name + '" value="' + answer['htmlized'] + '"'
				if self.answer == answer['htmlized']:
					resp += ' checked="checked" '
					answered = True;
				resp += ' onclick="markRowSuccess(this)" '
				resp += '></td>\n'
			pre = '\n<tr id="' + self.variable_name + '"'
			if answered:
				pre += ' class="success"'
			pre += '>\n\t<td>' + self.secondary_content + '</td>\n'	
			resp = pre + resp;

		# elif self.answer_type == 'number' and self.extra_param == 'time':
		# 	resp += '<input type="hidden" name="__required_answer_count" value="' + str(len(self.answers)) + '" />'
		# 	for answer in self.answers:
		# 		resp += '\t<td style="text-align:center;">'
		# 		resp += '<input name="' + self.variable_name + '[]" '
		# 		resp += 'class="input-small time"';
		# 		resp += 'type="text" '
		# 		resp += 'isTime="true" '
		# 		resp += 'placeholder="TT:MM" '
		# 		if (self.answer != []):
		# 			resp += 'value="' + str(self.answer) + '" '
		# 		resp += '/></td>\n'
		# 	pre = '\n<tr><td>' + self.secondary_content + '</td>\n'
		# 	resp = pre + resp
		
		#elif self.answer_type == 'number':
		#	for answer in self.answers:
		#		resp += '\t<td><input type="number" name="' + self.variable_name + '_' + htmlize(answer) + '" max=' + str(self.extra_param) + ' min=0'
		#		if isinstance(self.answer,dict):
		#			if (self.variable_name + '_' + htmlize(answer)) in self.answer.keys():
		#				resp += ' value=' + str(self.answer[self.variable_name + '_' + htmlize(answer)])
		#		resp += ' placeholder="0-' + str(self.extra_param) + '" '
		#		resp += 'class="input-mini"'
		#		resp += '/></td>\n'

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

class TimeSubquestion(SubQuestion):
	def __init__(self, primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param, required=True):
		super( TimeSubquestion, self).__init__(primary_content, secondary_content, additional_content, \
				inclusion_condition, answer_type, variable_name, answers, extra_param, required)
		if not self.variable_name.endswith('[]'):
			self.variable_name = self.variable_name + '[]'

	def render(self):
		resp = '<input type="hidden" name="__required_answer_count" value="' + str(len(self.answers)) + '" />'
		responses = []

		if self.answer:
			responses = self.answer.split(',')
		if (len(responses) != len(self.answers)):
			responses = ['' for a in self.answers]
		for response, answer in zip(responses, self.answers):
			resp += '\t<td style="text-align:center;">'
			resp += '<input name="' + self.variable_name + '"'
			resp += 'class="input-small time"';
			resp += 'type="text" '
			resp += 'isTime="true" '
			resp += 'placeholder="T:MM" '
			resp += 'value="' + str(response) + '" '
			resp += 'onblur="timeFieldChanged(this,6)" '
			resp += '/></td>\n'
		pre = '\n<tr><td>' + self.secondary_content + '</td>\n'
		resp = pre + resp + '</tr>\n'
		return resp	
		
class GridQuestion(Question):

	def add_subquestion(self, subquestion):
		self.data.append(subquestion)

	def get_subquestion_variables(self):
		resp = [];
		for sub in self.data:
			resp.append(sub.variable_name)
		return resp

	def render(self):
		resp = self.prerender();
		resp += '\n<table class="table table-bordered table-hover">\n';
		resp += '<tr>\n\t<th></th>';
		for answer in self.answers:
			resp +='\n\t<th style="width:8%;vertical-align:bottom;text-align:center;">' + answer['raw'] + '</th>';
		resp += '\n</tr>\n'
		for sub in self.data:
			if sub.secondary_content.startswith('[SPLIT]'):
				resp += '\n</table>';
				resp += '<p style="width:80%"><strong>' + sub.secondary_content.replace('[SPLIT]','') + '</strong></p>\n';
				resp += '<input type="hidden" name="' + sub.variable_name + '" value="1"/>'
				resp += '\n<table class="table table-bordered table-hover">\n';
				resp += '<tr>\n\t<th></th>';
				for answer in self.answers:
					resp +='\n\t<th style="width:8%;vertical-align:bottom;text-align:center;">' + answer['raw'] + '</th>';
				resp += '\n</tr>\n'
			else:
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
		resp = '<div class="row" style="margin-left:0px">';
		if len(self.secondary_content) > 0:
			resp += '<div class="span8">' + self.secondary_content + '</div>';
		
		return resp

	def to_dict(self):
		o = super(NumberSubquestion, self).to_dict()
		o['type'] = 'subquestion'
		return o

class MultiNumberQuestion(GridQuestion):
	def render(self):
		resp = self.prerender()
		#resp += '<div class="row">\n'
		for sub in self.data:
			resp += sub.render() + '\n'
		
		#resp += '</div>\n'
			
		
		return resp

class TextSubquestion(SubQuestion):
	def prerender(self):
		return ''

	def render(self):
		#resp = '<div class="control-group">'
		#resp += '<label class="control-label" for="' + self.variable_name + '">' + self.secondary_content + '</label>'
		#resp += '<div class="controls">'
		resp =  '<div class="row">'
		resp += '<div class="span1" style="text-align:right;padding-right:10px">' + self.secondary_content + '</div>'
		resp += '<input type="text" style="input-big" name="' + self.variable_name + '"'
		if self.answer: 
			resp += 'value="' + escape(str(self.answer)) + '"'
		resp += '>'
		resp += '</div>'
		# resp = '<div class="span1" style="text-align:right">' + self.secondary_content + '</div>'
		# resp += '<input type="text" style="input-medium" name="' + self.variable_name + '" value="'
		# if self.answer: 
		# 	resp += escape(str(self.answer)) 
		# resp += '">'
		return resp


class MultiTextQuestion(GridQuestion):
	def render(self):
		resp = self.prerender()
		
		for sub in self.data:
			resp += sub.render() + '\n'
		return resp

	def list_required_vars(self):
		resp = '<input type="hidden" name="__required_vars" value="';
		resp_count = len(self.get_subquestion_variables())
		try: resp_count = int(float(self.extra_param))
		except: pass
		resp += ','.join(self.get_subquestion_variables()[0:resp_count]);
		resp +='" />\n';
		return resp


class RadioSubquestion(Question):
	def to_dict(self):
		o = super(Question, self).to_dict()
		o['type'] = 'subquestion'
		return o

	def prerender(self):
		if len(self.primary_content) > 0:
			resp = '<h2>' + self.primary_content + '</h2>\n';
		else:
			resp = '';
		resp += '<div class="row" id="' + self.variable_name + '">'
		
		if len(self.secondary_content) > 0:
			resp += '<label style="margin-left:30px">' + self.secondary_content + '</label>\n';
		
		if len(self.additional_content) > 0:
			resp += '<div class="alert alert-info">' + self.additional_content + '</div><br/>';
		return resp

	def render(self):
		resp = self.prerender();
		for idx, answer in enumerate(self.answers):
			resp += '<label style="margin-left:30px" class="radio">\n';
			resp += '\t<input type="radio" name="' + self.variable_name + \
					'" value="' + answer['htmlized'] +'" '
			if self.answer != []:
				if self.answer == answer['htmlized']:
					resp += ' checked="checked" '
			resp += ' onclick="markDivSuccess(this)" '
			resp += '/>' + answer['raw'] + '\n'
			resp += '</label>\n';
		return resp + '</div>'


class MultiRadioQuestion(GridQuestion):
	def render(self):
		resp = self.prerender()
		for sub in self.data:
			resp += sub.render() + '<br/>\n'
		return resp

