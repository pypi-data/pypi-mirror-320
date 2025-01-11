WorkflowBuilder

Introduction
-------------------------
WorkflowBuilder is a tool for building and executing workflows. It allows users to define configuration classes, task classes, and workflows to create complex workflows, which can be easily managed and executed.

Installation
-------------------------
Ensure you have Python 3.6+ installed, then install WorkflowBuilder via pip:
pip install workflow_builder

Usage Example
-------------------------
### Configuration Class
First, define a configuration class to store the configuration information needed by the workflow. Here we define a configuration class named `ExampleConfiguration` that contains a `greeting` field.
python
from workflow_builder import configclass, Configuration

# Parameters specify aliases
@configclass('example', 'example_config')
class ExampleConfiguration(Configuration):
    greeting: str

### Task Classes
Next, define task classes. Each task class must inherit from the `Task` class and implement the `preprocess` and `work` methods.

#### ExampleTask1
`ExampleTask1` is a specific task class that retrieves `ExampleConfiguration` from the workflow's configuration manager before execution and returns a dictionary containing the processing results in the `work` method.
python
class ExampleTask1(Task):
    def __init__(self, task_config: TaskConfig):
        task_config.name = ''
        # task_config.asynchronize = True
        self.config = None

    def preprocess(self, workflow: Workflow):
        self.config = workflow.config_manager[ExampleConfiguration]

    def work(self, workflow):
        return {
            'example_task1': self.config.greeting + ' World'
        }

#### ExampleTask
`ExampleTask` is another task class that receives output from `ExampleTask1` in its `work` method and prints it.
python
class ExampleTask(Task):
    def __init__(self):
        ...

    def preprocess(self, workflow: Workflow):
        ...

    def work(self, example_task1):
        print(example_task1)

### Workflow
Finally, add the task classes to the workflow and create and execute the pipeline.
python
tasks = [
    ExampleTask1,
    ExampleTask
]

wf = Workflow(tasks)

# Manually specify configs
# workflow = Workflow(tasks, configs=configs)

# Load toml from the current directory by default:
# workflow = Workflow(tasks, configs_path='.')

pipeline = wf.create_pipeline()
# Execute pipeline
pipeline()

Configuration File
-------------------------
By default, the workflow loads toml configuration files from the current directory. You can specify other paths using the `configs_path` parameter.

### test.toml Example
[example]
greeting = "Hello"

Running
-------------------------
Ensure the configuration file exists, then run the following command to execute the workflow:
python your_script.py