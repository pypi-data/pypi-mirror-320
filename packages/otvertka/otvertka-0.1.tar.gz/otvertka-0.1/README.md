# Otvertka

Набор простых функций для работы с данными в ClickHouse.

## Установка

```bash
pip install otvertka
```

## Использование

```python
from otvertka import fetch_data, get_table_info, get_dates_tuples

# Получить информацию о таблице
get_table_info('my_table')

# Выполнить SQL запрос
df = fetch_data('SELECT * FROM my_table LIMIT 10')

# Разбить временной интервал на периоды
dates = get_dates_tuples('2024-01-01', '2024-02-01', days_interval=7)
```

## Требования

- Python 3.7+
- Необходимые переменные окружения:
  - `CH_USER` - пользователь ClickHouse
  - `CH_PASSWORD` - пароль ClickHouse
  - `CH_HOST` - хост ClickHouse (по умолчанию: localhost)
  - `CH_PORT` - порт ClickHouse (по умолчанию: 8123)

## Лицензия

MIT 