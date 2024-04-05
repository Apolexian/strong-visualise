import logging
import psutil
import time

class BaseLogger:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler = logging.FileHandler(f"{self.__class__.__name__.lower()}.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

class RequestLogger(BaseLogger):
    def log_request(self, request):
        log_message = f"{request.method} {request.url}"
        self.logger.info(log_message)

class ServerLoadLogger(BaseLogger):
    def log_server_load(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        log_message = f"CPU Usage: {cpu_percent}% | Memory Usage: {memory_percent}%"
        self.logger.info(log_message)
        
    def start_logging(self, interval=60):
        while True:
            self.log_server_load()
            time.sleep(interval)