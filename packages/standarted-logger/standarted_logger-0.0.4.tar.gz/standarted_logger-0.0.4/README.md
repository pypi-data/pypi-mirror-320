## Logger that can be used as a standard logger for various packages in case of further logs parsing

### Sample usage

```
from standarted_logger.logger import Logger
logger = Logger.get_logger("my_module")

logger.info("output_text")
```

Expected output:
```
2025-01-14 11:49:19,316 - my_module - INFO - <module> - output_text
```

### Usage with log levels
```
import logging
from standarted_logger.logger import Logger

logger = Logger.get_logger("my_module", log_level=logging.INFO)
logger.debug("output_text")
```
This will not print anything, since debug_level is set to INFO. The log level by default is DEBUG.

### Logging to file
```
from standarted_logger.logger import Logger

logger = Logger.get_logger("my_module", log_dir="logs")
logger.debug("output_text")
```
Will create directory named "logs" at your script folder and a file my_module.log within it