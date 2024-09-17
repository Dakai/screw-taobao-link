from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

# HTML template for the frontend
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Parser</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        input, button { padding: 10px; margin: 5px; width: 80%; }
        button { cursor: pointer; }
        #result { margin-top: 20px; color: green; }
    </style>
    <script>
        function parseLink() {
            const shareContent = document.getElementById('shareLink').value;
            let urlMatch = shareContent.match(/(http:\/\/e\.tb\.cn\/[^\s]+)/);
            if (urlMatch && urlMatch[0]) {
                const shareLink = urlMatch[0];

                fetch('/parse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ link: shareLink })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('result').innerText = 'Final Link: ' + data.final_link;
                        navigator.clipboard.writeText(data.final_link).then(() => {
                            alert('Final link copied to clipboard!');
                        });
                    } else {
                        document.getElementById('result').innerText = 'Error: ' + data.error;
                    }
                })
                .catch(error => {
                    document.getElementById('result').innerText = 'Error: ' + error;
                });
            }
        }

        function retrieveClipboardContent() {
            navigator.clipboard.readText().then(text => {
                document.getElementById('shareLink').value = text;
            }).catch(err => {
                console.error('Failed to read clipboard contents: ', err);
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            retrieveClipboardContent().then(() => {
                parseLink(); // Automatically parse the link after retrieving clipboard content
            });
            document.getElementById('shareLink').addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault(); // Prevents the default action (like a newline in textarea)
                    parseLink(); // Call the parse function
                }
            });
        });
    </script>
</head>
<body>
    <h1>Share Link Parser</h1>
    <input type="text" id="shareLink" placeholder="Paste the share link here..." />
    <button onclick="parseLink()">Parse and Copy</button>
    <div id="result"></div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/parse", methods=["POST"])
def parse():
    data = request.json
    share_link = data.get("link")
    if not share_link:
        return jsonify({"success": False, "error": "No link provided"}), 400

    try:
        # Make a request to the share link to get the final redirected URL
        response = requests.get(share_link, allow_redirects=True)
        print(response.url)
        html_content = response.text
        pattern = re.compile(r"var url = '([^']+)'")
        match = pattern.search(html_content)
        if match:
            js_url = match.group(1)
            print("URL found in JavaScript:", js_url)
        else:
            print("URL not found.")

        match = re.search(r"(https://item.taobao.com/item.htm\?id=\d+)", js_url)
        if match:
            short_url = match.group(1)
            print("Short URL:", short_url)
        else:
            print("URL pattern not found.")

        return jsonify({"success": True, "final_link": short_url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
