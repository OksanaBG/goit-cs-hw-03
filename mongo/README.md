# Mongo Cats CRUD (PyMongo)


## Швидкий старт
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env 
python main.py
```

## Можливості
- Вивести всі записи
- Знайти кота за іменем
- Оновити вік за іменем
- Додати характеристику до `features` за іменем (без дублювань)
- Видалити запис за іменем
- Видалити всі записи

## Примітки з безпеки
- Не комітьте справжній MONGODB_URI у репозиторій.
- Для MongoDB Atlas обмежте доступ за IP.
- Тримайте унікальний індекс на полі `name`.
