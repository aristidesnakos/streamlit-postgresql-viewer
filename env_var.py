import os
from dotenv import load_dotenv
import tempfile

load_dotenv()

ENV = os.getenv("ENV")

AWS_DB_HOST=os.getenv("AWS_DB_HOST")
AWS_DB_NAME=os.getenv("AWS_DB_NAME")
AWS_DB_USER=os.getenv("AWS_DB_USER")
AWS_DB_PASSWORD=os.getenv("AWS_DB_PASSWORD")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

OUTPUT_DIR = os.path.join(
    tempfile.gettempdir(),
    'output'
)

os.makedirs(OUTPUT_DIR, exist_ok=True)