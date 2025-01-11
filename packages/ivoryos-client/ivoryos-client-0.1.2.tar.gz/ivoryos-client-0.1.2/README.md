# ivoryOS Client

[ivoryOS](https://gitlab.com/heingroup/ivoryos) client automates the generation of client-side APIs based on server-defined robotic control script. 
It mirrors the control Python code features but sending command through HTTP request to the ivoryOS backend (where the actual robotic communication are happening) that receives the info and execute the actual control methods.

## Features

- **Dynamic Interface Generation**: Automatically generates Python classes and methods to match server-side API definitions.

## Installation

```bash
pip install git+https://gitlab.com/heingroup/ivoryos
```

## usage
in terminal, use ivoryos-client + ivoryos server url
```bash
ivoryos-client http://localhost:8000
```
this will create a Python script `generated_classes.py` with all API instances created.

```Python
from example import *
```

## Example 
classes generated ([generated_classes.py](example/generated_classes.py)) for abstract_sdl.py in [SDL examples](https://gitlab.com/heingroup/ivoryos/-/tree/main/example/sdl_example)
