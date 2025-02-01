from .connection import SessionLocal
from .models.crud import create_user, get_users
from .connection import init_db

# Инициализируем БД
init_db()




if __name__ == "__main__":
    # Пример использования
    with SessionLocal() as db:
        # Добавляем нового пользователя
        # user = create_user(db, tg_id=123456789, name="Иван", phone="+79991112233", city="Москва", code="ABCD1234")
        # print(f"Добавлен пользователь: {user.name} ({user.phone})")

        # Выводим всех пользователей
        users = get_users(db)
        for user in users:
            print(f"{user.id}: {user.name} ({user.phone})")
