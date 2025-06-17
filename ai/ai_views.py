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
    "database": "bulk_orders_db"
}

def get_sql_query(user_request):
    prompt = f"""
    Generate a MySQL query for the following request: '{user_request}'.
    The table name is 'bulk_orders', and it contains the following columns:
    id, full_name, company_name, email, phone, lemon_chutney, pulihora_chutney, sorakaya_chutney,
    tomato_chutney, shipping_city, shipping_pincode, additional_message, created_at, source.
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
        result_data = []

        if query.strip().lower().startswith("select"):
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result_data = {"columns": columns, "rows": rows[:10]}
        else:
            cursor.execute(query)
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
