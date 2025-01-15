# Hierarchical logging in yaml format.

![PyPI](https://img.shields.io/pypi/v/nrt-logging?color=blueviolet&style=plastic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nrt-logging?color=greens&style=plastic)
![PyPI - License](https://img.shields.io/pypi/l/nrt-logging?color=blue&style=plastic)
![PyPI - Downloads](https://img.shields.io/pypi/dd/nrt-logging?style=plastic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nrt-logging?color=yellow&style=plastic)
[![Coverage Status](https://coveralls.io/repos/github/etuzon/nrt-logging/badge.svg)](https://coveralls.io/github/etuzon/pytohn-nrt-logging)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/etuzon/python-nrt-logging?style=plastic)
![GitHub last commit](https://img.shields.io/github/last-commit/etuzon/python-nrt-logging?style=plastic)
[![DeepSource](https://deepsource.io/gh/etuzon/python-nrt-logging.svg/?label=active+issues&token=3pUgM1IEwZG6Gpuc065dKDxM)](https://deepsource.io/gh/etuzon/python-nrt-logging/?ref=repository-badge)

Hierarchical logging help to group logs that are related to the same code flow.

Log style can be styled in Yaml format or in Line format.

### Examples:

#### Output in YAML style

```Python
from nrt_logging.logger import NrtLogger
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import ManualDepthEnum

NAME_1 = 'TEST1'
NAME_2 = 'TEST2'


class Child:
    __logger: NrtLogger

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)

    def child_1(self):
        self.__logger.info('Child 1')
        self.child_2()

    def child_2(self):
        self.__logger.info('Child 2')


class Parent:
    MSG_1 = 'MSG_1'
    MSG_2 = 'MSG_2'
    MSG_3 = 'MSG_3'
    INCREASE_MSG = 'INCREASE_MSG'
    DECREASE_MSG = 'DECREASE_MSG'

    __logger: NrtLogger
    __child: Child

    def __init__(self):
        self.__logger = logger_manager.get_logger(NAME_1)
        self.__child = Child()

    def a1(self):
        self.__logger.warn(self.MSG_1)
        self.__child.child_1()

    def a2_manual(self):
        self.__logger.info(self.MSG_2)
        self.__logger.increase_depth()
        self.__logger.info(self.INCREASE_MSG)
        self.__logger.decrease_depth()
        self.__logger.info(self.DECREASE_MSG)
        self.__logger.error(self.MSG_1)
        self.a1()

    def a3_manual(self):
        self.__logger.info(self.MSG_2)
        self.__logger.increase_depth()
        self.__logger.info(self.INCREASE_MSG)
        self.__logger.decrease_depth()
        self.__logger.info(self.DECREASE_MSG)
        self.__logger.error(self.MSG_3)

    def a4_manual(self):
        self.__logger.info(self.MSG_1)
        self.__logger.info(self.INCREASE_MSG, ManualDepthEnum.INCREASE)
        self.__logger.info(self.DECREASE_MSG, ManualDepthEnum.DECREASE)
        self.__logger.error(self.MSG_2)
```

```Python
from examples.demo_classes.demo_classes import NAME_1, Parent
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


def logging_style(log_style: LogStyleEnum):
    sh = ConsoleStreamHandler()
    sh.style = log_style
    logger = logger_manager.get_logger(NAME_1)
    logger.add_stream_handler(sh)
    p = Parent()
    p.a1()


def logging_line_style():
    logging_style(LogStyleEnum.LINE)


def logging_yaml_style():
    logging_style(LogStyleEnum.YAML)


logging_yaml_style()
```

Output
```YAML
---
date: 2022-10-31 17:59:04.653084
log_level: WARN
path: demo_classes.py.Parent
method: a1
line_number: 38
message: MSG_1
children:
  - date: 2022-10-31 17:59:04.655071
    log_level: INFO
    path: demo_classes.py.Child
    method: child_1
    line_number: 16
    message: Child 1
    children:
      - date: 2022-10-31 17:59:04.656137
        log_level: INFO
        path: demo_classes.py.Child
        method: child_2
        line_number: 20
        message: Child 2
```

#### Output in LINE style

```YAML
- log: 2022-10-31 18:16:54.033735 [WARN] [demo_classes.py.Parent.a1:38] MSG_1
  children:
    - log: 2022-10-31 18:16:54.034660 [INFO] [demo_classes.py.Child.child_1:16] Child 1
      children:
        - log: 2022-10-31 18:16:54.036723 [INFO] [demo_classes.py.Child.child_2:20] Child 2
```

```Python
from nrt_logging.log_level import LogLevelEnum
from nrt_logging.logger_manager import logger_manager
from nrt_logging.logger_stream_handlers import \
    ConsoleStreamHandler, LogStyleEnum


sh = ConsoleStreamHandler()
sh.log_level = LogLevelEnum.TRACE
sh.style = LogStyleEnum.LINE
logger = logger_manager.get_logger('NAME_1')
logger.add_stream_handler(sh)

logger.info('main level log')
logger.increase_depth()
logger.info('child 1')
logger.increase_depth()
logger.info('child 1_1')
logger.decrease_depth()
logger.info('child 2')
logger.decrease_depth()
logger.info('continue main level')
```

Output
```YAML
- log: 2022-10-31 18:18:34.520544 [INFO] [manual_hierarchy_line_logging_1.py.<module>:13] main level log
  children:
    - log: 2022-10-31 18:18:34.522606 [INFO] [manual_hierarchy_line_logging_1.py.<module>:15] child 1
      children:
        - log: 2022-10-31 18:18:34.523784 [INFO] [manual_hierarchy_line_logging_1.py.<module>:17] child 1_1
- log: 2022-10-31 18:18:34.524810 [INFO] [manual_hierarchy_line_logging_1.py.<module>:19] child 2
- log: 2022-10-31 18:18:34.525864 [INFO] [manual_hierarchy_line_logging_1.py.<module>:21] continue main level
```

### Config file

log_manager config file in YAML style.<br>
Configure loggers and stream handlers.

parameters are inherited. Parameters that are deeper in YAML file will be taken.

```YAML
log_level: WARN
date_format: '%Y-%m-%d %H:%M:%S'
loggers:
  - name: TEST1
    style: yaml
    log_line_template: '[$log_level$] <$date$> $message$'
    stream_handlers:
      - type: console
        style: line
      - type: file
        file_path: logs/log_test_1.txt
        log_level: DEBUG
        style: line
        date_format: '%Y'
        log_line_template: 'Test1 $date$ $message$'
  - name: TEST2
    style: yaml
    stream_handlers:
      - type: file
        file_path: logs/log_test_2.txt
        log_level: ERROR
        date_format: '%Y'
        log_yaml_elements:
          ['log_level', 'date', 'message']
```

```Python
from nrt_logging.logger_manager import logger_manager


CONFIG_FILE_PATH = './config/config1.yaml'

logger_manager.set_config(file_path=CONFIG_FILE_PATH)
```

Wiki: https://github.com/etuzon/nrt-logging/wiki

