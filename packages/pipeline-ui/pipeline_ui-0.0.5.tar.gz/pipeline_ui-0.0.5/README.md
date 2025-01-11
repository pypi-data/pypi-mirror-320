# PipelineUI
PipelineUI is a python package that allow you to create your own comfyui style backend for your ML code.

with pipelineUI we expose two new decorator that can be added to your python project to create graphical interface.

# how to install

`pip install pipeline-ui`

locally
`git clone`
`uv pip install -e .`

# Here is an example

create a example.py file

python
```
from pipeline_ui import PipelineUI

pui = PipelineUI()

@pui.node()
def add_numbers(a: int, b: int) -> int:
    return a + b

@pui.node()
def multiply(a: int, b: int) -> int:
    return a + b

@pui.workflow()
def math_workflow(a: int, b: int) -> int:
    c = add_numbers(a, b)
    d = multiply(c, d)
    return d
```
start with `python example.py` this start an web interface at localhost:8114
where you can see your code graphically

# commands
pui start pipeline_ui/examples/simple.py

pui publish pipeline_ui/examples/simple.py