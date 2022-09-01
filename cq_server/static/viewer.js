import { Viewer } from './vendor/three-cad-viewer.esm.js';

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
	const viewer = new Viewer(cad_view_dom, options, () => {});
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

	document.getElementById('cad_error_message').innerText = message;
	document.getElementById('cad_error_stacktrace').innerText = stacktrace;
	document.getElementById('cad_error_stacktrace').style.display = stacktrace ? 'block' : 'none';
	document.getElementById('cad_error').style.display = 'block';
}

function render(_data) {
	if ('error' in _data) {
		error(_data.error, _data.stacktrace)
		return
	}
	document.getElementById('cad_error').style.display = 'none';

	data = _data
	viewer.clear();
	const [ shapes, states ] = data.model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function init_viewer(module_name, _options) {
	options = _options;
	update_size_options();
	viewer = build_viewer();

	fetch(`json?module=${ module_name }`)
		.then(response => response.json())
		.then(model => render(model))
		.catch(error => console.log(error));
}

function build_error_dom() {
	const dom_error = document.createElement('div');
	dom_error.id = 'cad_error';
	dom_error.style.display = 'none';

	const dom_error_title = document.createElement('h2');
	dom_error_title.innerText = 'Oops! An error occured.'
	dom_error.appendChild(dom_error_title);

	const dom_error_message = document.createElement('p');
	dom_error_message.id = 'cad_error_message';
	dom_error.appendChild(dom_error_message);

	const dom_error_stacktrace = document.createElement('pre');
	dom_error_stacktrace.id = 'cad_error_stacktrace';
	dom_error.appendChild(dom_error_stacktrace);

	cad_view_dom.parentNode.insertBefore(dom_error, null);
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

export { init_viewer };
