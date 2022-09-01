# CadQuery server

A web server used to render 3d models from CadQuery code loaded dynamically.

It has been created for the [Cadquery VSCode extension](https://open-vsx.org/extension/roipoussiere/cadquery), but can be used as standalone.

Because the CadQuery module is loaded when starting the web server and the scripts are loaded dynamically by request, it has a fast response time.

Example usage in the VSCode extension:

![](./images/screenshot.png)

Please note that the web server is intended for personal use and it's absolutely not safe to open it to a public network.

## Installation

If you already have CadQuery installed on your system:

    pip install cadquery-server

If you want to install both cq-server and CadQuery:

    pip install 'cadquery-server[cadquery]'

This may take a while.

## Usage

### Starting the server

Once installed, the `cq-server` command should be available on your system:

Positional arguments:

- `dir`: Path of the directory containing CadQuery scripts (default: ".").

Options:

- `-p`, `--port`: Server port (default: 5000);
- `-m`, `--module`: Default module to load (default: "main").

This list might not be up to date, please use `-h` to list all options.

Example:

    cq-server ./examples -p 5000 -m box

This command will run the server on the port `5000` and load the `box.py` python file in the `./examples` directory. Note that the `-m` option can be overridden by url parameter if necessary (see below).

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

### Using the web server

Once the server is started, go to its url (ie. `http://127.0.0.1`).

Optional url parameters:

- `module`: name of module to load (default: defined in the `--module` cli option);

example: `http://127.0.0.1?module=box`).

Note that the `/json` endpoint is used internally and can be used for advanced use. It takes same parameters but returns the model as a threejs json object.
