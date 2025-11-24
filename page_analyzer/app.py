import os

from flask import Flask
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


@app.get("/")
def index():
    return "Hello, Hexlet Page Analyzer!"
