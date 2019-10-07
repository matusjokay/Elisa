(function($) {

	$.fn.dynamicFormSet = function(label, options) {
		$(this).each(function() {
			new DynamicFormSet(this, label, options);
		});
		return this;
	}

	$.fn.dynamicFormSet.defaults = {
		sortable: false,
	}

	function DynamicFormSet(element, label, options) {

		var instance = this;
		this.label = label;
		this.element = element;
		this.settings = $.extend({}, $.fn.dynamicFormSet.defaults, options);

		this.init = function() {

			$('.panel-group', $(instance.element)).append('<div><a href="#" class="btn btn-link add-form">Add '+label+'...</a></div>').each(instance.set_row_events);

			if (instance.settings.sortable) {

				var sortable_element = $('.panel-group', $(instance.element));

				$('.dynamic-form input[name$="ORDER"]', $(sortable_element)).parent().css('display', 'none');
				$('.dynamic-form .form-inline', $(sortable_element)).prepend('<span class="sortable-handler">{% bootstrap_icon "move" %}</span>');
				$(sortable_element).disableSelection().sortable({
					cursor: 'move',
					opacity: 0.7,
					handle: '.sortable-handler',
					items: '> .dynamic-form',
					update: function(event, ui) {
						$('.dynamic-form input[name$="ORDER"]', $(sortable_element)).each(function(index, value) {
							if ($(this).val())
								$(this).val(index+1)
						});
					}
				});

			}
		}

		this.set_row_events = function() {
			var formset_element = $(this).parent();
			var formset_wrapper = $(this);
			var formset_row = $(formset_wrapper).children('.dynamic-form:last').css('display', 'none');

			// remove some classes and attributes
			$(formset_row).find('*[required="required"]').removeAttr('required');
			$(formset_row).find('.bootstrap-select').remove();
			$(formset_row).find('.hasTimepicker').removeClass('hasTimepicker');
			$(formset_row).find('.hasDatepicker').removeClass('hasDatepicker');
			$(formset_row).find('.hasColorpicker').removeClass('hasColorpicker');

			var prefix = $(formset_element).attr('id').substring($(formset_element).attr('id').indexOf('_')+1);
			$(formset_element).find('.add-form').click(function(event) {
				event.preventDefault();
				event.stopPropagation();
				new_row = instance.add_form(prefix, formset_row);
				$(new_row).trigger('form_elements_loaded');
				$(new_row).find('fieldset').each(instance.set_row_events);
			});
		}

		this.update_element_index = function(el, prefix, ndx) {
			var id_regex = new RegExp('(' + prefix + '-\\d+)');
			var replacement = prefix + '-' + ndx;
			if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
			if ($(el).attr("href")) $(el).attr("href", $(el).attr("href").replace(id_regex, replacement));
			// if ($(el).attr("data-id")) $(el).attr("data-id", $(el).attr("data-id").replace(id_regex, replacement));
			if (el.id) el.id = el.id.replace(id_regex, replacement);
			if (el.name) el.name = el.name.replace(id_regex, replacement);
		}

		this.add_form = function(prefix, row) {
			var form_count = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
			var new_row = $(row).clone(false, false);
			$(new_row).find('input, select, button, fieldset, .panel-title, .panel-collapse').each(function() {
				instance.update_element_index(this, prefix, form_count);
			});
			$(new_row).css('display', 'block');
			$(row).before(new_row);
		//     $(row).find('.delete-row').click(function() {
		//         instance.delete_form(this, prefix);
		//     });
			$('#id_' + prefix + '-TOTAL_FORMS').val(form_count + 1);
			return new_row;
		}

		this.delete_form = function(btn, prefix) {
			$(btn).parents('.dynamic-form').remove();
			var forms = $('.dynamic-form');
			$('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
			for (var i=0, form_count=forms.length; i<form_count; i++) {
				$(forms.get(i)).children().not(':last').children().each(function() {
					instance.update_element_index(this, prefix, i);
				});
			}
			return false;
		}

		this.init();
		

	}

}(jQuery));