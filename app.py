from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse():
    data = request.json
    share_link = data.get("link")
    if not share_link:
        return jsonify({"success": False, "error": "No link provided"}), 400

    try:
        # Make a request to the share link to get the final redirected URL
        response = requests.get(share_link, allow_redirects=True)
        # print(response.url)
        html_content = response.text
        pattern = re.compile(r"var url = '([^']+)'")
        match = pattern.search(html_content)
        if match:
            js_url = match.group(1)
            print("URL found in JavaScript:", js_url)
        else:
            print("URL not found.")
        match = re.search(
            r"(https://item.taobao.com/item.htm\?id=\d+)|(https://\w+\.taobao.com)",
            js_url,
        )
        # match = re.search(r"(https://item.taobao.com/item.htm\?id=\d+)", js_url)
        if match:
            # short_url = match.group(1)
            short_url = match.group(1) if match.group(1) else match.group(2)
            print("Short URL:", short_url)
        else:
            print("URL pattern not found.")

        return jsonify({"success": True, "final_link": short_url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
