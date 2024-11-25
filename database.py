from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from os import environ

load_dotenv()

MYSQL_USER = environ.get('MYSQL_USER')
MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD')
MYSQL_HOST = environ.get('MYSQL_HOST')
MYSQL_DB = environ.get('MYSQL_DB')

params = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4"
engine = create_engine(params)


def retrieve_records(sql_string):
    records_list = []

    with engine.connect() as conn:
        result = conn.execute(text(sql_string))

        for row in result.all():
            row_to_dict = row._asdict()
            records_list.append(row_to_dict)

    return records_list

def insert_user(usr, pwd):
    pwd = str(generate_password_hash(pwd))

    query = f"INSERT INTO users (user_name, user_password) values ('{usr}', '{pwd}')"

    with engine.connect() as conn:
        result = conn.execute(text(query))

    return result


print(insert_user('tsw581', 'my_secret_password'))