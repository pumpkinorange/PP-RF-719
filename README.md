## Установка и запуск

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/your-username/your-project.git
    cd your-project
    ```

2.  Создайте виртуальное окружение:
    ```bash
    # Для Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Для Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4.  Запустите проект:
    ```bash
    python 719.py
    ```

## Использование:
  1. Введите ссылку на скачивание 'Скачать только действующие XLSX'
  2. Введите необходимые ОКПД-2
  3. Скрипт отфильтрует все организации по данному ОКПД-2, удалит лишние столбцы и заменит длинные названия организаций на сокращенные.
     Например, (АКЦИОНЕРНОЕ ОБЩЕСТВО - АО).
  
