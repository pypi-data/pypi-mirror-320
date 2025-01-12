import sqlite3
import datetime
from datetime import timedelta


class SecuritySystem:
    def __init__(self, db_path='security.db', allowed_numbers_file='allowed_numbers.txt'):
        """
        Инициализация системы безопасности
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        self.allowed_numbers = self._load_allowed_numbers(allowed_numbers_file)

    def phone_exists(self, phone: str) -> bool:
        """Проверяет, существует ли номер телефона в базе"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE phone = ?', (phone,))
            return cursor.fetchone() is not None
        except sqlite3.Error:
            return False

    def link_user_to_phone(self, user_id: int, phone: str) -> tuple[bool, str]:
        """Привязывает существующий номер к новому пользователю"""
        try:
            cursor = self.conn.cursor()

            # Проверяем, не занят ли номер другим пользователем
            cursor.execute(
                'SELECT user_id FROM users WHERE phone = ?', (phone,))
            existing_user = cursor.fetchone()

            if existing_user and existing_user[0] != user_id:
                return False, "Этот номер уже зарегистрирован другим пользователем"

            # Проверяем, есть ли номер в списке разрешенных
            if phone not in self.allowed_numbers:
                return False, "Номер не найден в базе разрешенных номеров"

            # Привязываем номер к пользователю
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, phone) 
                VALUES (?, ?)
            ''', (user_id, phone))
            self.conn.commit()
            return True, "Регистрация успешна"

        except sqlite3.Error as e:
            return False, f"Ошибка при привязке номера: {str(e)}"

    def _create_tables(self):
        """Создание необходимых таблиц"""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER UNIQUE,
                phone TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        self.conn.commit()

    def _load_allowed_numbers(self, filename):
        """Загрузка разрешенных номеров"""
        try:
            with open(filename, 'r') as file:
                return {line.strip() for line in file if line.strip()}
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Создаю новый файл...")
            with open(filename, 'w') as file:
                # Можно добавить несколько тестовых номеров
                default_numbers = ['+79776000056']
                file.write('\n'.join(default_numbers))
            return set(default_numbers)

    def register_user(self, user_id: int, phone: str) -> tuple[bool, str]:
        """
        Регистрация пользователя

        Returns:
            tuple: (успех, сообщение)
        """
        # Проверка формата номера
        if not self._is_valid_phone(phone):
            return False, "Неверный формат номера телефона"

        # Проверка номера в списке разрешенных
        if phone not in self.allowed_numbers:
            return False, "Номер не найден в базе разрешенных номеров"

        cursor = self.conn.cursor()

        # Проверка, не занят ли номер другим пользователем
        cursor.execute('SELECT user_id FROM users WHERE phone = ?', (phone,))
        existing_user = cursor.fetchone()
        if existing_user and existing_user[0] != user_id:
            return False, "Этот номер уже зарегистрирован другим пользователем"

        # Проверка, есть ли у пользователя другой номер
        cursor.execute('SELECT phone FROM users WHERE user_id = ?', (user_id,))
        user_phone = cursor.fetchone()
        if user_phone and user_phone[0] != phone:
            return False, "Вы уже зарегистрированы с другим номером телефона"

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, phone) 
                VALUES (?, ?)
            ''', (user_id, phone))
            self.conn.commit()
            return True, "Регистрация успешна"
        except sqlite3.Error as e:
            return False, f"Ошибка при регистрации: {str(e)}"

    def _is_valid_phone(self, phone: str) -> bool:
        """Проверка валидности номера"""
        if not isinstance(phone, str):
            return False

        # Убираем '+' если он есть
        if phone.startswith('+'):
            phone = phone[1:]

        # Убираем '7' или '8' в начале если есть
        if phone.startswith('7') or phone.startswith('8'):
            phone = phone[1:]

        # Проверяем что остались только цифры и их 10 (код страны уже убрали)
        return phone.isdigit() and len(phone) == 10

    def check_spam(self, user_id: int) -> bool:
        """Проверка на спам"""
        cursor = self.conn.cursor()
        time_window = datetime.datetime.now() - timedelta(seconds=10)

        cursor.execute('''
            SELECT COUNT(*) FROM actions 
            WHERE user_id = ? AND timestamp >= ?
        ''', (user_id, time_window))

        count = cursor.fetchone()[0]
        return count >= 5

    def log_action(self, user_id: int) -> bool:
        """Логирование действия"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO actions (user_id) VALUES (?)', (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def set_role(self, user_id: int, role: str) -> bool:
        """Установка роли пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET role = ? WHERE user_id = ?',
                           (role, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_role(self, user_id: int) -> str:
        """Получение роли пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'unauthorized'

    def get_user_info(self, user_id: int) -> dict:
        """Получение информации о пользователе"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, phone, role, registration_date 
            FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'phone': result[1],
                'role': result[2],
                'registration_date': result[3]
            }
        return {}

    def is_registered(self, user_id: int) -> bool:
        """Проверка регистрации пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

    def close(self):
        """Закрытие соединения"""
        self.conn.close()