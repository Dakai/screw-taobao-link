import pyperclip
import re
import time
import requests
import re

# Define the regex pattern to match the URLs
url_pattern = re.compile(r"(http:\/\/e\.tb\.cn\/[^\s]+|https:\/\/m\.tb\.cn\/[^\s]+)")

url_pattern_item = re.compile(r"(https:\/\/item\.taobao\.com\/item\.htm[^\s]*)")


# Store the last clipboard content to avoid repeated processing
last_clipboard = ""

try:
    print("Monitoring clipboard... Press Ctrl+C to stop.")
    while True:
        # Get the current clipboard content
        clipboard_content = pyperclip.paste()

        # Check if the clipboard content has changed
        if clipboard_content != last_clipboard:
            last_clipboard = clipboard_content

            # Try to match the URL pattern
            url_match = url_pattern.search(clipboard_content)
            url_match_item = url_pattern_item.search(clipboard_content)

            if url_match:
                share_link = url_match.group(0)
                print(f"Matched URL: {share_link}")
                response = requests.get(share_link)
                html_content = response.text
                pattern = re.compile(r"var url = '([^']+)'")
                match = pattern.search(html_content)
                if match:
                    js_url = match.group(1)
                    # print("URL found in JavaScript:", js_url)
                else:
                    print("URL not found.")
                match = re.search(
                    r"(https://item.taobao.com/item.htm\?id=\d+)|(https://\w+\.taobao.com)",
                    js_url,
                )
                if match:
                    short_url = match.group(1) if match.group(1) else match.group(2)
                    # push short_url to clipboard
                    pyperclip.copy(short_url)
                    print("Short URL copied:", short_url)
                else:
                    print("URL pattern not found.")
            else:
                print("No matching URL found in clipboard.")

            if url_match_item:
                share_link = url_match_item.group(0)
                print(f"Matched URL: {share_link}")
                long_pattern = (
                    r"https://item\.taobao\.com/item\.htm\?.*?id=(\d+).*?skuId=(\d+)"
                )
                match = re.search(long_pattern, share_link)
                if match:
                    # Constructing the URL from matched groups
                    extracted_url = f"https://item.taobao.com/item.htm?id={match.group(1)}&skuId={match.group(2)}"
                    pyperclip.copy(extracted_url)
                    print("Extracted URL copied:", extracted_url)
                else:
                    print("No match found")

        # Sleep for a short duration before checking the clipboard again
        time.sleep(1)  # Check every second to avoid excessive CPU usage

except KeyboardInterrupt:
    print("\nStopped monitoring clipboard.")
