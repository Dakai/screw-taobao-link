function parseLink() {
  const shareContent = document.getElementById('shareLink').value;
  //let urlMatch = shareContent.match(/(http:\/\/e\.tb\.cn\/[^\s]+)/);
  let urlMatch = shareContent.match(/(http:\/\/e\.tb\.cn\/[^\s]+|https:\/\/m\.tb\.cn\/[^\s]+)/);
  console.log(urlMatch);
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
            //alert('Final link copied to clipboard!');
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

const retrieveClipboardContent = async () => {
  return navigator.clipboard.readText().then(text => {
    document.getElementById('shareLink').value = text;
  }).catch(err => {
    console.error('Failed to read clipboard contents: ', err);
  });
}

document.addEventListener('DOMContentLoaded', () => {
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

