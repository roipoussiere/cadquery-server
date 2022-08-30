import { Viewer } from './vendor/three-cad-viewer.esm.js';

const container = document.getElementById('cad_view');

let options = {};
let viewer = build_viewer();
let model = [ {}, {} ];

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
	const viewer = new Viewer(container, options, () => {});
	viewer.trimUI(["axes", "axes0", "grid", "ortho", "more", "help"], false);
	return viewer;
}

function render(_model) {
	model = _model
	console.log('new model loaded:', model);
	viewer.clear();
	const [ shapes, states ] = model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function update_model(module_name, object_var) {
	fetch(`json?module=${ module_name }&object=${ object_var }`)
		.then(response => response.json())
		.then(model => render(model))
		.catch(error => console.log(error));
}

window.addEventListener('resize', event => {
	viewer = build_viewer();
	render(model);
});

export { update_model };
