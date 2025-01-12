# streamlit-extented

streamlit-extented — это простое расширение для работы с базами данных через pyodbc.

## Установка



pip install streamlit-extented

## Использование



from streamlit_extented import perform_query

connection_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=user;PWD=pass"
query = "SELECT * FROM my_table"
result = perform_query(connection_str, query, fetch_results=True, return_json=True)
print(result)