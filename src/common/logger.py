import logging
import os

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Папка для логов
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Файл логов
log_file = os.path.join(logs_dir, "app.log")
file_handler = logging.FileHandler(log_file, encoding="utf-8")

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s | %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Консольный хэндлер
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
