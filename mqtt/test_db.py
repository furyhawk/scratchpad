from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL


import os
from dotenv import load_dotenv

load_dotenv()

HOSTNAME = os.getenv("DATABASE__HOSTNAME")
USERNAME = os.getenv("DATABASE__USERNAME")
PASSWORD = os.getenv("DATABASE__PASSWORD")
PORT = os.getenv("DATABASE__PORT")
DB = os.getenv("DATABASE__DB")

url = URL.create(
    drivername="postgresql",
    username=USERNAME,
    password=PASSWORD,
    host="db.furyhawk.lol",
    port=5432,
    database="default_db",
)

engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execution_options(stream_results=True).execute(
        text("select * from temperature")
    )
    for row in result:
        print(row)
        break
