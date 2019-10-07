(function($) {

	function ActivityDefinition(json_data) {
		var instance = this;

		this.id = parseInt(json_data.id, 10);
		this.name = json_data.name;
		this.color = json_data.color;
		this.weeks = json_data.week_numbers;
		this.students_count = parseInt(json_data.students_count, 10);
		this.hours_count = parseInt(json_data.hours_count, 10);
		this.room_capacity_rate = parseFloat(json_data.room_capacity_rate, 10);
		this.periodical = json_data.periodical || false;
		
		this.activitydefinition_events = [];
		$.each(json_data.events || [], function(key, values) {
// TODO: count remaining students count
			instance.activitydefinition_events.push(new ActivityDefinitionEvent(values, instance));
		});

		this.calendar_events = [];

// TODO: rename to tools.createWatchedProperty (e.g. tools.createBindedProperty)
		tools.watch(this, 'remaining_students_count', this.students_count, this.updateRemainingStudentsCountNode);

// TODO:
		this.node = undefined;
		this.wrapper_node = undefined;
		this.remaining_students_count_node = undefined;
		this.events_node = undefined;

		this.attributes = {
			'data-id': this.id,
			// 'data-hours-count': this.hours_count,
			'href': '/data/activitydefinition/'+this.id+'/update/',
			'target': '_blank',
		};

	};
	ActivityDefinition.prototype.updateRemainingStudentsCountNode = function() {
		if (this.remaining_students_count_node) {
			var value = this.remaining_students_count;
			$(this.remaining_students_count_node).html(value);
			if (value > 0)
				$(this.remaining_students_count_node).addClass('bg-danger');
			else
				$(this.remaining_students_count_node).removeClass('bg-danger');
		}
	};
	ActivityDefinition.prototype.addEventFromJSON = function(event_json) {
		var new_event = new ActivityDefinitionEvent(event_json.id, undefined, event_json);
		if (event_json.rooms)
			var instance = this;
			$.each(event_json.rooms, function(i, room) {
				if (room.capacity) {
					instance.remaining_students_count.set(instance.remaining_students_count.get() - parseInt(room.capacity, 10));
				}
			});
		this.activitydefinition_events.push(new_event);
		if (this.wrapper_node) {
			$(this.events_node).append($('<li/>').append(new_event.getHtmlNode()));
		}
	};
	ActivityDefinition.prototype.getHtmlNode = function() {
		if (!this.wrapper_node) {
			this.events_node = $('<ul/>');
			this.remaining_students_count_node = tools.createHtmlNode('span', '', [], ['badge', 'pull-right']);
			this.updateRemainingStudentsCountNode();
			this.node = tools.createHtmlNode('a', this.name, this.attributes);
			$(this.node).css('color', this.color);
			$(this.node).data('obj', this);
			this.wrapper_node = $('<li/>')
				.append(this.remaining_students_count_node)
				.append(this.node)
				.append(this.events_node);
			var instance = this;
			$.each(instance.activitydefinition_events, function(key, ad_event) {
				var ad_event_node = ad_event.getHtmlNode();
				$(instance.events_node).append($('<li/>').append(ad_event_node));
			});
			this.setDraggable();
		}
		return this.wrapper_node;
	};
	ActivityDefinition.prototype.createEvent = function(json_data) {
		// var data = {
		// 	'start': start,
		// 	'end': end,
		// 	'name': this.name
		// }
		console.log('adCreateEvent, data:', json_data);
		var calendar_event = new CalendarEvent(json_data, this);
		var activitydefinition_event = new ActivityDefinitionEvent(json_data, this);
		this.calendar_events.push(calendar_event);
		this.activitydefinition_events.push(activitydefinition_event);
		$(this.events_node).append($('<li/>').append(activitydefinition_event.getHtmlNode()));
		return calendar_event;
	};
	ActivityDefinition.prototype.setDraggable = function() {
		if (this.node) {
			$(this.node).addClass('ad-draggable');
			var draggable_options = {
				appendTo: '#wrap',
				helper: 'clone',
			};
			$(this.node).draggable(draggable_options);
		}
	};


	function Event(json_data, activity_definition) { // model_type: onetimeevent/semesterevent
		this.id = parseInt(json_data.id, 10);
		this.model_type = json_data.model_type || 'event';
		this.color = json_data.color || '';
		this.name = json_data.name || json_data.auto_name || '';
		this.fixed = json_data.fixed || false;
		this.rooms = json_data.rooms || [];
		this.start = json_data.start || '';
		this.end = json_data.end || '';
		this.weeks = json_data.weeks || '';
		this.holiday = json_data.holiday || false;
		this.hours_count = json_data.hours_count || 0;
		if (activity_definition) {
			if (!this.hours_count)
				this.hours_count = activity_definition.hours_count;
			if (!this.color)
				this.color = activity_definition.color;
			if (!this.name)
				this.name = activity_definition.name;
		}			

		this.activity_definition = activity_definition || undefined;

		this.text = '';
		this.tag = 'a';
		this.classes = [];
		if (this.id)
			this.attributes = {
				'event-id': this.id,
				'href': '/timetable/'+this.model_type+'/'+this.id+'/update/',
				'target': '_blank',
			}
		else
			this.attributes = {};
		this.attributes['title'] = this.name;
	};
	Event.prototype.getPopoverTitle = function() {
		return this.name;
	};
	Event.prototype.getPopoverContent = function() {
		return '<strong>From:</strong> '+this.start+'<br /><strong>To:</strong> '+this.end;
	};
	Event.prototype.getHtmlNode = function() {
		if (!this.node) {
			this.text = this.text.trim();
			if (this.text.substr(-1) == ',')
				this.text = this.text.slice(0, -1);
			this.node = tools.createHtmlNode(this.tag, this.text || '(empty)', this.attributes, this.classes);
			this.node.data('obj', this);
			if (this.color)
				this.node.css('color', this.color);
			this.setEvents();
		}
		return this.node;
	};
	Event.prototype.setEvents = function() {
		var instance = this;
		$.each(this.setEventsCallbacks, function(key, value) {
			instance[value].call(instance);
		});
	};
	Event.prototype.setPopover = function() {};
	Event.prototype.setDraggable = function() {};
	Event.prototype.setEventsCallbacks = ['setPopover', 'setDraggable'];
	

	function CalendarEvent(json_data, activity_definition) {
		Event.call(this, json_data, activity_definition);
		this.classes.push('cal-cell-event');
		this.text = this.name;
	};
	tools.inherit(CalendarEvent, Event);
	CalendarEvent.prototype.setDraggable = function() {
		if (this.node)
			setCalendarEventDraggable(this.node);
	};
	CalendarEvent.prototype.setPopover = function() {
		if (this.node)
			setCalendarEventPopover(this.node);
	};
	

	function ActivityDefinitionEvent(json_data, activity_definition) {
		Event.call(this, json_data, activity_definition);
		var instance = this;
		$.each(instance.rooms, function(key, room) {
			instance.text += room.name + ', ';
		});
		if (instance.start && instance.end)
			instance.text += instance.start + ' - ' + instance.end;
	};
	tools.inherit(ActivityDefinitionEvent, Event);
	ActivityDefinitionEvent.prototype.setDraggable = function() {
		if (this.node) {
			var instance = this;
			$(this.node).addClass('event-draggable');
			var draggable_options = {
				appendTo: '#wrap',
				helper: 'clone',
				start: function(event, ui) {
					var ad = $(this).closest('ul').closest('li').find('.ad-draggable');
					// $(ui.helper).attr('data-hours-count', $(ad).attr('data-hours-count'));
					$(ui.helper).attr('data-hours-count', instance.hours_count);
					// $(ui.helper).attr('title', $(ad).html());
					$(ui.helper).attr('title', instance.name);
					// $(ui.helper).html($(ad).html());
					$(ui.helper).html(instance.name);
					$(ui.helper).addClass('cal-cell-event');
				},
			};
			$(this.node).draggable(draggable_options);
		}
	};



	function setCalendarEventPopover(elements) {
		var popover_settings = {
			html: true,
			trigger: 'hover',
			placement: 'top',
			delay: {show: 1000, hide: 200},
			content: function() {
				console.log('getting popover content for this', this);
				return $(this).html();
			}
		};
		$(elements).popover(popover_settings);

		$(elements).hover(function() {
			// on mouse in
			if ($(this).closest('.cal-cell').hasClass('ui-selecting'))
				return false;
			var id = $(this).attr('event-id');
			$('.cal-cell-event[event-id="'+id+'"]').closest('.cal-cell').addClass('cal-cell-hover').css('background-color', tools.getRGBAfromElementRGB(this));
		}, function() {
			// on mouse out
			$('.cal-cell-hover').css('background-color', '').removeClass('cal-cell-hover');
		});

		$(elements).on('show.bs.popover', function () {
			if ($(this).closest('.cal-cell').hasClass('ui-selecting'))
				return false;
		});
		$(elements).on('shown.bs.popover', function () {
			$(this).parent().find('.popover-title').css('background-color', tools.getRGBAfromElementRGB(this));
		});
	};


	function setCalendarEventDraggable(elements) {
		var draggable_options = {
			start: function(event, ui) {
				var id = $(ui.helper).attr('event-id');
				var event_cells = $('.cal-cell-event[event-id="'+id+'"]');
				$(ui.helper).attr('data-hours-count', event_cells.length);
				$(event_cells).not(ui.helper).remove();
			},
		};
		$(elements).addClass('event-draggable');
		$(elements).draggable(draggable_options);
	};



	function Calendar(wrapper, options) {

		var instance = this;
		this.wrapper = wrapper;
		this.settings = $.extend({}, $.fn.timetableCalendar.defaults, options);

		this.activity_definitions = [];


		// "constructor" function called at the end of this file
		this.init = function() {

			console.log('calendar init with data', instance.settings.data);

			instance.selected_cells = new Array();
			instance.modal = false;

			instance.initForms();
			instance.initInputMethodChooser();
			instance.initDroppable();
			instance.initActivityFilter();
			instance.initSelectableCells();

			setCalendarEventPopover('.cal-cell-event');
			setCalendarEventDraggable('.cal-cell-event');
		};


		this.initForms = function() {
			instance.onetimeevent_modal = $(instance.settings.onetimeevent_modal).modal(instance.settings.modal_settings);
			$(instance.onetimeevent_modal).on('show.bs.modal', instance.initOneTimeEventData);
			$(instance.onetimeevent_modal).on('hide.bs.modal', instance.resetSelectedElements);

			instance.semesterevent_modal = $(instance.settings.semesterevent_modal).modal(instance.settings.modal_settings);
			$(instance.semesterevent_modal).on('show.bs.modal', instance.initSemesterEventData);
			$(instance.semesterevent_modal).on('hide.bs.modal', instance.resetSelectedElements);

			instance.onetimeevent_form = $.formTools_AjaxForm($('form', $(instance.onetimeevent_modal)), {
				success_callback: instance.onetimeeventFormSuccessCallback,
				unsuccess_callback: instance.formUnsuccessCallback,
			});
			instance.semesterevent_form = $.formTools_AjaxForm($('form', $(instance.semesterevent_modal)), {
				success_callback: instance.semestereventFormSuccessCallback,
				unsuccess_callback: instance.formUnsuccessCallback,
			});
		};


		this.initInputMethodChooser = function() {
			$('body').on('set_calendar_input_method', function(event, method_index) {
				if (method_index > instance.settings.input_methods.length - 1) {
					console.error('Calendar input method index out of range: ' + method_index);
				} else {
					instance.input_method = instance.settings.input_methods[method_index];

					if (instance.input_method == 'activities') {
						$(instance.wrapper).selectable('disable');
						instance.modal = false;
					} else {
						$(instance.wrapper).selectable('enable');
						if (instance.input_method == 'onetime')
							instance.modal = instance.onetimeevent_modal;
						else if (instance.input_method == 'semester')
							instance.modal = instance.semesterevent_modal;
					}
				}
			});
		};


		this.initActivityFilter = function() {
			var filter_form = $(instance.settings.activity_filter_form);
			var target = $(instance.settings.activity_list_target);

			var getMultiValue = function(name) {
				var temp = [];
				var values = filter_form.find('[name="'+name+'"]').val() || [];
				if (typeof(values) == "string" || typeof(values) == "number")
					return values;
				$.each(values, function(key, value) {
					if (value)
						temp.push(value);
				});
				return temp.join('_');
			};
			
			$(filter_form).submit(function(event) {

				event.preventDefault();
				event.stopPropagation();

				target.html('<div class="ajax-loader"></div>');
				
				var data = {};
				
				var activity_values = getMultiValue('activity_type');
				if (activity_values.length < 1) {
					var temp = [];
					$('select[name="activity_type"] option', $(filter_form)).each(function(key, option) {
						if ($(option).val())
							temp.push($(option).val());
					});
					activity_values = temp.join('_');
				}
				data['activitytype'] = activity_values;
				data['year'] = getMultiValue('year');
				data['group'] = getMultiValue('group');
				data['subject'] = getMultiValue('subject');
				data['department'] = getMultiValue('department');

				instance.initActivityDefinitions(target, data);

				$(this).closest('.collapse').collapse('hide');
			});
		};


		this.initActivityDefinitions = function(target, source_data) {
			var activity_list_url = $(this.settings.activity_filter_form).attr('action') || '';
			var instance = this;

			$.getJSON(activity_list_url, $.extend({
					'format': 'json', 
					'limit': instance.settings.activity_list_limit,
				}, source_data),
				function(response, status, xhr) {
					target.empty();
					instance.activity_definitions.length = 0;
					if (response.length == 0) {
						target.html('<li><div class="alert alert-info">No activities match the filter.</div></li>');
					} else {
						$.each(response, function(key, activity_definition_data) {
							var activity_definition = new ActivityDefinition(activity_definition_data);
							instance.activity_definitions.push(activity_definition);
							target.append(activity_definition.getHtmlNode());
						});
					}
				}
			);
		};


		this.initSelectableCells = function() {
			$(instance.wrapper).selectable({
				filter: "td",
				start: function(event, ui) {
					instance.selected_cells.length = 0;
				},
				stop: function(event, ui) {
					if (instance.selected_cells.length > 0) {
						$(instance.modal).modal('show');
					}
				},
				selected: function(event, ui) {
					instance.selected_cells.push(ui.selected);
				},
				unselected: function(event, ui) {
					instance.selected_cells.pop(ui.unselected)
				},
			});
		};


		this.onetimeeventFormSuccessCallback = function(responseText, statusText, xhr, form) {
			var scope = form;
			var data = {};
			data['model_type'] = 'onetimeevent';
			data['start'] = $(".datepicker-from", scope).val() + " " + $(".timepicker-from", scope).val();
			data['end'] = $(".datepicker-to", scope).val() + " " + $(".timepicker-to", scope).val();
			instance.formSuccessCallback(responseText, statusText, xhr, form, data);
		};


		this.semestereventFormSuccessCallback = function(responseText, statusText, xhr, form) {
			var scope = form;
			var data = {};
			data['model_type'] = 'semesterevent';
			data['start'] = $(".timepicker-from", scope).val();
			data['end'] = $(".timepicker-to", scope).val();
			// data['days'] = $('[name="'+model_type+'-days"][checked="checked"]');
			// data['weeks'] = $('[name="'+model_type+'-weeks"][checked="checked"]');
			instance.formSuccessCallback(responseText, statusText, xhr, form, data);
		};


		this.formSuccessCallback = function(responseText, statusText, xhr, form, data) {

			var scope = form;

			if (data == undefined)
				data = {}
			data['id'] = responseText.id;
			data['custom_color'] = $('.colorpicker', scope).val() ? $("#id_semesterevent-custom_color", scope).val() : '';
			data['name'] = $('[name="'+data.model_type+'-name"]', scope).val();
			data['auto_name'] = responseText.object_str;

			var rooms_finished = false;
			var ads_ids = $('[name="'+data.model_type+'-activities"]', scope).val() || [];
			var rooms_ids = $('[name="'+data.model_type+'-rooms"]', scope).val() || [];
			var rooms_node = $('[name="'+data.model_type+'-rooms"]', scope);
			data['rooms'] = [];

			var rooms_loaded_cb = function() {

				rooms_finished = true;

				// correct missing rooms
				if (data['rooms'].length != rooms_ids.length) {
					$.each(data['rooms'], function() {
						rooms_ids.splice(rooms_ids.indexOf(this.id), 1);
					});
					$.each(rooms_ids, function(key, value) {
						var name = $(rooms_node).children('[value="'+value+'"]').first().html();
						console.info('Could not retrieve room info ' + value + ': ' + name);
						data['rooms'].push({'id': value, 'name': name});
					});
				}
				
				// insert event node to left panel (under related activity definition node)
				var new_event_node = undefined;
				$.each(ads_ids, function() {
					var ad_id = parseInt(this, 10);
					$.each(instance.activity_definitions, function() {
						if (this.id == ad_id) {
							var data2 = {
								id: responseText.id,
								auto_name: data.name,
							};
							new_event_node = this.createEvent($.extend({}, data, data2));
							// new ActivityDefinitionEvent($.extend({}, data, data2), this);
							// this.addEventFromJSON($.extend({}, data, data2));
							return false;
						}
					});
				});

				// insert event node to calendar
				$(instance.selected_cells).each(function() {
					var calendar_event = new_event_node || new CalendarEvent(data);
					console.log('to add calendar event nodes', calendar_event, new_event_node);
					$(this).find(instance.settings.events_wrapper).append(calendar_event.getHtmlNode());
				});

				if (data.model_type == 'semesterevent') {
					$(instance.semesterevent_modal).modal('hide');
					instance.semesterevent_form.reset();
				} else if (data.model_type == 'onetimeevent') {
					$(instance.onetimeevent_modal).modal('hide');
					instance.onetimeevent_form.reset();
				}
			};


			var rooms_timeout = window.setTimeout(rooms_loaded_cb, instance.settings.room_timeout * rooms_ids.length);

			$.each(rooms_ids, function(key, value) {
				var id = parseInt(value, 10);
				$.getJSON('/data/room/'+id+'/', {'format': 'json'}, function(responseText, status, xhr) {
					data['rooms'][key] = responseText[0]; // because json allways returns an array
					if (data['rooms'].length == rooms_ids.length && !rooms_finished) {
						window.clearTimeout(rooms_timeout);
						rooms_loaded_cb();
					}
				});
			});
			// if (rooms_ids.length == 0) {
			// 	window.clearTimeout(rooms_timeout);
			// 	rooms_loaded_cb();
			// }

		};


		this.formUnsuccessCallback = function(responseText, textStatus, XMLHttpRequest) {
			alert('Form submit unsuccessfull.');
		};


		this.resetSelectedElements = function(e) {
			$(instance.selected_cells).removeClass('ui-selected');
			instance.selected_cells.length = 0;
		};


		this.initData = function(prefix, scope) {
			var start = instance.selected_cells[0];
			var end = instance.selected_cells[instance.selected_cells.length-1];
			
			$('.timepicker-from', $(scope)).val($(start).attr('data-time-from'));
			$('.timepicker-to', $(scope)).val($(end).attr('data-time-to'));

			if (instance.settings.data.room)
				$('[name="'+prefix+'-rooms"]', $(scope)).val(instance.settings.data.room.id);
			if (instance.settings.data.group)
				$('[name="'+prefix+'-groups"]', $(scope)).val(instance.settings.data.group);

		}


		this.initOneTimeEventData = function() {
			instance.initData('onetimeevent', instance.onetimeevent_modal);

			var start = instance.selected_cells[0];
			var end = instance.selected_cells[instance.selected_cells.length-1];
			$('.datepicker-from', $(instance.onetimeevent_modal)).val($(start).attr('data-date'));
			$('.datepicker-to', $(instance.onetimeevent_modal)).val($(end).attr('data-date'));
		};


		this.initSemesterEventData = function() {
			instance.initData('semesterevent', instance.semesterevent_modal);

			var start = instance.selected_cells[0];
			var end = instance.selected_cells[instance.selected_cells.length-1];
			var start_col_index = $(start).index() - 1;
			var end_col_index = $(end).index() - 1;
			$('input[name="semesterevent-days"]').each(function(index, element) {
				if (index >= start_col_index && index <= end_col_index)
					$(element).prop('checked', true);
				else 				
					$(element).prop('checked', false);
			});
		};


		this.initDroppable = function() {
			var droppable_parent = $('tbody', instance.wrapper).first();
			var get_event_cells = function(start, ui) {
				var obj = $(ui.draggable).data('obj');
				console.log('get_event_cells obj', obj, ui);
				var length = undefined;
				if (obj)
					length = obj.hours_count;
				else
					length = parseInt($(ui.helper).attr('data-hours-count'));
				var elements = new Array();
				var start_col_index = $(start).index()-1;
				var start_row_index = $(start).parent().index();
				for (var i=0; i<length; i++) {
					elements.push($($($(droppable_parent).children('tr')[start_row_index + i]).children('td')[start_col_index]));
				}
				return elements;
			}

			var droppable_options = {
				accept: '.ad-draggable, .event-draggable',
				tolerance: 'pointer',
				over: function(event, ui) {
					var elements = get_event_cells($(this), ui);
					$(elements).each(function() {
						$(this).addClass('ui-state-highlight');
					});
				},
				out: function(event, ui) {
					var elements = get_event_cells($(this), ui);
					$(elements).each(function() {
						$(this).removeClass('ui-state-highlight');
					});
				},
				drop: function(event, ui) {

					instance.selected_cells = get_event_cells($(this), ui);
					$('.ui-state-highlight').removeClass('ui-state-highlight');

					if ($(ui.helper).hasClass('ad-draggable')) {
						// crate new event
						console.log('drop ad-draggable, draggable:', $(ui.draggable).data('obj'));
						console.log('drop ad-draggable, helper:', $(ui.helper).data('obj'));

						var activity_definition = $(ui.draggable).data('obj');

						if (activity_definition) {
							if (activity_definition.periodical) {
								instance.initSemesterEventData();
								$('[name="semesterevent-activities"]', $(instance.semesterevent_modal)).val(activity_definition.id);
								// TODO: nastavit weeks podla toho, ako je nastavene pri activity definition => previazat objekt AD s html uzlom AD
								instance.semesterevent_form.submit();
							} else {
								instance.initOneTimeEventData();
								$('[name="onetimeevent-activities"]', $(instance.onetimeevent_modal)).val(activity_definition.id);
								instance.onetimeevent_form.submit();
							}
						}
					} else {
						// update existing event
						var id = $(ui.helper).attr('event-id');
						$('.cal-cell-event[event-id="'+id+'"]').remove();

						var cells = get_event_cells(this, ui);
						var csrf = $('input[name="csrfmiddlewaretoken"]').first().val();
						var last = cells.length - 1;
						var data = {
							'csrfmiddlewaretoken': csrf,
							'time_from': $(cells[0]).attr('data-time-from'),
							'time_to': $(cells[last]).attr('data-time-to'),
							'date_from': $(cells[0]).attr('data-date'),
							'date_to': $(cells[last]).attr('data-date')
						};
						if (instance.settings.data.room)
							data['room'] = instance.settings.data.room.id;

						$.ajax({
							url: '/timetable/event/' + $(ui.helper).attr('event-id') + '/update/',
							type: 'POST',
							dataType: 'text',
							data: data,
							success: function(data, textStatus, xhr) {

								$(ui.helper).css('position', '');
								$(ui.helper).css('top', '');
								$(ui.helper).css('left', '');

								$(ui.draggable).popover('destroy');
								$('.cal-cell-hover').css('background-color', '').removeClass('cal-cell-hover');

								$(instance.selected_cells).each(function() {
									var event_node = $(ui.helper).clone(true, false);
									setCalendarEventPopover(event_node);
									setCalendarEventDraggable(event_node);
									$(this).find(instance.settings.events_wrapper).append(event_node);
								});

								$(ui.helper).remove();
							}
						});
					}
				}
			};
			$('.cal-cell').droppable(droppable_options);
		};

		this.init();
	};


	$.fn.timetableCalendar = function(options) {
		$(this).each(function() {
			var calendar = new Calendar(this, options);
		});
		return this;
	};

	$.fn.timetableCalendar.defaults = {
		onetimeevent_modal: '#modal-onetimeevent',
		semesterevent_modal: '#modal-semesterevent',
		data: {},
		cell_wrapper: '.cal-cell',
		events_wrapper: '.cal-cell-events',
		event_wrapper: '.cal-cell-event',
		calendar_filter_form: '#calendar-filter',
		activity_filter_form: '#activity-filter',
		activity_list_target: '#activity-list',
		activity_list_limit: 20,
		modal_settings: {
			show: false,
			backdrop: 'static',
		},
		input_methods: ['activities', 'onetime', 'semester'],
		room_timeout: 1100,
	};

}(jQuery));