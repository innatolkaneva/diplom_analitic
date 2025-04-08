import os
from dotenv import load_dotenv

def get_env_var(key, default = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Переменная {key} не найдена в .env!")
    return value

load_dotenv()

BOT_TOKEN = get_env_var("TG_BOT_TOKEN")

CHART_TYPES = {
    "line": "Линейный график",
    "bar": "Столбчатый график",
    "scatter": "Точечный график",
    "hist": "Гистограмма",
    "box": "Ящик с усами",
    "heatmap": "Тепловая карта",
    "pie": "Круговая диаграмма"
}

COLOR_OPTIONS = {
    "blue": "Синий",
    "green": "Зеленый",
    "red": "Красный",
    "cyan": "Голубой",
    "magenta": "Пурпурный",
    "yellow": "Желтый",
    "black": "Черный"
}

USER_DATA = {}