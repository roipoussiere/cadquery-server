# CadQuery server

A web server that executes a given CadQuery code and returns the generated model as a threejs object.

It has been created for the [Cadquery VSCode extension](https://open-vsx.org/extension/roipoussiere/cadquery), but could fit other needs.

## Installation

    pip install cq-server

## Usage

### Starting the server

Once installed, the `cq-server` command should be available on your system:

CLI options:

- `-p`, `--port`: server port (default: 5000)

Example:

    cq-server -p 5000

### Writing a CadQuery code

The Python script must contain the `show()` method.

Example:

```py
import cadquery as cq

model = cq.Workplane("XY").box(1, 2, 3)

show(model)
```

Note that the `import cadquery as cq` part is optional (`cadquery` is already imported at server start), but can be useful to enable syntax check and code completion in your IDE.

Please read the [CadQuery documentation](https://cadquery.readthedocs.io/en/latest/) for more details about the CadQuery library.

### Using the server

Once the server is started, a CadQuery Python code can be send in a `POST` request payload.

Example:

    curl -X POST --data-binary "@./examples/test.py" 127.0.0.1:5000

It should return the model as a threejs object.
