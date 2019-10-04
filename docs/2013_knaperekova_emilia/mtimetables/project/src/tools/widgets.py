# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django import forms as django_forms
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bootstrap3.forms import render_field_and_label, render_field

import logging
logger = logging.getLogger(__name__)



DEFAULT_LAYOUT = 'horizontal'
DEFAULT_DELIMITER = ","



class BaseMultiWidget(widgets.MultiWidget):

	def __init__(self, widgets, attrs=None, labels=[], delimiter=DEFAULT_DELIMITER, layout=DEFAULT_LAYOUT):
		self.labels = labels
		self.delimiter = delimiter
		self.layout = layout
		super(BaseMultiWidget, self).__init__(widgets, attrs)
	
	def decompress(self, value):
		if not value:
			return []
		if isinstance(value, list):
			return value
		return value.split(self.delimiter)

	def value_from_datadict(self, data, files, name):
		values = super(BaseMultiWidget, self).value_from_datadict(data, files, name)
		return ",".join(values)

	def format_output(self, rendered_widgets):
		output = ''
		for i, widget in enumerate(rendered_widgets):
			label = self.labels[i] if len(self.labels) > i and self.labels[i] and self.layout != 'inline' else ''
			output += '<div class="form-group">%s</div>' % render_field_and_label(widget, label, layout=self.layout)
		return output
		# return ''.join(rendered_widgets)

	def render(self, name, value, attrs=None):
		if self.is_localized:
			for widget in self.widgets:
				widget.is_localized = self.is_localized
		# value is a list of values, each corresponding to a widget
		# in self.widgets.
		if not isinstance(value, list):
			value = self.decompress(value)
		output = []
		final_attrs = self.build_attrs(attrs)
		id_ = final_attrs.get('id', None)
		for i, widget in enumerate(self.widgets):
			try:
				widget_value = value[i]
			except IndexError:
				widget_value = None
			if id_:
				final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))

			list_to_class = None
			form_control_class = 'form-control'
			if isinstance(widget, widgets.RadioSelect):
				form_control_class = ''
				list_to_class = 'radio'
				final_attrs['class'] = ''
			elif isinstance(widget, widgets.CheckboxSelectMultiple):
				form_control_class = ''
				list_to_class = 'checkbox'
				final_attrs['class'] = ''

			if form_control_class:
				final_attrs['class'] = form_control_class
				final_attrs['placeholder'] = self.labels[i] if len(self.labels) > i else ''

			rendered_widget = widget.render(name + '_%s' % i, widget_value, final_attrs)
			if list_to_class:
				mapping = [
					('<ul', '<div'),
					('</ul>', '</div>'),
					('<li', '<div class="%s"' % list_to_class),
					('</li>', '</div>'),
				]
				for k, v in mapping:
					rendered_widget = rendered_widget.replace(k, v)

			# rendered_widget = '<div class="form-group">%s</div>' % rendered_widget

			output.append(rendered_widget)
		return mark_safe(self.format_output(output))



class DatePicker(django_forms.DateInput):
	range_type = None

	def render(self, name, value, attrs=None):
		if value is None:
			value = ''
		final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
		if value != '':
			final_attrs['value'] = force_text(self._format_value(value))
		datepicker_class = 'datepicker%s' % (' datepicker-%s' % self.range_type if self.range_type else '')
		if 'class' in  final_attrs.keys():
			final_attrs['class'] += ' %s' % datepicker_class
		else:
			final_attrs['class'] = datepicker_class
		final_attrs['placeholder'] = 'YYYY-MM-DD'
		return format_html('<div class="input-group"><span class="glyphicon glyphicon-calendar input-group-addon"></span><input{0} /></div>', flatatt(final_attrs))



class DatePickerFrom(DatePicker):
	range_type = 'from'



class DatePickerTo(DatePicker):
	range_type = 'to'



class TimePicker(django_forms.TimeInput):
	range_type = None

	def render(self, name, value, attrs=None):
		if value is None:
			value = ''
		final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
		if value != '':
			final_attrs['value'] = force_text(self._format_value(value))
		timepicker_class = 'timepicker%s' % (' timepicker-%s' % self.range_type if self.range_type else '')
		if 'class' in  final_attrs.keys():
			final_attrs['class'] += ' %s' % timepicker_class
		else:
			final_attrs['class'] = timepicker_class
		final_attrs['placeholder'] = 'HH:MM'
		return format_html('<div class="input-group"><span class="glyphicon glyphicon-time input-group-addon"></span><input{0} /></div>', flatatt(final_attrs))



class TimePickerFrom(TimePicker):
	range_type = 'from'



class TimePickerTo(TimePicker):
	range_type = 'to'



class ColorPicker(django_forms.TimeInput):

	def render(self, name, value, attrs=None):
		if value is None:
			value = ''
		final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
		if value != '':
			final_attrs['value'] = force_text(self._format_value(value))
		colorpicker_class = 'colorpicker'
		if 'class' in  final_attrs.keys():
			final_attrs['class'] += ' %s' % colorpicker_class
		else:
			final_attrs['class'] = colorpicker_class
		final_attrs['placeholder'] = ''
		return format_html('<div class="input-group"><span class="glyphicon glyphicon-adjust input-group-addon"></span><input{0} /></div>', flatatt(final_attrs))



class DatetimeWidget(BaseMultiWidget):

	def __init__(self, label='', widgets=None, attrs=None, *args, **kwargs):
		self.label = label
		if not widgets:
			widgets = [DatePicker(), TimePicker()]
		super(DatetimeWidget, self).__init__(widgets, attrs, *args, **kwargs)
		
	def decompress(self, value):
		if not value:
			return []
		if isinstance(value, datetime.datetime):
			return [value.date(), value.time()]
		return value

	def value_from_datadict(self, data, files, name):
		values = super(BaseMultiWidget, self).value_from_datadict(data, files, name)
		dt = datetime.datetime.strptime(" ".join(values), "%Y-%m-%d %H:%M")
		return dt

	def format_output(self, rendered_widgets):
		output = '<div class="row">'
		output += '<div class="col-md-6">%s</div>' % rendered_widgets[0]
		output += '<div class="col-md-6">%s</div>' % rendered_widgets[1]
		output += '</div>'
		return '<div class="form-group">%s</div>' % render_field_and_label(output, self.label, layout='inline')



class DatetimeWidgetFrom(DatetimeWidget):

	def __init__(self, label='', widgets=None, attrs=None, *args, **kwargs):
		widgets = [DatePickerFrom(), TimePickerFrom()]
		super(DatetimeWidgetFrom, self).__init__(label, widgets, attrs, *args, **kwargs)



class DatetimeWidgetTo(DatetimeWidget):

	def __init__(self, label='', widgets=None, attrs=None, *args, **kwargs):
		widgets = [DatePickerTo(), TimePickerTo()]
		super(DatetimeWidgetTo, self).__init__(label, widgets, attrs, *args, **kwargs)



class BitmaskWidget(widgets.CheckboxSelectMultiple):

	def value_from_datadict(self, data, files, name):
		values = super(BitmaskWidget, self).value_from_datadict(data, files, name)
		result = 0
		for value in values:
			result = result | int(value)
		return result

	def render(self, name, value, attrs=None, choices=()):
		if not value:
			result = []
		else:
			choices_keys = [i[0] for i in self.choices]
			result = [key for key in choices_keys if value & key] if value not in choices_keys else [value, ]
		return super(BitmaskWidget, self).render(name, result, attrs, choices)



class LinkWidget(django_forms.Widget):

	def __init__(self, url, name, attrs=None):
		self.url = url
		self.name = name
		super(LinkWidget, self).__init__(attrs)

	def render(self, name, value, attrs=None):
		return '<a class="btn btn-link" href="%s">%s</a>' % (self.url, self.name)