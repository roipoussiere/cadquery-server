'use strict';

const tcv = window.CadViewer;
const cad_view_dom = document.getElementById('cad_view');

let data = {};
let options = {};
let modules_name = [];
let viewer = null;
let timer = null;
let sse = null;


function init_sse() {
	sse = new EventSource('events');
	sse.addEventListener('file_update', event => {
		render(JSON.parse(event.data));
	})
	sse.onerror = error => {
		if (sse.readyState == 2) {
			setTimeout(init_sse, 1000);
		}
	};	
}

function update_size_options() {
	options.height = window.innerHeight - 44;
	options.treeWidth = window.innerWidth > 400 ? window.innerWidth / 3 : 200;
	options.cadWidth = window.innerWidth - (options.glass ? 8 : options.treeWidth + 10);
}

function load_camera_position() {
	if (viewer != null) {
		options.position = viewer.getCameraPosition();
		options.quaternion = viewer.getCameraQuaternion();
		options.target = viewer.getCameraTarget();
		options.zoom = viewer.getCameraZoom();
	} else {
		options.up = 'Z'
	}
}

function init_viewer(_options, _modules_name) {
	options = _options;
	modules_name = _modules_name;
	update_size_options();
	load_camera_position();

	viewer = new tcv.Viewer(cad_view_dom, options, () => {});
	add_modules_dropdown();

	if ('hideButtons' in options) {
		viewer.trimUI(options.hideButtons, false);
	}
}

function show_error() {
	document.title = 'error | CadQuery Server';
	document.getElementById('cqs_index').style.display = 'none';

	document.getElementById('cqs_error_message').innerText = data.error;
	document.getElementById('cqs_stacktrace').innerText = data.stacktrace;
	document.getElementById('cqs_stacktrace').style.display = data.stacktrace ? 'block' : 'none';

	document.getElementById('cqs_error').style.display = 'block';
}

function show_index() {
	document.title = 'index | CadQuery Server';
	document.getElementById('cqs_error').style.display = 'none';

	if (sse) {
		window.history.pushState('/', '', window.location.origin);
	}

	const modules_list_dom = document.getElementById('cqs_modules_list');

	while (modules_list_dom.firstChild) {
        modules_list_dom.removeChild(modules_list_dom.firstChild);
    }

	for(let module_name of modules_name) {
		const item_dom = document.createElement('div');
		item_dom.classList.add('cqs_module_item');

		const text_dom = document.createElement('p');
		text_dom.innerText = module_name;
		if (sse) {
			item_dom.append(text_dom);
			item_dom.classList.add('cqs_module_item_link');
			item_dom.addEventListener('click', event => render_from_name(module_name));
	
		} else {
			const img_dom = document.createElement('img');
			img_dom.setAttribute('src', `png/${ module_name }.png`);
			img_dom.addEventListener('click', event => render_from_name(module_name));
			img_dom.classList.add('cqs_module_item_link');

			const info_dom = document.createElement('div');
			const stl_link_dom = document.createElement('a');
			stl_link_dom.setAttribute('href', `stl/${ module_name }.stl`)
			stl_link_dom.innerText = 'get stl';
			info_dom.append(text_dom);
			info_dom.append(stl_link_dom);

			item_dom.append(img_dom);
			item_dom.append(info_dom);
		}

		modules_list_dom.append(item_dom);
	}

	document.getElementById('cqs_no_modules').style.display = modules_name.length == 0 ? 'block' : 'none';
	document.getElementById('cqs_index').style.display = 'block';
}

function show_model() {
	document.title = data.module_name + ' | CadQuery Server';
	document.getElementById('cqs_error').style.display = 'none';
	document.getElementById('cqs_index').style.display = 'none';

	if (sse) {
		const url = new URL(window.location.href);
		url.searchParams.set('m', data.module_name);
		window.history.pushState(url.pathname, '', url.href);
	}

	const [ shapes, states ] = data.model;
	const [ group, tree ] = viewer.renderTessellatedShapes(shapes, states, options);
	viewer.render(group, tree, states, options);
}

function render(_data) {
	data = _data;
	let cameraSettings

	if ( ! viewer) {
		init_viewer(options, modules_name);
	} else {
		try {
			cameraSettings = viewer.getCameraLocationSettings();
		} catch(error) { console.log(error) }
		viewer.clear();
	}

	update_modules_dropdown();

	if ('error' in data) {
		show_error();
	} else if (data.module_name) {
		show_model();
		try {
			viewer.setCameraLocationSettings(cameraSettings.position, cameraSettings.quaternion, cameraSettings.target, cameraSettings.zoom);
		} catch(error) { console.log(error) }
	} else {
		show_index();
	}
}

function render_from_name(module_name) {
	if(sse) {
		fetch(`json?m=${ module_name }`)
			.then(response => response.json())
			.then(_data => render(_data))
			.catch(error => console.error(error));
	} else {
		render(modules[module_name]);
	}
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

function update_modules_dropdown() {
	const modules_dropdown_dom = document.getElementById('modules_dropdown');

	while (modules_dropdown_dom.firstChild) {
        modules_dropdown_dom.removeChild(modules_dropdown_dom.firstChild);
    }

	const option_dom = document.createElement('option');
	option_dom.setAttribute('selected', 'selected');
	option_dom.innerText = 'Index page';
	modules_dropdown_dom.appendChild(option_dom);

	for(let module_name of modules_name) {
		const option_dom = document.createElement('option');
		if (module_name == data.module_name) {
			option_dom.setAttribute('selected', 'selected');
		}
		option_dom.innerText = module_name;
		modules_dropdown_dom.appendChild(option_dom);
	}

	modules_dropdown_dom.style.display = data.module_name == undefined ? 'none' : 'inline';
}

function add_modules_dropdown() {
	const modules_dropdown_dom = document.createElement('select');
	modules_dropdown_dom.id = 'modules_dropdown';

	modules_dropdown_dom.addEventListener('change', event => {
		if (event.target.value == 'Index page') {
			render({});
		} else {
			render_from_name(event.target.value);
		}		
	});

	document.getElementsByClassName('tcv_cad_toolbar')[0].prepend(modules_dropdown_dom);
}

