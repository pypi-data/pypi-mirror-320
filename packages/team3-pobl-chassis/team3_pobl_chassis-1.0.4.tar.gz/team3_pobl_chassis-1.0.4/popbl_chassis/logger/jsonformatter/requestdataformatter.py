import json
import logging
import time


class RequestDataFormatter(logging.Formatter):
    def format(self, record):
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

        data = getattr(record, 'data', {})

        log_record = {
            "timestamp": created_time,
            "level": record.levelname,
            "message": record.getMessage(),
            "client_ip": data.get('client_ip', 'unknown'),
            "method": data.get('method', 'unknown'),
            "path": data.get('path', 'unknown'),
            "status_code": data.get('status_code', 'unknown'),
            "user_agent": data.get('user_agent', 'unknown'),
            "headers": data.get('headers', 'unknown'),
            "body_size": data.get('body_size', 'unknown'),
            "packet_size": data.get('packet_size', 'unknown'),
            "body_content": data.get('body_content', 'unknown'),
        }

        return json.dumps(log_record)