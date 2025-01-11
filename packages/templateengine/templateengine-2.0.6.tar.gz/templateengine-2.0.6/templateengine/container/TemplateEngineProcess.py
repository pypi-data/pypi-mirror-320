import os
from pip_services4_container import ProcessContainer
from ..build import TemplateEngineFactory, StrategiesFactory, PlannersFactory, ToolsFactory, AIModelsFactory, ExecutorsFactory

class TemplateEngineProcess(ProcessContainer):
    def __init__(self):
        super(TemplateEngineProcess, self).__init__('templateengine-v2', 'Template engine process')
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config_path = os.path.join(script_dir, "config", "config.yml")

        self._factories.add(TemplateEngineFactory())
        self._factories.add(StrategiesFactory())
        self._factories.add(PlannersFactory())
        self._factories.add(ToolsFactory())
        self._factories.add(AIModelsFactory())
        self._factories.add(ExecutorsFactory())
