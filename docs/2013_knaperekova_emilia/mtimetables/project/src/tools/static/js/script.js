(function($) {

	$(function() {

		// scrollbar
		$('#left-panel').perfectScrollbar({
			wheelSpeed: 50,
			suppressScrollX: true,
			includePadding: true,
		});

		// 
		$('#content-aside .panel').collapse();

		// forms
		$('body').on('form_loaded', 'form', function() {
			$(this).formTools_initFields();
			init_dynamic_formsets($(this));
		});
		$('fieldset').on('form_elements_loaded', '.dynamic-form', function() {
			$(this).formTools_initFields();
		});
		$('form').trigger('form_loaded');


	});


	function init_dynamic_formsets(scope) {

		// console.log('init dynamic formsets in scope', scope);

		if (scope == undefined) {
			scope = $('body');
		}

		$('#formset_requireobject_requirement_packages', scope).dynamicFormSet('requirement package', {
			sortable: true,
		});
		$('#formset_room_equipments', scope).dynamicFormSet('equipment');
		$('#formset_user_groups', scope).dynamicFormSet('group');
		$('#formset_user_departments', scope).dynamicFormSet('department');
		$('#formset_timetablegrid_hours', scope).dynamicFormSet('hour');
		$('#formset_subject_study_types', scope).dynamicFormSet('study type');
		$('#formset_subject_teachers', scope).dynamicFormSet('user');
		$('#formset_semesterevent_users', scope).dynamicFormSet('user');
		$('#formset_onetimeevent_users', scope).dynamicFormSet('user');
		$('#formset_requirementtype_object_requirementtype_connection', scope).dynamicFormSet('object');

	}

}(jQuery));