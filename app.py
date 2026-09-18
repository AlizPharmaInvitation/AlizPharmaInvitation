from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import os, re

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
ORIGINAL = os.path.join(BASE, "invitation-original.png")
OUTPUT = os.path.join(BASE, "personalized-invitation.png")

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aliz Pharma Invitation</title>
<style>
body{margin:0;background:#f5f1e8;font-family:Arial,sans-serif;text-align:center;color:#173b2b}
.box{max-width:430px;margin:40px auto;padding:25px;background:white;border-radius:18px;box-shadow:0 5px 25px #0002}
h1{margin-top:0}
input{width:90%;padding:15px;border:1px solid #bbb;border-radius:10px;font-size:18px;box-sizing:border-box}
button{margin-top:15px;padding:14px 25px;border:0;border-radius:10px;background:#173b2b;color:white;font-size:17px}
img{width:100%;margin-top:20px;border-radius:10px}
.download{display:inline-block;margin-top:15px;padding:13px 20px;background:#b28a35;color:white;text-decoration:none;border-radius:10px}
</style>
</head>
<body>
<div class="box">
<h1>ALÍZ PHARMA</h1>
<p>Grand Opening Invitation</p>
<form method="POST">
<input name="name" placeholder="Enter guest name" maxlength="60" required>
<br>
<button type="submit">Generate Invitation</button>
</form>
{% if image %}
<img src="/invitation?t={{ stamp }}">
<a class="download" href="/invitation" download="Aliz-Pharma-Invitation.png">Download Invitation</a>
{% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    image = False
    if request.method == "POST":
        name = request.form.get("name","").strip()
        if name:
            generate(name)
            image = True
    import time
    return render_template_string(HTML, image=image, stamp=time.time())

@app.route("/invitation")
def invitation():
    return send_file(OUTPUT, mimetype="image/png")

def generate(name):
    im = Image.open(ORIGINAL).convert("RGB")
    draw = ImageDraw.Draw(im)

    # Guest-name area — will be adjusted after visual test
    # Elegant italic + bold guest name
    font_paths = [
        "/system/fonts/Roboto-BoldItalic.ttf",
        "/system/fonts/Roboto-Italic.ttf",
        "/system/fonts/Roboto-Bold.ttf",
        "/system/fonts/Roboto-Regular.ttf"
    ]

    font = None
    size = 42

    for fp in font_paths:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, size)
            break

    if font is None:
        font = ImageFont.load_default()

    text = name

    # Automatically reduce size for long names
    max_width = 760

    while size >= 28:
        for fp in font_paths:
            if os.path.exists(fp):
                test_font = ImageFont.truetype(fp, size)
                break
        else:
            test_font = font

        bbox = draw.textbbox((0, 0), text, font=test_font)
        tw = bbox[2] - bbox[0]

        if tw <= max_width:
            font = test_font
            break

        size -= 2

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (im.width - tw) // 2

    # Place name ABOVE the original underline
    y = 395

    draw.text(
        (x, y),
        text,
        font=font,
        fill="#173b2b",
        stroke_width=1,
        stroke_fill="#173b2b"
    )

    im.save(OUTPUT, "PNG")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
