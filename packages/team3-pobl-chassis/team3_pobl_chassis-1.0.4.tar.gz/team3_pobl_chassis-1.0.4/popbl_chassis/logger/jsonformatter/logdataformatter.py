import json
import logging
import time


class LogDataFormatter(logging.Formatter):
    def format(self, record):
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

        log_record = {
            "timestamp": created_time,
            "level": record.levelname,
            "message": record.getMessage(),
            "filename": record.filename,  # Nombre del fichero
        }

        return json.dumps(log_record)