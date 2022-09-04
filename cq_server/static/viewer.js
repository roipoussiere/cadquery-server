const tcv = window.CadViewer;

const cad_view_dom = document.getElementById('cad_view');
const event_source = new EventSource('events');

let data = {};
let options = {};
let viewer = null;
let timer = null;

function update_size_options() {
	options.height = window.innerHeight - 44;
	options.treeWidth = window.innerWidth > 400 ? window.innerWidth / 3 : 200;
	options.cadWidth = window.innerWidth - (options.glass ? 8 : options.treeWidth + 10);
}

function build_viewer() {
	update_size_options();
	const viewer = new tcv.Viewer(cad_view_dom, options, () => {});
	if ('hideButtons' in options) {
		viewer.trimUI(options.hideButtons, false);
	}
	return viewer;
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

	data = _data
	viewer.clear();
	const [ shapes, states ] = data.model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function init_viewer(module_name, _options) {
	fetch(`json?m=${ module_name }`)
		.then(response => response.json())
		.then(data => init_viewer_from_data(data, _options))
		.catch(error => console.log(error));
}

function init_viewer_from_data(_data, _options) {
	options = _options;
	viewer = build_viewer();
	render(_data);
}

window.addEventListener('resize', event => {
	if (timer) {
		clearTimeout(timer);
	}
	timer = setTimeout(() => {
		viewer = build_viewer();
		render(data);
	}, 500);
});

window.addEventListener('DOMContentLoaded', () => {
	build_error_dom();
});

event_source.addEventListener('file_update', event => {
	render(JSON.parse(event.data));
})
