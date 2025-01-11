import abc
import inspect
from typing import Type, Iterable

from workflow_builder.configuration import ConfigManager

_TASK_CONFIG = '__TASK_CONFIG__'
_WORK_FUNCTION = 'work'

class TaskConstructorFunctionException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class TaskInitializeException(Exception):
    ...

class NotSupportedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def match_argument(_shared_parameters, name: str, _type):
    if name and (r := _shared_parameters.get(name)) is not None:
        return r
    if _type is None:
        return None
    type_matched = [p for p in _shared_parameters.items() if isinstance(p[1], _type)]
    if len(type_matched) == 0:
        raise ValueError(f"'{name}' is not a valid argument")
    if len(type_matched) == 1:
        return type_matched[0][1]
    if len(type_matched) > 1:
        name_matched = [p for p in type_matched if p[0] == name]
        if len(name_matched) == 0:
            raise ValueError(f"'{name}' is not a valid argument")
        if len(name_matched) == 1:
            return name_matched[0][1]
        if len(name_matched) > 1:
            raise ValueError(f"'{name}' is not a valid argument")

class TaskConfig:
    def __init__(self, name='', depends=None, asynchronous=False,
                 args_inject=True, name_inject=True,
                 position_inject=True):
        if depends is None:
            self.depends = []
        self.name = name
        self.asynchronous = asynchronous
        self.args_inject=args_inject
        if self.args_inject:
            self.name_inject = name_inject
            self.position_inject = position_inject


class Task(abc.ABC):
    @abc.abstractmethod
    def work(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def preprocess(self, workflow):
        ...

    def wrap(self):
        task_config: TaskConfig = getattr(self, _TASK_CONFIG)
        if task_config.args_inject:
            func = self.work
            _sig = inspect.signature(func).parameters
            def wrapped_func(*args, _shared_parameters=None, **kwargs):
                if _shared_parameters is None:
                    _shared_parameters = {}
                params = {}
                position = 0
                for _name, _param in _sig.items():
                    injected = _param.default if _param.default is not inspect.Parameter.empty else \
                        match_argument(_shared_parameters, _name if task_config.name_inject else None,
                                       _param.annotation if _param.annotation != inspect.Parameter.empty else None)
                    if task_config.position_inject:
                        if injected is None and len(args) > position:
                            params[_name] = args[position]
                        else:
                            params[_name] = injected
                        position += 1
                params.update(kwargs)
                return func(**params)
            setattr(self, _WORK_FUNCTION, wrapped_func)



class Pipeline:
    def __init__(self, task_instances: Iterable[Task], workflow,
                 shared_parameters=None, asynchronous=False):
        self.asynchronous = asynchronous
        self.shared_parameters = {'workflow': workflow}
        if shared_parameters:
            self.shared_parameters.update(shared_parameters)
        task_mesh = []
        temp = []
        for task_instance in task_instances:
            task_config: TaskConfig = getattr(task_instance, _TASK_CONFIG)
            task_instance.preprocess(workflow)
            temp.append(task_instance)
            if task_config.asynchronous:
                continue
            task_mesh.append(tuple(temp))
            temp = []
        self.task_mesh = tuple(task_mesh)

    def __call__(self, *args, **kwargs):
        for group in self.task_mesh:
            if not self.asynchronous and len(group) > 1:
                raise NotSupportedException('asynchronous')
            else:
                # TODO async support
                ...
            result = group[0].work(_shared_parameters=self.shared_parameters)
            if result:
                self.shared_parameters.update(result)


class Workflow:
    def __init__(self, tasks: Iterable[Type[Task]], /, configs_path='.',
                 configs=None, console_arguments=None):
        self.task_instances = []
        self.config_manager = ConfigManager(config_files=configs_path)
        self.config_manager.load_configs()
        if configs is not None:
            self.config_manager.config_data.update(configs)

        for task in tasks:
            default_task_config = TaskConfig()
            try:
                params = inspect.signature(task.__init__).parameters.items()
                if len(params) > 2:
                    raise TaskConstructorFunctionException('Illegal constructor')
                elif len(params) == 2:
                    first = False
                    for _, _param in params:
                        if not first:
                            first = True
                            continue
                        if _param.annotation != inspect.Parameter.empty:
                            if not isinstance(default_task_config, _param.annotation):
                                raise TaskConstructorFunctionException('Illegal constructor')
                    task_instance = task(default_task_config)
                else:
                    task_instance = task()
                if default_task_config.name == '':
                    default_task_config.name = task.__name__
                setattr(task_instance, _TASK_CONFIG, default_task_config)
                task_instance.wrap()

                self.task_instances.append(task_instance)
            except Exception as e:
                raise TaskInitializeException from e

    def create_pipeline(self) -> Pipeline:
        return Pipeline(self.task_instances, self)