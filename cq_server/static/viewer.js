import { Viewer } from './vendor/three-cad-viewer.esm.js';

const cad_view_dom = document.getElementById('cad_view');

let options = {};
let viewer = build_viewer();
let data = {};

const event_source = new EventSource('events');
event_source.addEventListener('file_update', event => {
	render(JSON.parse(event.data));
})

function update_options() {
	options = {
		cadWidth: window.innerWidth - 8,
		height: window.innerHeight - 44,
		treeWidth: window.innerWidth > 400 ? window.innerWidth / 3 : 200,
		glass: true
	}
}

function build_viewer() {
	update_options();
	const viewer = new Viewer(cad_view_dom, options, () => {});
	viewer.trimUI(['axes', 'axes0', 'grid', 'ortho', 'more', 'help'], false);
	return viewer;
}

function error(message, stacktrace) {
	data = {
		error: message,
		stacktrace: stacktrace
	}

	console.log('error:', message);
	document.getElementById('cad_error_message').innerText = message;

	document.getElementById('cad_error_stacktrace').innerText = stacktrace;
	document.getElementById('cad_error_stacktrace').style.display = stacktrace ? 'block' : 'none';

	document.getElementById('cad_error').style.display = 'block';
}

function render(_model) {
	if ('error' in _model) {
		error(_model['error'], _model['stacktrace'])
		return
	}
	document.getElementById('cad_error').style.display = 'none';

	data = { model: _model }
	viewer.clear();
	const [ shapes, states ] = data.model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function update_model(module_name) {
	fetch(`json?module=${ module_name }`)
		.then(response => response.json())
		.then(model => render(model))
		.catch(error => console.log(error));
}

window.addEventListener('resize', event => {
	viewer = build_viewer();
	render(data);
});

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

window.addEventListener('DOMContentLoaded', () => {
	build_error_dom();
});

export { update_model };
