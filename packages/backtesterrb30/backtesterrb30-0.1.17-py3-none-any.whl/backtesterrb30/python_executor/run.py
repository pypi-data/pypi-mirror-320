import os

from backtesterrb30.libs.utils.module_loaders import import_executor_module
from backtesterrb30.libs.utils.run_service import run_service

here = os.getcwd()
strategy_path = os.getenv("STRATEGY_PATH")
strategy_file = os.getenv("STRATEGY_FILE")
executor_class_name = os.getenv("EXECUTOR_CLASS_NAME")


microservice_name = "python_executor"
module = import_executor_module(strategy_path, strategy_file, executor_class_name)
run_service(microservice_name, module)
