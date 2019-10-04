// for debugging
// TODO: comment or delete
global_table_events = undefined;
global_all_events = undefined;
global_activity_definitions = undefined;
global_calendar = undefined;

(function($) {

	var TRANSITION_DURATION = 2000;
	var SELECTING_CLASS = 'ui-selecting';
	var SELECTED_CLASS = 'ui-selected';


	$.fn.timetableCalendar = function(options) {
		$(this).each(function() {
			var calendar = new Calendar(this, options);
		});
		return this;
	};


	$.fn.timetableCalendar.defaults = {
		table_cell_wrapper: '.cal-cell',
		table_events_wrapper: '.cal-cell-events',
		table_event_wrapper: '.cal-cell-event',
		// calendar_filter_form: '#calendar-filter',
		// activity_filter_form: '#activity-filter',
		activity_list_target: '#activity-list',
		// activity_list_limit: 20,
		bottom_panel: '#bottom-panel .panel-body',

		event_url_base: '/timetable/',
		url_update_suffix: '/update/',
		url_create_suffix: '/create/',

		onetimeevent_modal: '#modal-onetimeevent',
		semesterevent_modal: '#modal-semesterevent',
		data: {},
		modal_settings: {
			show: false,
			backdrop: 'static',
		},
		room_timeout: 1100,
		popover: {
			html: true,
			trigger: 'hover',
			placement: function() {},
			// placement: 'auto top',
			delay: {show: 500, hide: 200},
			container: 'body',
		},
	};


	function Calendar(table_wrapper, options) {

		var instance = this;

		this.settings = $.extend({}, $.fn.timetableCalendar.defaults, options);

		this.table_wrapper = table_wrapper;

		// TODO: check elements of these objects during events creation, activities and calendar table reloading
		this.all_events = {};
		this.table_events = {};
		this.activity_definitions = {};
		// this.collision_events = {};

		this.room = this.settings.data.room || undefined;
		this.group = this.settings.data.group || undefined;
		this.user = this.settings.data.user || undefined;
		this.subject = this.settings.data.subject || undefined;

		global_calendar = this;
		global_all_events = this.all_events;
		global_table_events = this.table_events;
		global_activity_definitions = this.activity_definitions;
		global_collision_events = {};


		$(this.table_wrapper).on('calendar_json_events_loaded', function(event, json_events, room, group, user, subject) {
			instance.reloadTableEvents.call(instance, json_events, room, group, user, subject);  // this is because of the right context in reload function
		});

		$(this.table_wrapper).on('calendar_json_activites_loaded', function(event, json_activities) {
			instance.reloadActivities.call(instance, json_activities);  // this is because of the right context in reload function
		});

		this.setDroppable();
		this.setSelectable();
		this.setInputMethodChooser();

	};
	Calendar.prototype.weekdays = new Array("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday");
	Calendar.prototype.loadEvent = function(event_json, activity_definition) {
		var id = parseInt(event_json.id);
		if (!this.all_events[id])
			this.all_events[id] = new TEvent(this, event_json, activity_definition);
		else if (activity_definition)
			this.all_events[id].activity_definition = activity_definition;
		return this.all_events[id];
	};
	Calendar.prototype.reloadTableEvents = function(json_events, room, group, user, subject) {
		$.each(this.table_events, function() {delete this;}); // clear table events object

		this.room = room;
		this.group = group;
		this.user = user;
		this.subject = subject;

		this.cells = $(this.settings.table_cell_wrapper, $(this.table_wrapper));
		this.n_colls = $('tr:last', $(this.table_wrapper)).children(this.settings.table_cell_wrapper).length;

		var instance = this;
		$.each(json_events || [], function(event_key, event_data) {
			var id = parseInt(event_data.id);
			var event_obj = instance.table_events[id] = instance.loadEvent(event_data);

			$(instance.settings.table_event_wrapper + '[event-id="'+id+'"]', instance.table_wrapper).each(function(key, node) {
				new TableTEventNode(event_obj, node);
			});
		});

		this.setDroppable();

		// FAR FUTURE TODO:
		// Insert event nodes into calendar table directly by javascript.
		// Now calendar filter form ajax returns text/html table with event nodes.
	};
	Calendar.prototype.reloadActivities = function(json_activities) {
		$.each(this.activity_definitions, function() {delete this;}); // clear activity definition object

		var instance = this;
		$.each(json_activities || [], function(activity_key, activity_data) {
			var ad_obj = new ActivityDefinition(instance, activity_data);
			instance.activity_definitions[ad_obj.id] = ad_obj;

			// init activity definition events (create new or get existing TEvent objects)
			$.each(activity_data.events, function(event_key, event_data) {
				ad_obj.loadEvent(instance.loadEvent(event_data, ad_obj));
			});

			// create html node for activity definition
			var ad_node = new ADNode(ad_obj);
			$(instance.settings.activity_list_target).append(ad_node.getHtml());
		});
		$('#left-panel').scrollTop(0);
		$('#left-panel').perfectScrollbar('update');
	};
	Calendar.prototype.setInputMethodChooser = function() {
		var instance = this;
		$(this.table_wrapper).on('set_calendar_input_method', function(event, method) {
			instance.input_method = method;
			if (method == 'draganddrop')
				$(instance.table_wrapper).selectable('disable');
			else if (method == 'semesterevent' || method == 'onetimeevent')
				$(instance.table_wrapper).selectable('enable');
		});
	};
	Calendar.prototype.computeTEventNewCells = function(start, ui) {
		var obj = $(ui.draggable).data('obj');
		var length = 1;
		
		if (obj instanceof TableTEventNode) {
			length = obj.event_obj.table_event_nodes.length;
		} else if (obj instanceof ADTEventNode) {
			length = obj.event_obj.activity_definition.hours_count;
		} else if (obj instanceof ADNode) {
			length = obj.ad_obj.hours_count;
		}

		var selected_cells = new Array();
		var start_col_index = $(start).index()-1;
		var start_row_index = $(start).parent().index();
		for (var i=0; i<length; i++) {
			var offset = start_row_index * this.n_colls + start_col_index + i * this.n_colls;
			selected_cells.push(this.cells[offset]);
		}
		return selected_cells;
	};
	Calendar.prototype.setDroppable = function() {
		var instance = this;
		var droppable_options = {
			addClasses: false,
			accept: '.ad-draggable, .event-draggable',
			tolerance: 'pointer',

			over: function(event, ui) {
				$('.'+SELECTING_CLASS, this.table_wrapper).removeClass(SELECTING_CLASS);
				var cells = instance.computeTEventNewCells($(this), ui);
				$(cells).each(function() {
					$(this).addClass(SELECTING_CLASS);
				});
			},
			drop: function(event, ui) {

				var cells = instance.computeTEventNewCells(this, ui);
				var i_last_cell = cells.length - 1;
				var event_obj = undefined;
				var ad_obj = undefined;

				$(cells).each(function() {
					$(this).removeClass(SELECTING_CLASS);
					$(this).addClass(SELECTED_CLASS);
				});

				if ($(ui.helper).hasClass('ad-draggable')) {
					// create new event from activity definition
					ad_obj = $(ui.draggable).data('obj').ad_obj;
					var event_data = {
						model_type: (ad_obj.periodical) ? 'semesterevent' : 'onetimeevent',
					};
					event_obj = new TEvent(instance, event_data, ad_obj);
				} else {
					// update existing event
					event_obj = $(ui.draggable).data('obj').event_obj;
				}

				// set event date and time
				var datetime_from = $(cells[0]).attr('data-date') + ' ' + $(cells[0]).attr('data-time-from');
				var datetime_to = $(cells[i_last_cell]).attr('data-date') + ' ' + $(cells[i_last_cell]).attr('data-time-to');
				event_obj.updateDateTime(datetime_from, datetime_to);

				// set event rooms
				if (instance.room && instance.room.id) {
					var rewrite = true;
					var room_assigned = event_obj.containsRoom(instance.room.id);
					if (!(event_obj.rooms.length == 1 && room_assigned)) {
						var new_room = {id: instance.room.id, capacity: instance.room.capacity, name: instance.room.name};
						if (event_obj.rooms.length > 0)
							rewrite = window.confirm("Rewrite already assigned event rooms ("+event_obj.getRooms().join(', ')+") to "+instance.room.name+"?\r\nOtherwise event rooms will be set to "+event_obj.getRooms().join(', ')+( (!room_assigned) ? ", "+instance.room.name : "" )+".");
						if (rewrite)
							event_obj.rooms = [new_room];
						else {
							if (!room_assigned)
								event_obj.rooms.push(new_room);
						}
					}
				}

				event_obj.save({
					success_cb: function(data, textStatus, xhr) {

						// remove old event nodes
						$.each(event_obj.table_event_nodes, function(key, node_obj) {
							$(node_obj.node).remove();
						});
						event_obj.table_event_nodes = [];

						// set new event id
						if (!event_obj.id) {
							event_obj.id = data.id;
							// create activity definition event node
							ad_obj.loadEvent(event_obj);
						} else {
							// refresh activity definition event nodes
							$.each(event_obj.ad_event_nodes, function(key, ad_event_node) {
								ad_event_node.refresh();
							});
							if (event_obj.activity_definition)
								event_obj.activity_definition.updateRemainingStudentsCount();
						}

						// create new table event nodes
						$.each(cells, function(key, cell) {
							var new_event_node = new TableTEventNode(event_obj);
							$(cell).find(instance.settings.table_events_wrapper).append(new_event_node.getHtml());
							$(cell).removeClass(SELECTED_CLASS, TRANSITION_DURATION);
						});

						// check event collisions (for newly created and also updated event)
						$.ajax('/timetable/event/'+event_obj.id+'/collisions/', {
							success: function(data, textStatus, xhr) {
								if (data.length > 0) {
									var collision_events = [];
									$.each(data, function(key, event_json) {
										var collision_event = instance.loadEvent(event_json);
										collision_events.push(collision_event);
									});
									var collision_node = new CollisionsNode(event_obj, collision_events);
									$(instance.settings.bottom_panel).prepend(collision_node.getHtml());

									if ($('#bottom-panel').css('display') == 'none')
										$('#bottom-panel').css('display', 'block');
									$('#collapse-bottom-panel-content').collapse('show');

								}
							}
						});
					}
				});

			}
		};
		$(this.settings.table_cell_wrapper).droppable(droppable_options);
	};
	Calendar.prototype.setSelectable = function() {
		var instance = this;
		var selected_cells = [];

		// init modal ajax forms
		
		this.onetimeevent_modal = $(this.settings.onetimeevent_modal).modal(this.settings.modal_settings);
		$(this.onetimeevent_modal).on('show.bs.modal', function(event) {
			instance.initOneTimeEventData.call(instance, selected_cells);
		});

		this.semesterevent_modal = $(this.settings.semesterevent_modal).modal(this.settings.modal_settings);
		$(this.semesterevent_modal).on('show.bs.modal', function(event) {
			instance.initSemesterEventData.call(instance, selected_cells);
		});

		var modals_selector = this.settings.onetimeevent_modal + ', ' + this.settings.semesterevent_modal;

		$(modals_selector).on('hide.bs.modal', function(event) {
			$(selected_cells).removeClass('ui-selected', TRANSITION_DURATION);
			selected_cells.length = 0;
		});

		$('form', $(modals_selector)).ajaxForm({
			resetForm: true,
			success: function(responseText, statusText, xhr, form) {
				var new_event = new TEvent(instance, responseText.object_json);
				$.each(selected_cells, function(key, cell) {
					var new_event_node = new TableTEventNode(new_event);
					$(cell).find(instance.settings.table_events_wrapper).append(new_event_node.getHtml());
				});
				$(form).closest('.modal').modal('hide');
			},
		});


		// set selectable calendar table fields
		$(this.table_wrapper).selectable({
			disabled: true,			
			filter: instance.settings.table_cell_wrapper,
			start: function(event, ui) {
				$(selected_cells).removeClass('ui-selected');
				selected_cells.length = 0;
			},
			stop: function(event, ui) {
				if (selected_cells.length > 0) {
					if (instance.input_method == 'onetimeevent') {
						$(instance.settings.onetimeevent_modal).modal('show');
					} else if (instance.input_method == 'semesterevent') {
						$(instance.settings.semesterevent_modal).modal('show');
					}
				}
			},
			selected: function(event, ui) {
				selected_cells.push(ui.selected);
			},
			unselected: function(event, ui) {
				selected_cells.pop(ui.unselected)
			},
		});
	};
	Calendar.prototype.initData = function(selected_cells, prefix, scope) {
		var start = selected_cells[0];
		var end = selected_cells[selected_cells.length-1];
		$('.timepicker-from', $(scope)).val($(start).attr('data-time-from'));
		$('.timepicker-to', $(scope)).val($(end).attr('data-time-to'));
		if (this.room)
			$('[name="'+prefix+'-rooms"]', $(scope)).val(this.room.id);
		if (this.group)
			$('[name="'+prefix+'-groups"]', $(scope)).val(this.group);
		if (this.user)
			$('[name="'+prefix+'-users"]', $(scope)).val(this.user.id);
		if (this.subject)
			$('[name="'+prefix+'-subjects"]', $(scope)).val(this.subject);
	};
	Calendar.prototype.initOneTimeEventData = function(selected_cells) {
		this.initData(selected_cells, 'onetimeevent', this.onetimeevent_modal);
		var start = selected_cells[0];
		var end = selected_cells[selected_cells.length-1];
		$('.datepicker-from', this.onetimeevent_modal).val($(start).attr('data-date'));
		$('.datepicker-to', this.onetimeevent_modal).val($(end).attr('data-date'));
	};
	Calendar.prototype.initSemesterEventData = function(selected_cells) {
		this.initData(selected_cells, 'semesterevent', this.semesterevent_modal);
		var start = selected_cells[0];
		var end = selected_cells[selected_cells.length-1];
		var start_col_index = $(start).index() - 1;
		var end_col_index = $(end).index() - 1;
		$('input[name="semesterevent-days"]').each(function(index, element) {
			if (index >= start_col_index && index <= end_col_index)
				$(element).prop('checked', true);
			else 				
				$(element).prop('checked', false);
		});
	};



	// Class for storring timetable event objects.
	// For storring timetable event nodes (calendar table or activity definition event) use appropriate TEventNode class.
	// One TEvent object can be associated with multiple related TEventNode objects.
	function TEvent(calendar, json_data, activity_definition) {
		this.calendar = calendar;
		this.id = parseInt(json_data.id, 10) || undefined;
		this.model_type = json_data.model_type || 'onetimeevent'; // model_type: onetimeevent/semesterevent/event
		this.color = json_data.color || '';
		this.name = json_data.name || json_data.auto_name || '';
		this.fixed = json_data.fixed || false;
		this.rooms = json_data.rooms || [];
		this.start = json_data.start || '';
		this.end = json_data.end || '';
		this.week_numbers = json_data.week_numbers || [];
		this.day_numbers = json_data.day_numbers || [];
		this.holiday = json_data.holiday || false;
		this.hours_count = json_data.hours_count || 0;
		this.activity_definition = activity_definition || undefined;
		
		if (this.activity_definition) {
			if (!this.hours_count)
				this.hours_count = this.activity_definition.hours_count;
			if (!this.color)
				this.color = this.activity_definition.color;
			if (!this.name)
				this.name = this.activity_definition.name;
			if (this.activity_definition.periodical && this.week_numbers.length < 1) {
				this.week_numbers = activity_definition.week_numbers.slice(0);
			}
		}

		// correct wrong start and end (in datetime format) for semesterevent
		if (this.model_type == 'semesterevent' && this.start.split().length > 1) {
			this.updateDateTime(this.start, this.end);
		}

		this.table_event_nodes = [];
		this.ad_event_nodes = [];
		this.collision_event_nodes = [];
	};
	TEvent.prototype.containsRoom = function(room_id) {
		for (i=0; i<this.rooms.length; i++) {
			if (this.rooms[i].id == room_id) {
				return true;
			}
		}
		return false;
	};
	TEvent.prototype.updateDateTime = function(datetime_from, datetime_to, week_numbers) {
		if (this.model_type == 'semesterevent') {
			if (week_numbers)
				this.week_numbers = week_numbers.slice(0);
			else if (this.week_numbers.length < 1 && this.activity_definition)
				this.week_numbers = this.activity_definition.week_numbers.slice(0);
			this.day_numbers = [];
			var d1 = new Date(datetime_from);
			var d2 = new Date(datetime_to);
			for (var d = d1; d <= d2; d.setDate(d.getDate() + 1)) {
				var day = (d.getDay() - 1 < 0) ? 6 : d.getDay() - 1;
				this.day_numbers.push(day);
			}
			this.start = datetime_from.split(' ')[1];
			this.end = datetime_to.split(' ')[1];
		} else {
			this.start = datetime_from;
			this.end = datetime_to;
		}
	};
	TEvent.prototype.getDetailURL = function() {
		if (this.id)
			return this.calendar.settings.event_url_base + this.model_type + '/' + this.id + this.calendar.settings.url_update_suffix;
		return undefined;
	};
	TEvent.prototype.getUpdateURL = function() {
		if (this.id)
			return this.calendar.settings.event_url_base + 'event/' + this.id + this.calendar.settings.url_update_suffix;
		return undefined;
	};
	TEvent.prototype.getCreateURL = function() {
		return this.calendar.settings.event_url_base + this.model_type + this.calendar.settings.url_create_suffix;
	};
	TEvent.prototype.getWeekdays = function() {
		var weekdays = [];
		var instance = this;
		$.each(this.day_numbers, function(key, day_num) {
			weekdays.push(instance.calendar.weekdays[day_num]);
		});
		return weekdays;
	};
	TEvent.prototype.getWeeks = function() {
		var weeks = [];
		$.each(this.week_numbers, function(key, week_num) {
			weeks.push(week_num+1);
		});
		return weeks;
	};
	TEvent.prototype.getRooms = function() {
		var rooms = [];
		$.each(this.rooms, function(key, room) {
			rooms.push(room.name);
		});
		return rooms;
	};
	TEvent.prototype.getPopoverTitle = function() {
		return this.name;
	};
	TEvent.prototype.getPopoverContent = function() {
		var str = '<strong>From:</strong> '+this.start+'<br /><strong>To:</strong> '+this.end;
		if (this.model_type == 'semesterevent') {
			str += '<br /><strong>Days:</strong> ' + this.getWeekdays().join(', ');
			str += '<br /><strong>Weeks:</strong> ' + this.getWeeks().join(', ');
		}
		if (this.rooms.length > 0) {
			str += '<br /><strong>Rooms:</strong> ' + this.getRooms().join(', ');
		}
		return str;
	};
	TEvent.prototype.getCapacity = function() {
		var count = 0;
		$.each(this.rooms, function(key, room) {
			count += parseInt(room.capacity, 10);
		});
		return count;
	};
	TEvent.prototype.save = function(options) {
		// Saves ONLY time and room for existing events and activity definition for new events.
		var instance = this;

		// prepare data
		var data = {
			'csrfmiddlewaretoken': tools.getCSRF(),
		};
		if (this.model_type == 'semesterevent') {
			var weeks = [];
			$.each(this.week_numbers, function(key, week_no) {
				weeks.push('week_' + week_no);
			});
			var days = [];
			$.each(this.day_numbers, function(key, day_no) {
				days.push('day_' + day_no);
			});
			data[this.model_type + '-weeks'] = weeks;
			data[this.model_type + '-days'] = days;
			data[this.model_type + '-start'] = this.start;
			data[this.model_type + '-end'] = this.end;
			
		} else {
			var datetime_from = this.start.split(' ');
			var datetime_to = this.end.split(' ');
			data[this.model_type + '-start_0'] = datetime_from[0];
			data[this.model_type + '-start_1'] = datetime_from[1];
			data[this.model_type + '-end_0'] = datetime_to[0];
			data[this.model_type + '-end_1'] = datetime_to[1];
		}

		// set values required by form for new event creation
		if (!this.id) {
			data[this.model_type + '_users-TOTAL_FORMS'] = 0;
			data[this.model_type + '_users-INITIAL_FORMS'] = 0;
			data[this.model_type + '_users-MAX_NUM_FORMS'] = 1000;
			if (this.activity_definition)
				data[this.model_type + '-activities'] = this.activity_definition.id;
		}

		var roomsids = [];
		$.each(this.rooms, function(key, room) {
			roomsids.push(room.id);
		});
		data[this.model_type + '-rooms'] = roomsids;

		// prepare ajax settings
		// note:
		// 		traditional = true
		// 			rooms: 44
		// 			rooms: 88
		// 		traditional = false
		// 			rooms[]: 44
		// 			rooms[]: 88
		var ajax_settings = {
			type: 'POST',
			url: (this.id) ? this.getUpdateURL() : this.getCreateURL(),
			// dataType: 'text',
			data: data,
			traditional: true,
			success: function(data, textStatus, xhr) {
				console.info('Event successfully saved.');
				if (options.success_cb)
					options.success_cb(data, textStatus, xhr);
			},
			error: function(xhr, textStatus, errorThrown) {
				console.info('Event could not be saved.');
				if (options.error_cb)
					options.error_cb(xhr, textStatus, errorThrown);
			},
		};

		// process ajax request
		if (ajax_settings['url']) {
			$.ajax(ajax_settings);
		} else {
			console.error('Cannot save event, because no url set');
		}
	};



	function TEventNode(event_obj, node) {
		this.event_obj = event_obj;
		this.calendar = this.event_obj.calendar;
		this.node = node || undefined;

		if (this.node) {
			$(this.node).data('obj', this);
			this.setPopover();
			this.setDraggable();
		}
	};
	TEventNode.prototype.getText = function() {
		return this.event_obj.name || '(undefined)';
	};
	TEventNode.prototype.getAttributes = function() {
		return {
			'event-id': this.event_obj.id,
			'href': this.event_obj.getDetailURL(),
			'target': '_blank',
		};
	};
	TEventNode.prototype.getClasses = function() {
		return [];
	};
	TEventNode.prototype.setPopover = function() {
		if (this.node) {
			var instance = this;
			var options = {
				title: instance.event_obj.getPopoverTitle(),
				content: instance.event_obj.getPopoverContent(),
			};
			var settings = $.extend({}, instance.calendar.settings.popover, options);
			var table_cell_wrapper = instance.calendar.settings.table_cell_wrapper;
			$(instance.node).popover(settings);

			$(instance.node).hover(function() {
				// on mouse in
				var color = tools.getRGBAfromElementRGB(instance.node);
				if ($(instance.node).closest(table_cell_wrapper).hasClass('ui-selecting'))
					return false;
				$.each(instance.event_obj.table_event_nodes, function(key, node_obj) {
					$(node_obj.node).closest(table_cell_wrapper).addClass('cal-cell-hover').css('background-color', color);
				});
			}, function() {
				// on mouse out
				$.each(instance.event_obj.table_event_nodes, function(key, node_obj) {
					$(node_obj.node).closest(table_cell_wrapper).removeClass('cal-cell-hover').css('background-color', '');
				});
			});

			$(instance.node).on('show.bs.popover', function () {
				if ($(instance.node).closest(table_cell_wrapper).hasClass('ui-selecting'))
					return false;
			});
			$(instance.node).on('shown.bs.popover', function () {
				var color = tools.getRGBAfromElementRGB(instance.node);
				// $(this).parent().find('.popover-title').css('background-color', color);
				$('.popover-title').css('background-color', color);
			});
		}
	};
	TEventNode.prototype.setDraggable = function() {
		if (this.node) {
			$(this.node).addClass('event-draggable');
			var instance = this;
			var draggable_options = {
				addClasses: false,
				appendTo: '#wrap',
				helper: 'clone',
				start: function(event, ui) {
					if (instance.calendar.input_method != 'draganddrop')
						return false;
					var cbf = function(key, node_obj) {
						node_obj.setDragging();
					};
					$.each(instance.event_obj.table_event_nodes, cbf);
					$.each(instance.event_obj.ad_event_nodes, cbf);
					$.each(instance.event_obj.collision_event_nodes, cbf);
				},
			};
			$(this.node).draggable(draggable_options);
		}
	};
	TEventNode.prototype.setDragging = function() {
		if (this.node) {
			$(this.node).animate({opacity: 0.3});
		}
	};
	TEventNode.prototype.refresh = function() {
		if (this.node) {
			this.node.text(this.getText());
			this.node.animate({opacity: 1});
		}
	};
	TEventNode.prototype.getHtml = function() {
		if (!this.node) {
			this.node = tools.createHtmlNode('a', this.getText(), this.getAttributes(), this.getClasses());
			$(this.node).data('obj', this);
			if (this.event_obj.color)
				this.node.css('color', this.event_obj.color);
			this.setPopover();
			this.setDraggable();
		}
		return this.node;
	};



	function TableTEventNode(event_obj, node) {
		TEventNode.call(this, event_obj, node);
		event_obj.table_event_nodes.push(this);
	};
	tools.inherit(TableTEventNode, TEventNode);
	TableTEventNode.prototype.getClasses = function() {
		return ['cal-cell-event'];
	};




	function ADTEventNode(event_obj, node) {
		TEventNode.call(this, event_obj, node);
		event_obj.ad_event_nodes.push(this);
	};
	tools.inherit(ADTEventNode, TEventNode);
	ADTEventNode.prototype.getText = function() {
		var text = this.event_obj.getRooms().join(', ');
		if (this.event_obj.start && this.event_obj.end) {
			if (text)
				text += ': ';
			text += this.event_obj.start + ' - ' + this.event_obj.end;
		}
		text = text.trim();
		if (!text)
			text = '(empty)';
		return text;
	};



	function CollisionTEventNode(event_obj, node) {
		TEventNode.call(this, event_obj, node);
		// event_obj.collision_event_nodes.push(this);
	};
	tools.inherit(CollisionTEventNode, TEventNode);



	function ActivityDefinition(calendar, json_data) {
		var instance = this;

		this.calendar = calendar;
		this.id = parseInt(json_data.id, 10);
		this.name = json_data.name;
		this.color = json_data.color;
		this.week_numbers = json_data.week_numbers || [];
		this.students_count = parseInt(json_data.students_count, 10);
		this.hours_count = parseInt(json_data.hours_count, 10);
		this.room_capacity_rate = parseFloat(json_data.room_capacity_rate, 10);
		this.periodical = json_data.periodical || false;

		tools.watch(this, 'remaining_students_count', this.students_count, this.updateRemainingStudentsCountNode)
		
		// init events variable, events will be loaded by Calendar.reloadActivities method
		this.ad_events = {};

		this.nodes = [];
	};
	ActivityDefinition.prototype.updateRemainingStudentsCount = function() {
		var temp = this.students_count;
		$.each(this.ad_events, function(event_id, event_obj) {
			temp -= event_obj.getCapacity();
		});
		if (this.remaining_students_count != temp)
			this.remaining_students_count = temp;
	};
	ActivityDefinition.prototype.updateRemainingStudentsCountNode = function() {
		$.each(this.nodes, function(key, node) {
			node.updateRemainingStudentsCountNode();
		});
	};
	ActivityDefinition.prototype.loadEvent = function(event_obj) {
		if (!this.ad_events[event_obj.id]) {
			this.ad_events[event_obj.id] = event_obj;
			this.remaining_students_count -= event_obj.getCapacity();
			$.each(this.nodes, function(key, node_obj) {
				node_obj.loadEvent(event_obj);
			});
		}
		return this.ad_events[event_obj.id];
	};



	function ADNode(ad_obj) {
		this.ad_obj = ad_obj;
		this.calendar = this.ad_obj.calendar;
		this.ad_obj.nodes = [this];
		this.node = undefined;
		this.remaining_students_count_node = undefined;
		this.events_node = $('<ul/>');
		this.ad_node = undefined;

		this.setDraggable();
	};
	ADNode.prototype.getAttributes = function() {
		return {
			'ad-id': this.ad_obj.id,
			'href': '/data/activitydefinition/'+this.ad_obj.id+'/update/',
			'target': '_blank',
		};
	};
	ADNode.prototype.getClasses = function() {
		return [];
	};
	ADNode.prototype.loadEvent = function(event_obj) {
		var new_event_node = new ADTEventNode(event_obj);
		$(this.events_node).append($('<li/>').append(new_event_node.getHtml()));
	};
	ADNode.prototype.updateRemainingStudentsCountNode = function() {
		if (this.remaining_students_count_node) {
			var count = this.ad_obj.remaining_students_count;
			$(this.remaining_students_count_node).html(count);
			if (count > 0)
				$(this.remaining_students_count_node).addClass('bg-danger');
			else
				$(this.remaining_students_count_node).removeClass('bg-danger');
		}
	};
	ADNode.prototype.setDraggable = function() {
		if (this.ad_node) {
			$(this.ad_node).addClass('ad-draggable');
			var instance = this;
			var draggable_options = {
				addClasses: false,
				appendTo: '#wrap',
				helper: 'clone',
				start: function(event, ui) {
					if (instance.calendar.input_method != 'draganddrop')
						return false;
				},
			};
			$(this.ad_node).draggable(draggable_options);
		}
	};
	ADNode.prototype.getHtml = function() {
		if (!this.node) {
			var instance = this;

			this.remaining_students_count_node = tools.createHtmlNode('span', '', [], ['badge', 'pull-right']);
			this.updateRemainingStudentsCountNode();
			this.ad_node = tools.createHtmlNode('a', this.ad_obj.name, this.getAttributes(), this.getClasses());
			$(this.ad_node).css('color', this.ad_obj.color);
			$(this.ad_node).data('obj', this);
			
			// create activity definition events nodes
			$.each(this.ad_obj.ad_events, function(key, event_obj) {
				instance.loadEvent(event_obj);
			});
			
			// $(this.ad_node).data('obj', this.ad_obj);
			this.node = $('<li/>')
				.append(this.remaining_students_count_node)
				.append(this.ad_node)
				.append(this.events_node);

			this.setDraggable();
		}
		return this.node;
	};



	function CollisionsNode(event_obj, collision_events_objs) {
		this.event_obj = event_obj;
		this.collision_events_objs = collision_events_objs;
	};
	CollisionsNode.prototype.getHtml = function() {
		if (!this.node) {
			var instance = this;
			var n_collisions = this.collision_events_objs.length;
			var collisions_node = tools.createHtmlNode('span');
			for (var i=0; i<n_collisions; i++) {
				if (i>0)
					$(collisions_node).append(', ');
				var collision_event_node = new CollisionTEventNode(instance.collision_events_objs[i]);
				$(collisions_node).append(collision_event_node.getHtml());
			}
			var node = tools.createHtmlNode('div');
			var collision_event_node = new CollisionTEventNode(this.event_obj);
			node.append(collision_event_node.getHtml());
			node.append(' collisions: ');
			node.append(collisions_node);
			this.node = tools.wrapAlert(node, false, true);

			$(this.node).bind('closed.bs.alert', function() {
				console.log('closed', $('#bottom-panel .panel-body').children().length);
				if ($('#bottom-panel .panel-body').children().length <= 1) {
					$('#bottom-panel').css('display', 'none');
				}
			});
		}
		return this.node;
	};



}(jQuery));