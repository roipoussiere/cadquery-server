function updateJson(module_name, object_var) {
	fetch(`json?module=${ module_name }&object=${ object_var }`)
		.then(response => response.json())
		.then(json => {
			document.getElementById('json').innerHTML = JSON.stringify(json, null, 4);
		})
		.catch(error => {
			console.log(error);
		});
}
