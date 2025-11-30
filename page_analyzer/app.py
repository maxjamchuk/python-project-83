import os
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



@app.post("/urls/<int:id>/checks")
def url_checks_create(id: int):
    url = db.get_url(id)
    if url is None:
        abort(404)

    db.create_check(id)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("urls_show", id=id))
