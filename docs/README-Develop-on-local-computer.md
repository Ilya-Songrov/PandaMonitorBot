

## Develop on local computer

#### How to run in terminal:
```bash
python3.10 -m venv ./venv
source venv/bin/activate
python --version # Python 3.10.9
pip3.10 install -r requirements.txt
python3.10 main.py --help
```


#### Додавання нових функцій:
1. **Нові команди**: Додайте в `src/handlers/command_handlers.py`
2. **Нові монітори**: Створіть файл в `src/monitors/`
3. **Нові утиліти**: Додайте в `src/utils/`


#### Структура проєкту
```bash
PandaMonitorBot/
├── bot.py                 # Головний файл запуску
├── src/
│   ├── bot_manager.py     # Менеджер бота
│   ├── handlers/          # Обробники команд
│   │   ├── __init__.py
│   │   └── command_handlers.py
│   ├── monitors/          # Модулі моніторингу
│   │   ├── __init__.py
│   │   └── computer_monitor.py
│   └── utils/             # Утиліти
│       ├── __init__.py
│       ├── decorators.py  # Декоратори авторизації
│       └── system_info.py # Системна інформація
├── config/
│   └── settings.py        # Налаштування
├── requirements.txt       # Python залежності
├── Dockerfile            # Docker конфігурація
├── docker-compose.yml    # Docker Compose
├── .env.example          # Приклад змінних середовища
├── build-and-run-bot.sh  # Скрипт збірки та запуску
└── README.md
```
