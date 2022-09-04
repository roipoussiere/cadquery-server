const tcv = window.CadViewer;

const cad_view_dom = document.getElementById('cad_view');
const event_source = new EventSource('events');

let data = {};
let options = {};
let modules_name = [];
let viewer = null;
let timer = null;

function update_size_options() {
	options.height = window.innerHeight - 44;
	options.treeWidth = window.innerWidth > 400 ? window.innerWidth / 3 : 200;
	options.cadWidth = window.innerWidth - (options.glass ? 8 : options.treeWidth + 10);
}

function init_viewer(_options, _modules_name) {
	options = _options;
	modules_name = _modules_name;

	update_size_options();
	viewer = new tcv.Viewer(cad_view_dom, options, () => {});
	add_modules_list();
	if ('hideButtons' in options) {
		viewer.trimUI(options.hideButtons, false);
	}
}

function error(message, stacktrace) {
	data = {
		error: message,
		stacktrace: stacktrace
	}

	document.getElementById('cqs_error_message').innerText = message;
	document.getElementById('cqs_stacktrace').innerText = stacktrace;
	document.getElementById('cqs_stacktrace').style.display = stacktrace ? 'block' : 'none';
	document.getElementById('cqs_error').style.display = 'block';
}

function render(_data) {
	if ('error' in _data) {
		error(_data.error, _data.stacktrace)
		return
	}
	document.getElementById('cqs_error').style.display = 'none';

	data = _data;
	document.title = data.module_name + ' | CadQuery Server';

	viewer.clear();
	const [ shapes, states ] = data.model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function render_from_name(module_name) {
	fetch(`json?m=${ module_name }`)
		.then(response => response.json())
		.then(_data => render(_data))
		.catch(error => console.error(error));
}

window.addEventListener('resize', () => {
	if (timer) {
		clearTimeout(timer);
	}
	timer = setTimeout(() => {
		viewer = init_viewer(options, modules_name);
		render(data);
	}, 500);
});

function add_modules_list() {
	const current_module_name = new URLSearchParams(window.location.search).get('m')

	if (current_module_name == undefined) {
		return;
	}

	select_dom = document.createElement('select');
	select_dom.name = 'modules_list';

	option_dom = document.createElement('option');
	option_dom.innerText = 'Index page';
	select_dom.append(option_dom);

	for(module_name of modules_name) {
		option_dom = document.createElement('option');
		if (module_name == current_module_name) {
			option_dom.setAttribute('selected', 'selected');
		}
		option_dom.innerText = module_name;
		select_dom.append(option_dom);
	}

	select_dom.addEventListener('change', event => {
		if (event.target.value == 'Index page') {
			window.location.href = '/';
		} else {
			render_from_name(event.target.value);
		}		
	});

	document.getElementsByClassName('tcv_cad_toolbar')[0].prepend(select_dom);
}

event_source.addEventListener('file_update', event => {
	render(JSON.parse(event.data));
})
