from bs4 import BeautifulSoup


def extract_seo_data(html: str) -> tuple[str | None, str | None, str | None]:
    h1_text: str | None = None
    title_text: str | None = None
    description_text: str | None = None

    try:
        soup = BeautifulSoup(html, "html.parser")

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

    return h1_text, title_text, description_text
