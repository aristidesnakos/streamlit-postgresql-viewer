import psycopg2
from env_var import AWS_DB_HOST, AWS_DB_NAME, AWS_DB_USER, AWS_DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=AWS_DB_HOST,
        database=AWS_DB_NAME,
        user=AWS_DB_USER,
        password=AWS_DB_PASSWORD
    )

def close_connection(connection):
    if connection:
        connection.close()