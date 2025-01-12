import pyodbc
import json

def perform_query(connect_str, query, fetch_results=True, return_json=False):
    """
    Подключается к базе данных через ODBC, выполняет запрос и возвращает результат (если требуется).
    
    Примеры строк подключения к БД:
    SQL Server: connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server_name;DATABASE=db_name;UID=user;PWD=password"
    MySQL: connection_string = "DRIVER={MySQL ODBC 8.0 Driver};SERVER=server_name;DATABASE=db_name;UID=user;PWD=password"

    :param connect_str: Строка подключения к базе данных.
    :param query: SQL-запрос для выполнения.
    :param fetch_results: Флаг, указывающий, нужно ли возвращать данные (True для SELECT).
    :param return_json: Флаг, указывающий, нужно ли возвращать данные в формате JSON (True).
    :return: Список с результатами запроса (для SELECT) или None (для других запросов).
    """
    try:
        # Подключение к базе данных
        conn = pyodbc.connect(connect_str)
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(query)

        # Если запрос требует возврата данных (например, SELECT)
        if fetch_results:
            data = cursor.fetchall()

            # Если нужно вернуть данные в JSON формате
            if return_json:
                # Получаем имена колонок
                columns = [column[0] for column in cursor.description]
                # Преобразуем данные в список словарей
                result = [dict(zip(columns, row)) for row in data]
                # Преобразуем список словарей в JSON
                return json.dumps(result, ensure_ascii=False, indent=4)
            else:
                return data

        # Если запрос не требует возврата данных (например, INSERT, UPDATE, DELETE)
        conn.commit()  # Подтвердить изменения
        return None
    except pyodbc.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        # Закрытие ресурсов
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as close_error:
            print(f"Ошибка при закрытии ресурсов: {close_error}")