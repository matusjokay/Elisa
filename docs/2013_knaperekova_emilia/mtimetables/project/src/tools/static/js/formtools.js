(function($) {


	$.formTools_ModalForm = function(options) {
		return new ModalForm(options);
	}

	$.fn.formTools_modalForm = function(options) {
		$(this).each(function() {
			f = new ModalForm($(this), options);
		});
		return this;
	};
	$.fn.formTools_modalForm.defaults = {
		url: false,
		modal: '#modal',
		form_target: '#modal .modal-content',
		data_init_callback: function() {},
		success_callback: function() {},
		show_callback: function() {},
		hide_callback: function() {},
		destroy_on_hide: false,
	};

	$.formTools_AjaxForm = function(form, options) {
		return new AjaxForm(form, options);
	};

	$.fn.formTools_ajaxForm = function(options) {
		$(this).each(function() {
			f = new AjaxForm($(this), options);
		});
		return this;
	};
	$.fn.formTools_ajaxForm.defaults = {
		messages_target: '#messages',
		extra_data: {},
		init_callback: function() {},
		success_callback: function() {},
		unsuccess_callback: function() {},
	};

	$.fn.formTools_initFields = function() {
		// setSelect($(this));
		// console.log('called init fields on', this);
		setDatePicker(this);
		setTimePicker(this);
		setColorPicker(this);
		return this;
	};




	function ModalForm(options) {

		var instance = this;
		// this.form = form;

		this.settings = $.extend({}, $.fn.formTools_modalForm.defaults, options);
		
		// "constructor" function called at the end of this "class"
		this.init = function() {
			instance.form = false;
		};

		this.resetForm = function() {
			$('input', $(instance.form)).not('[type="hidden"], [type="checkbox"], [type="radio"]').val('');
			$('select, textarea', $(instance.form)).val('');
			$('.colorpicker', $(instance.form)).css('background-color', 'inherit');
			$('input[type="checkbox"], input[type="radio"]', $(instance.form)).prop('checked', false);
		};

		this.load = function() {
			$(instance.settings.form_target).load(instance.settings.url, function(responseText, textStatus, XMLHttpRequest) {
				if (textStatus == 'success') {
					console.info('form successfully loaded from ' + instance.settings.url);
					instance.form = $('form', $(instance.settings.form_target));
					$(instance.form).trigger('form_loaded');
					instance.settings.data_init_callback.call(this);
					$(instance.form).formTools_ajaxForm({
						success_callback: function(responseText, statusText, xhr, form) {
							instance.settings.success_callback(responseText, statusText, xhr, form);
							instance.hide();
						}
					});
				} else {
					console.error('form could not be loaded from ' + instance.settings.url);
				}
			});
		};

		this.show = function() {
			$(instance.settings.modal).modal('show');
			if (instance.form == false && instance.settings.url) {
				$(instance.settings.form_target).html('<div class="ajax-loader"></div>');
				instance.load();
			} else if (instance.settings.data_init_callback) {
				instance.settings.data_init_callback();
			}
		};

		this.hide = function() {
			$(instance.settings.modal).modal('hide');
		};

		this.toggle = function() {
			$(instance.settings.modal).modal('toggle');
		};

		this.destroy = function() {
			instance.form = false;
			$(instance.settings.form_target).empty();
		};

		$(instance.settings.modal).on('shown.bs.modal', function(e) {
			instance.settings.show_callback.call(this);
		});

		$(instance.settings.modal).on('hide.bs.modal', function(e) {
			instance.settings.hide_callback.call(this);
			if (instance.settings.destroy_on_hide)
				instance.destroy();
		});


		this.init();
	}


	function AjaxForm(form, options) {

		var instance = this;
		this.settings = $.extend({}, $.fn.formTools_ajaxForm.defaults, options);

		this.init = function() {

			if (typeof(form) == 'object') {
				instance.form = form;
				instance.settings.init_callback.call(this);
				instance.ajaxForm();
			} else {
				instance.load(form);
			}

		};


		this.load = function(url) {
			form_target = $('<div/>').css('display', 'none');
			$('body').append(form_target);
			$(form_target).load(url, function(responseText, textStatus, XMLHttpRequest) {
				if (textStatus == 'success') {
					console.info('form successfully loaded from ' + url);
					instance.form = $('form', $(form_target));
					$(instance.form).trigger('form_loaded');
					instance.settings.init_callback.call(this);
					instance.ajaxForm();
				} else {
					console.error('form could not be loaded from ' + url);
				}
			});
		};

		this.ajaxForm = function() {
			instance.form.ajaxForm({
				success: function(responseText, statusText, xhr, form) {
					$(instance.settings.messages_target).append(responseText.msg);
					if (statusText == 'success') {
						instance.settings.success_callback(responseText, statusText, xhr, form);
						$(form).resetForm();
						$('.colorpicker', $(instance.form)).css('background-color', 'inherit');
					} else {
						instance.settings.unsuccess_callback.call(this);
					}
				},
				data: instance.settings.extra_data,
				dataType: 'json',
				resetForm: false,
			});
		};

		// this.resetForm = function() {
		// 	$('input', $(instance.form)).not('[type="hidden"], [type="checkbox"], [type="radio"]').val('');
		// 	$('select, textarea', $(instance.form)).val('');
		// 	$('.colorpicker', $(instance.form)).css('background-color', 'inherit');
		// 	$('input[type="checkbox"], input[type="radio"]', $(instance.form)).prop('checked', false);
		// }

		this.reset = function() {
			$(instance.form).resetForm();
		};

		this.submit = function() {
			$(instance.form).submit();
		};

		instance.init();
	}


	function setSelect(scope) {

		$('select', $(scope)).attr('data-live-search', 'true');

		var select_defaults = {
			dropupAuto: false,
		};

		$('select', $(scope)).selectpicker(select_defaults);

	}


	function setDatePicker(scope) {

		var datepicker_defaults = {
			dateFormat: "yy-mm-dd",
			changeMonth: false,
			numberOfMonths: 1,
			firstDay: 1,
		};

		$('.datepicker.datepicker-from', $(scope)).datepicker($.extend({}, {
			onClose: function(selectedDate) {
				$('.datepicker.datepicker-to', $(scope)).datepicker('option', 'minDate', selectedDate);
			}
		}, datepicker_defaults));

		$('.datepicker.datepicker-to', $(scope)).datepicker($.extend({}, {
			onClose: function(selectedDate) {
				$('.datepicker.datepicker-from', $(scope)).datepicker('option', 'maxDate', selectedDate);
			}
		}, datepicker_defaults));

		$('.datepicker', $(scope)).not('.datepicker-to').not('.datepicker-from').datepicker(datepicker_defaults);

	}


	function setTimePicker(scope) {

		var time_separator = ":"
		var timepicker_defaults = {
			timeSeparator: time_separator,
			amPmText: ['', ''],
			defaultTime: '',
			// showNowButton: true,
			// showCloseButton: true,
			// showDeselectButton: true,
		};

		$('.timepicker.timepicker-from', $(scope)).timepicker($.extend({}, {
			onClose: function(selectedTime) {
				time_array = selectedTime.split(time_separator);
				min_time = {hour: time_array[0], minute: time_array[1]};
				$('.timepicker.timepicker-to', $(scope)).timepicker('option', 'minTime', min_time);
			}
		}, timepicker_defaults));

		$('.timepicker.timepicker-to', $(scope)).timepicker($.extend({}, {
			onClose: function(selectedTime) {
				time_array = selectedTime.split(time_separator);
				max_time = {hour: time_array[0], minute: time_array[1]};
				$('.timepicker.timepicker-from', $(scope)).timepicker('option', 'maxTime', max_time);
			}
		}, timepicker_defaults));

		$('.timepicker', $(scope)).not('.timepicker-to').not('.timepicker-from').timepicker(timepicker_defaults);

	}


	function setColorPicker(scope) {

		var colorpicker_defaults = {
			colorFormat: '#HEX',
			hsv: false,
			okOnEnter: true,
			title: 'Color',
			altField: $('.colorpicker'),
			altProperties: 'background-color',
			parts:  ['header', 'map', 'bar',
				'swatches', 'footer'
			],
		};
		
		$('.colorpicker', $(scope)).colorpicker(colorpicker_defaults);

	}

}(jQuery));