import os
import mysql.connector
from django.conf import settings
from django.shortcuts import render
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# MySQL config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "business_form"
}

def get_sql_query(user_request):
    schema_info = get_all_table_schemas()

    if "Database Error" in schema_info:
        return schema_info

    prompt = f"""
    Based on the following database schema:
    {schema_info}

    Generate a MySQL query for the request: "{user_request}".
    Only return the SQL query.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI Error: {e}"

def execute_query(query):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        result_data = {}

        cursor.execute(query)

        if cursor.description:  # Means the query returned rows (like SELECT, SHOW, etc.)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result_data = {"columns": columns, "rows": rows[:10]}
        else:
            conn.commit()
            result_data = {"message": "Query executed successfully."}

        cursor.close()
        conn.close()
        return result_data

    except mysql.connector.Error as e:
        return {"error": str(e)}


def db_agent_view(request):
    context = {}
    if request.method == "POST":
        user_request = request.POST.get("user_request")
        query = get_sql_query(user_request)
        context["generated_query"] = query

        if "error" not in query.lower():
            result = execute_query(query)
            context.update(result)

    return render(request, "dbagent/agent.html", context)


def get_all_table_schemas():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        schema_info = []

        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            schema_info.append(f"Table: {table}, Columns: {', '.join(column_names)}")

        cursor.close()
        conn.close()
        return "\n".join(schema_info)

    except mysql.connector.Error as e:
        return f"Database Error: {e}"
