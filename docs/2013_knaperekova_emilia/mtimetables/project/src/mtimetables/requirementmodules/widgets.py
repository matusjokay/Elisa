# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets as django_widgets
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from bootstrap3.forms import render_field_and_label

from tools import widgets as tools_widgets

import logging
logger = logging.getLogger(__name__)



# class MyChoiceFieldRenderer(django_widgets.RadioFieldRenderer):

# 	def render(self):
# 		id_ = self.attrs.get('id', None)
# 		start_tag = format_html('<div id="{0}">', id_) if id_ else '<div>'
# 		output = [start_tag]
# 		for i, choice in enumerate(self.choices):
# 			choice_value, choice_label = choice
# 			self.attrs['class'] = ''
# 			if isinstance(choice_label, (tuple, list)):
# 				attrs_plus = self.attrs.copy()
# 				if id_:
# 					attrs_plus['id'] += '_{0}'.format(i)
# 				sub_ul_renderer = ChoiceFieldRenderer(name=self.name,
# 													  value=self.value,
# 													  attrs=attrs_plus,
# 													  choices=choice_label)
# 				sub_ul_renderer.choice_input_class = self.choice_input_class
# 				output.append(format_html('<div class="checkbox">{0}{1}</div>', choice_value, sub_ul_renderer.render()))
# 			else:
# 				w = self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, i)
# 				output.append(format_html('<div class="checkbox">{0}</div>', force_text(w)))
# 		output.append('</div>')
# 		return mark_safe('\n'.join(output))


# class BaseRadioSelect(django_widgets.RadioSelect):
	# renderer = MyChoiceFieldRenderer




class TableInput(tools_widgets.BaseMultiWidget):

	def __init__(self, widget, n_rows, n_cols, row_labels=[], col_labels=[], label="", offset=0, *args, **kwargs):
		self.n_rows = n_rows
		self.n_cols = n_cols
		self.row_labels = row_labels
		self.col_labels = col_labels
		self.label = label
		self.offset = offset
		w = [widget] * self.n_rows * self.n_cols
		super(TableInput, self).__init__(w, *args, **kwargs)
	

	def format_output(self, rendered_widgets):
		table = """
		<table class="table table-bordered table-calendar">
			<thead>%s</thead>
			<tbody>%s</tbody>
		</table>
		"""
		table_head = '<th>&nbsp;</th>' if len(self.row_labels)>0 and len(self.col_labels)>0 else "" 
		table_head += "".join(['<th>%s</th>' % i for i in self.col_labels]) if len(self.col_labels)>0 else ""
		table_rows = ''

		for i in range(self.n_rows):
			row_cols = str('<th>%s</th>' % self.row_labels[i]) if len(self.row_labels)>0 else ""
			for j in range(self.n_cols):
				row_cols += '<td>%s</td>' % rendered_widgets[i * self.n_cols + j]
			table_rows += '<tr>%s</tr>' % row_cols

		table = table % (table_head, table_rows)

		return render_field_and_label(table, self.label, layout=self.layout)