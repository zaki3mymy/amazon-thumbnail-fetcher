import base64
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from html.parser import HTMLParser
from logging import getLogger

logger = getLogger(__name__)
log_level = os.getenv("LOGLEVEL")
if log_level:
    logger.setLevel(log_level)
else:
    logger.setLevel("INFO")


def search_in_amazon(keyword: str) -> str:
    k = urllib.parse.quote_plus(keyword)
    url = f"https://www.amazon.co.jp/s?k={k}"

    try:
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req) as res:
            html = res.read().decode("utf-8")
            logger.debug("html: %s", html)
            return html
    except urllib.error.HTTPError as e:
        raise e


class SearchResultParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag != "img":
            return

        class_ = attrs.get("class")
        if class_ == "s-image":
            url = attrs.get("src")
            self.url = url
            return

    def get_image_url(self):
        return self.url


def parse_image_url(html: str) -> str:
    parser = SearchResultParser()
    parser.feed(html)
    parser.close()

    url = parser.get_image_url()
    return url


Content = namedtuple("Content", ["image", "content_type"])


def fetch_image(url: str) -> Content:
    try:
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req) as res:
            headers = res.info()
            content_type = headers.get("Content-Type")
            body = res.read()
            body = base64.b64encode(body).decode("utf-8")
            logger.debug("base64 encoded image: %s", body)
            return Content(body, content_type)
    except urllib.error.HTTPError as e:
        raise e


def lambda_function(event, context):
    query = event.get("queryStringParameters")
    if not query or not query.get("keyword"):
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "text/plain",
            },
            "body": "Keyword is not set.",
            "isBase64Encoded": False,
        }

    keyword = query["keyword"]
    logger.info(f"keyword: {keyword}")

    html = search_in_amazon(keyword)

    url = parse_image_url(html)
    logger.info(f"image url: {url}")

    content = fetch_image(url)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content.content_type,
        },
        "body": content.image,
        "isBase64Encoded": True,
    }
