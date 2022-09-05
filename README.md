# CadQuery Server

A web server used to render 3d models from CadQuery code loaded dynamically.

It has been created for the [Cadquery VSCode extension](https://open-vsx.org/extension/roipoussiere/cadquery), but can be used as standalone.

Example usage with Kate on the left and Firefox on the right:

![](./images/screenshot.png)

## About CadQuery Server

### Features

- fast response time
- built-in file-watcher
- live-reload
- use your favorite text editor or IDE
- display model on an external monitor or other device
- compatible with VSCode built-in browser

Please note that the web server is intended for personal use and it's absolutely not safe to open it to a public network.

### Functionning

CadQuery Server dynamically loads your CadQuery code and renders the model on the browser using [three-cad-viewer](https://github.com/bernhard-42/three-cad-viewer) (the same used in [jupyter-cadquery](https://github.com/bernhard-42/jupyter-cadquery)). It includes a file watcher that reloads the Python code and updates the web page when the file is updated.

This approach allows users to work on any IDE, and render the model on any web browser. It also allow them to display the model in an other monitor, or even in an other computer on the same local network (for instance a tablet on your desktop).

The project was originally started for the VSCode extension, but since it doesn't depend on VSCode anymore, it's now a project as it own.

### About CadQuery

From the [CadQuery readme](https://github.com/CadQuery/cadquery/blob/master/README.md):

> CadQuery is an intuitive, easy-to-use Python module for building parametric 3D CAD models. Using CadQuery, you can write short, simple scripts that produce high quality CAD models. It is easy to make many different objects using a single script that can be customized.

Read [CadQuery documentation](https://cadquery.readthedocs.io/en/latest/) for more information about CadQuery and its usage.

## Installation

### Create a virtual environment (recommended)

    python -m venv .venv
    source .venv/bin/activate

### Upgrade pip and setuptools

    pip install --upgrade pip setuptools

### Install with pip

If you already have CadQuery installed on your system:

    pip install cadquery-server

If you want to install both cq-server and CadQuery:

    pip install 'cadquery-server[cadquery]'

### Install with Docker

    docker pull cadquery/cadquery-server

Then add a volume and port when running the container. Typically:

    docker run -p 5000:5000 -v $(pwd)/examples:/data cadquery/cadquery-server

Where `examples` is in your current directory and contains CadQuery scripts.

### Install from sources

    git clone https://github.com/roipoussiere/cadquery-server.git
    cd cadquery-server

If you already have CadQuery installed on your system:

    pip install .

If you want to install both cq-server and CadQuery:

    pip install '.[cadquery]'

## Usage

### Starting the server

Once installed, the `cq-server` command should be available on your system.

It takes only one optional argument: the target, which can be a folder or a file. Defaults to the current directory (`.`).

Then the root endpoint (ie. `http://127.0.0.1`) will display:
- if `target` is a folder: an index page from which you can select a file to render;
- if `target` is a file: the root endpoint will render the corresponding file.

Server options:

- `-p`, `--port`: Server port (default: 5000);

Example:

    cq-server -p 8080 ./examples/box.py

This command will run the server on the port `8080`, then load and render `./examples/box.py`. The file to load can be overridden by url parameter if necessary (see below).

Use `cq-server -h` to list all available options.

### Exporting static html

You can use `-e` / `--export` cli option to obtain an html file that work as a standalone and doesn't require a running server.

### UI cli options

Other cli options are available to change the UI appearence:

- `--ui-hide`: a comma-separated list of buttons to disable, among: `axes`, `axes0`, `grid`, `ortho`, `more`, `help`;
- `--ui-glass`: activate tree view glass mode;
- `--ui-theme`: set ui theme, `light` or `dark` (default: browser config);
- `--ui-trackball`: set control mode to trackball instead orbit;
- `--ui-perspective`: set camera view to perspective instead orthogonal;
- `--ui-grid`: display a grid in specified axes (`x`, `y`, `z`, `xy`, etc.);
- `--ui-transparent`: make objects semi-transparent;
- `--ui-black-edges`: make edges black.

Example:

    cq-server --ui-hide ortho,more,help --ui-glass --ui-theme light --ui-grid xyz

### Writing a CadQuery code

CadQuery Server renders the model defined in the `show_object()` function (like in CadQuery Editor).

You **must** import it before from the `cq_server.ui` module, among with the `UI` class, which is used by the server to load the model.

Minimal working example:

```py
import cadquery as cq
from cq_server.ui import UI, show_object

show_object(cq.Workplane('XY').box(1, 2, 3))
```

Please read the [CadQuery documentation](https://cadquery.readthedocs.io/en/latest/) for more details about the CadQuery library.

### Using with the web server

Once the server is started, go to its url (ie. `http://127.0.0.1`).

Optional url parameters:

- `m`: name of an other module to load;

example: `http://127.0.0.1?m=box`).

Other endpoints:

- `/json?m=box`: returns the model as a threejs json object. Used internally to retrieve the model.
- `/html?m=box`: returns a static html page that doesn't require the CadQuery Server running.

### Using with VSCode

The web page can be displayed within VSCode IDE using [LivePreview extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server):

1. install the LivePreview VSCode extension;
2. `ctrl+shift+P` -> *Simple Browser: Show*;
3. update the url according to your running CadQuery server instance (ie. `127.0.0.1:5000`).

## About

- contact:
    - ping user `@roipoussiere` on channel `other-gui` in the CadQuery Discord;
    - [Mastodon](https://mastodon.tetaneutral.net/@roipoussiere);
- license: [MIT](./LICENSE);
- source: both on [Framagit](https://framagit.org/roipoussiere/cadquery-server) (Gitlab instance) and [Github](https://github.com/roipoussiere/cadquery-server);
- issue tracker: both on [Framagit](https://framagit.org/roipoussiere/cadquery-server/-/issues) and [Github](https://github.com/roipoussiere/cadquery-server/issues)
