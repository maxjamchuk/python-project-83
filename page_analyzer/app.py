import os
import requests
from bs4 import BeautifulSoup

from urllib.parse import urlparse

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
import validators

from page_analyzer import db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def urls_create():
    url_raw = request.form.get("url", "").strip()
    errors: dict[str, str] = {}

    if not url_raw:
        errors["url"] = "URL обязателен"
    elif len(url_raw) > 255:
        errors["url"] = "URL не должен превышать 255 символов"
    elif not validators.url(url_raw):
        errors["url"] = "Некорректный URL"

    if errors:
        return (
            render_template("index.html", errors=errors, url_value=url_raw),
            422,
        )

    parsed = urlparse(url_raw)
    if not parsed.scheme or not parsed.netloc:
        errors["url"] = "Некорректный URL"
        return (
            render_template("index.html", errors=errors, url_value=url_raw),
            422,
        )

    normalized_url = f"{parsed.scheme}://{parsed.netloc}"

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

    h1_text = None
    title_text = None
    description_text = None

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text(strip=True):
            h1_text = h1_tag.get_text(strip=True)

        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            title_text = title_tag.get_text(strip=True)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description_text = meta_desc.get("content").strip()

    except Exception:
        pass

    db.create_check(
        url_id=id,
        status_code=status_code,
        h1=h1_text,
        title=title_text,
        description=description_text,
    )

    flash("Страница успешно проверена", "success")
    return redirect(url_for("urls_show", id=id))


