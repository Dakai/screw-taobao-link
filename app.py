from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import requests
import re
import logging
from typing import Optional, Tuple, Union
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_ORIGINS = ["https://admin.thecopierparts.com"]
TIMEOUT_SECONDS = 10
TAOBAO_URL_PATTERN = re.compile(
    r"(https://item\.taobao\.com/item\.htm\?id=\d+)|(https://\w+\.taobao\.com)"
)
JS_URL_PATTERN = re.compile(r"var url = '([^']+)'")

app = Flask(__name__)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
CORS(
    app,
    resources={r"/parse": {"origins": ALLOWED_ORIGINS}},
)


def validate_url(url: str) -> bool:
    """Validate if the provided URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_taobao_url(html_content: str) -> Optional[str]:
    """Extract Taobao URL from HTML content."""
    try:
        # Find the JavaScript URL
        js_match = JS_URL_PATTERN.search(html_content)
        if not js_match:
            logger.warning("JavaScript URL pattern not found in HTML content")
            return None

        js_url = js_match.group(1)
        logger.info(f"URL found in JavaScript: {js_url}")

        # Extract the Taobao URL
        taobao_match = TAOBAO_URL_PATTERN.search(js_url)
        if not taobao_match:
            logger.warning("Taobao URL pattern not found in JavaScript URL")
            return None

        short_url = taobao_match.group(1) or taobao_match.group(2)
        logger.info(f"Extracted Taobao URL: {short_url}")
        return short_url

    except Exception as e:
        logger.error(f"Error extracting Taobao URL: {str(e)}")
        return None


def create_error_response(message: str, status_code: int) -> Tuple[Response, int]:
    """Create a standardized error response."""
    logger.error(f"Error response: {message} (Status: {status_code})")
    return jsonify({"success": False, "error": message}), status_code


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse() -> Union[Response, Tuple[Response, int]]:
    # Validate request data
    data = request.json
    if not data:
        return create_error_response("No data provided", 400)

    share_link = data.get("link")
    if not share_link:
        return create_error_response("No link provided", 400)

    if not validate_url(share_link):
        return create_error_response("Invalid URL format", 400)

    try:
        # Make request to the share link
        response = session.get(share_link, allow_redirects=True, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        # Extract Taobao URL
        short_url = extract_taobao_url(response.text)
        if not short_url:
            return create_error_response("Failed to extract Taobao URL", 404)

        logger.info(f"Successfully processed request for URL: {share_link}")
        return jsonify({"success": True, "final_link": short_url})

    except requests.Timeout:
        return create_error_response("Request timed out", 504)
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return create_error_response("Failed to fetch the URL", 502)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return create_error_response("Internal server error", 500)


if __name__ == "__main__":
    # In production, set debug=False
    app.run(host="0.0.0.0", port=5000, debug=True)
