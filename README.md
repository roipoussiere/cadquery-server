# CadQuery server

A web server used to render 3d models from CadQuery code loaded dynamically.

It has been created for the [Cadquery VSCode extension](https://open-vsx.org/extension/roipoussiere/cadquery), but can be used as standalone.

Because the CadQuery module is loaded when starting the web server and the scripts are loaded dynamically by request, it has a fast response time.

Example usage in the VSCode extension:

![](./images/screenshot.png)

Please note that the web server is intended for personal use and it's absolutely not safe to open it to a public network.

## Installation

    pip install cq-server

## Usage

### Starting the server

Once installed, the `cq-server` command should be available on your system:

CLI options:

- `-p`, `--port`: Server port (default: 5000);
- `-d`, `--dir`: Path of the directory containing CadQuery scripts (default: ".");
- `-m`, `--module`: Default module (default: "main");
- `-o`, `--object`: Default rendered object variable name (default: "result");
- `-f`, `--format`: Default output format (default: "json").

This list might not be up to date, please use `-h` to list all options.

Example:

    cq-server -p 5000 -d ./examples -m box -o result

This command will run the server on the port `5000`, load the `box.py` python file in the `./examples` directory and render the CadQuery model named `result`. These two last options can be overridden by url parameters if necessary.

### Writing a CadQuery code

Example:

```py
import cadquery as cq

model = cq.Workplane("XY").box(1, 2, 3)
```

Please read the [CadQuery documentation](https://cadquery.readthedocs.io/en/latest/) for more details about the CadQuery library.

### Using the web server

Once the server is started, go to its url (ie. `http://127.0.0.1`).

Optional url parameters:

- `module`: name of module to load (default: defined in the `--module` cli option);
- `object`: variable name of object to render (default: defined in the `--object` cli option).

example: `http://127.0.0.1?module=box&object=result`).

Note that the `/json` endpoint is used internally and can be used for advanced use. It takes same parameters but returns the model as a threejs json object.
