import psycopg2
DB_NAME = "bar"
DB_USER = "postgres"
DB_PASSWORD = "12"
DB_HOST = "localhost"
DB_PORT = "5432"
def create_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
def fetch_table_data(table_name):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return columns, rows
def fetch_inventory():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM GetInventory()")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return columns, rows
def fetch_order_receipt(order_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM GetOrderReceipt({order_id})")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return columns, rows
def add_record(table_name, values):
    connection = create_connection()
    cursor = connection.cursor()
    columns = ", ".join(values.keys())
    placeholders = ", ".join(["%s"] * len(values))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, list(values.values()))
    connection.commit()
    cursor.close()
    connection.close()
def edit_record(table_name, record_id, values):
    connection = create_connection()
    cursor = connection.cursor()
    set_values = ", ".join([f"{col} = %s" for col in values.keys()])
    query = f"UPDATE {table_name} SET {set_values} WHERE {table_name}_id = %s"
    cursor.execute(query, list(values.values()) + [record_id])
    connection.commit()
    cursor.close()
    connection.close()
def delete_record(table_name, record_id):
    connection = create_connection()
    cursor = connection.cursor()
    query = f"DELETE FROM {table_name} WHERE {table_name}_id = %s"
    cursor.execute(query, (record_id,))
    connection.commit()
    cursor.close()
    connection.close()
def fetch_order_total(order_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT SUM(quantity * price) FROM Order_Items WHERE order_id = {order_id}")
    total_amount = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return total_amount