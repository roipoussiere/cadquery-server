import { Viewer } from './vendor/three-cad-viewer.esm.js';

const container = document.getElementById('cad_view');
const options = {
	cadWidth: window.innerWidth - 8,
	height: window.innerHeight - 44,
	treeWidth: window.innerWidth > 400 ? window.innerWidth / 3 : 200,
	glass: true
};
const viewer = new Viewer(container, options, () => {});
viewer.trimUI(["axes", "axes0", "grid", "ortho", "more", "help"], false);

function render(model) {
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

export { update_model };
