var tools = {

	getRGBAfromElementRGB: function(element) {
		var color = $(element).css('color');
		var rgb = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
		var rgba = 'rgba(' + rgb[1] + ',' + rgb[2] + ',' + rgb[3] + ',0.3)';
		return rgba;
	},



	createHtmlNode: function(tag, text, attributes, classes) {
		attributes = attributes || {};
		var node = $('<'+tag+'/>');
		$.each(attributes, function(key, value) {
			$(node).attr(key, value);
		});
		classes = classes || [];
		$.each(classes, function(key, value) {
			$(node).addClass(value);
		});
		if (text != undefined)
			$(node).html(text);
		return node;
	},

	wrapAlert: function(content, type, dismissable) {
		var classes = ['alert'];
		if (type)
			classes.push('alert-'+type)
		if (dismissable)
			classes.push('alert-dismissable');
		var node = tools.createHtmlNode('div', '', {}, classes);
		if (dismissable) {
			var button = tools.createHtmlNode('button', '×', {'type': 'button', 'data-dismiss': 'alert', 'aria-hidden': 'true'}, ['close']);
			$(node).append(button);
		}
		return $(node).append(content);
	},


	getCSRF: function() {

		return $('[name="csrfmiddlewaretoken"]').first().val();

	},

	getAjaxLoaderHtml: function() {
		return '<div class="ajax-loader"></div>';
	},



	inherit: function(childConstructor, parentConstructor){
		var TempConstructor = function(){};
		TempConstructor.prototype = parentConstructor.prototype; // Inherit parent prototype chain

		childConstructor.prototype = new TempConstructor(); // Create buffer object to prevent assignments directly to parent prototype reference.
		// childConstructor.prototype.constructor = childConstructor; // Reset the constructor property back the the child constructor (currently set to TempConstructor )
	},



	Binder: function(cb_scope, set_callback, get_callback, init_val) {
		this._cb_scope = cb_scope;
		this._set_callback = set_callback;
		this._get_callback = get_callback;
		this._value = init_val || 0; // will be set 

		this.set = function(val) {
			this._value = val;
			if (this._set_callback)
				this._set_callback.call(this._cb_scope || this);
		};
		this.get = function() {
			if (this._get_callback)
				this._get_callback.call(this._cb_scope || this);
			return this._value;
		};
	},



	// create getter callback function for property
	getter: function(obj, prop, get) {
	  if (Object.defineProperty)
	    return Object.defineProperty(obj, prop, {enumerable: true, configurable: true, get: get});
	  if (Object.prototype.__defineGetter__)
	    return obj.__defineGetter__(prop, get);

	  throw new Error("browser does not support getters");
	},


	// create setter callback function for property
	setter: function(obj, prop, set) {
	  if (Object.defineProperty)
	    return Object.defineProperty(obj, prop, {enumerable: true, configurable: true, set: set});
	  if (Object.prototype.__defineSetter__)
	    return obj.__defineSetter__(prop, set);

	  throw new Error("browser does not support setters");
	},



	// watch read/write actions on object properties and runs onGet/onSet callbacks
	watch: function(obj, prop, val, onSet, onGet) {

		// console.log('creating watcher for ' + prop + ' with init val ' + val);

		if (val)
			obj['_'+prop] = val;
		
		tools.getter(obj, prop, function() {
			// console.log('watcher:' + prop + ' getter: ' + obj['_'+prop]);
			if (onGet)
				onGet.call(obj, obj['_'+prop]);
			return obj['_'+prop];
		});

		tools.setter(obj, prop, function(val) {
			obj['_'+prop] = val;
			// console.log('watcher:' + prop + ' setter: ' + obj['_'+prop]);
			if (onSet)
				onSet.call(obj, val);
		});

	},



	// bind html node text with object property and synchronize changes between them
	// (like bidirectional watcher)
	bind: function(obj, prop, node) {
		
		// console.log('binding for ' + prop);

		obj['_'+prop] = $(node).text();

		tools.getter(obj, prop, function() {
			// console.log('binder:' + prop + ' getter: ' + obj['_'+prop]);
			return obj['_'+prop];
		});

		tools.setter(obj, prop, function(val) {
			obj['_'+prop] = val;
			// console.log('binder:' + prop + ' setter: ' + obj['_'+prop]);
			$(node).html(val);
		});

		$(node).on('DOMSubtreeModified', function() {
			// console.log('DOM modiffied, updating ' + prop);
			obj['_'+prop] = $(node).text();
		});

	},

};