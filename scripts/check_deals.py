
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "GrizeLiAkcijeBot/0.1"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def number(value):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None


def allowed(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False

    robots_url = (
        f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    )
    try:
        response = SESSION.get(robots_url, timeout=12)
        if response.status_code == 404:
            return True
        if response.status_code != 200:
            return False

        robots = RobotFileParser()
        robots.parse(response.text.splitlines())
        return robots.can_fetch(USER_AGENT, url)
    except requests.RequestException:
        return False


def check_product(source):
    url = source.get("url", "")
    regular = number(source.get("regular_price"))
    low30 = number(source.get("lowest_30d"))

    if not regular or regular <= 0:
        return None

    if not allowed(url):
        print("Preskoceno:", url)
        return None

    try:
        response = SESSION.get(url, timeout=20)
        response.raise_for_status()

        if urlparse(response.url).hostname != urlparse(url).hostname:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        for script in soup.select(
            'script[type="application/ld+json"]'
        ):
            try:
                data = json.loads(script.string or script.get_text())
            except (ValueError, TypeError):
                continue

            nodes = data if isinstance(data, list) else [data]
            expanded = []

            for node in nodes:
                if isinstance(node, dict):
                    expanded.append(node)
                    graph = node.get("@graph", [])
                    if isinstance(graph, list):
                        expanded.extend(graph)

            for item in expanded:
                if not isinstance(item, dict):
                    continue

                types = item.get("@type", [])
                if isinstance(types, str):
                    types = [types]
                if "Product" not in types:
                    continue

                offers = item.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}

                if not isinstance(offers, dict):
                    continue

                if offers.get("priceCurrency") != "EUR":
                    continue

                sale = number(offers.get("price"))
                if not sale or sale >= regular:
                    continue

                discount = (regular - sale) / regular * 100

                if discount < 15:
                    continue

                if low30 and (low30 - sale) / low30 * 100 < 15:
                    continue

                image = item.get("image")
                if isinstance(image, list):
                    image = image[0] if image else None
                if not isinstance(image, str):
                    image = None

                return {
                    "title": item.get("name", ""),
                    "store": source.get("store", ""),
                    "category": source.get("category", "Ostalo"),
                    "regular_price": round(regular, 2),
                    "sale_price": round(sale, 2),
                    "discount_pct": round(discount, 2),
                    "lowest_30d": low30,
                    "image_url": image,
                    "availability": str(
                        offers.get("availability", "")
                    ).split("/")[-1],
                    "url": url,
                    "checked_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                }

    except requests.RequestException as error:
        print("Greska:", error)

    return None


def main():
    sources = json.loads(
        (ROOT / "sources.json").read_text(encoding="utf-8")
    )

    deals = []

    for source in sources.get("products", []):
        result = check_product(source)
        if result:
            deals.append(result)
        time.sleep(2)

    output = {
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "deals": deals
    }

    target = ROOT / "data" / "deals.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("Pronadeno ponuda:", len(deals))


if __name__ == "__main__":
    main()
