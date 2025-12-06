import os
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from dotenv import load_dotenv

from page_analyzer import db
from page_analyzer.url_utils import is_valid_url, normalize_url
from page_analyzer.html_parser import extract_seo_data

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def urls_create():
    url_raw = request.form.get("url", "").strip()

    if not is_valid_url(url_raw):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    normalized_url = normalize_url(url_raw)

    existing = db.find_url_by_name(normalized_url)
    if existing:
        flash("Страница уже существует", "info")
        return redirect(url_for("urls_show", id=existing["id"]))

    new_id = db.insert_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("urls_show", id=new_id))


@app.get("/urls")
def urls_index():
    urls = db.get_urls()
    return render_template("urls/index.html", urls=urls)


@app.get("/urls/<int:id>")
def urls_show(id: int):
    url = db.get_url(id)
    if url is None:
        abort(404)

    checks = db.get_checks_for_url(id)
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:id>")
def url_checks_create(id: int):
    url = db.get_url(id)
    if url is None:
        abort(404)

    try:
        response = requests.get(url["name"], timeout=10)
        status_code = response.status_code
        response.raise_for_status()
    except requests.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("urls_show", id=id))

    h1_text, title_text, description_text = extract_seo_data(response.text)

    db.create_check(
        url_id=id,
        status_code=status_code,
        h1=h1_text,
        title=title_text,
        description=description_text,
    )

    flash("Страница успешно проверена", "success")
    return redirect(url_for("urls_show", id=id))
