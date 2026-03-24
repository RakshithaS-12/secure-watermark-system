from flask import Flask, render_template, request
import os
import sqlite3
import datetime
import watermark_utils

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
WATERMARK_FOLDER = "watermarked"

# Create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(WATERMARK_FOLDER, exist_ok=True)

# ---------------- DATABASE SETUP ----------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
filename TEXT,
hash TEXT
)
""")

conn.commit()
conn.close()

# ---------------- HOME PAGE ----------------

@app.route("/", methods=["GET", "POST"])
def index():

    message = None

    if request.method == "POST":

        file = request.files["file"]

        if file:

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)

            file.save(filepath)

            # Generate SHA256 hash
            file_hash = watermark_utils.generate_hash(filepath)

            # Generate watermark text
            watermark_text = "User_" + datetime.datetime.now().strftime("%Y%m%d%H%M")

            watermarked_path = os.path.join(WATERMARK_FOLDER, file.filename)

            # Embed watermark
            watermark_utils.embed_watermark(filepath, watermark_text, watermarked_path)

            # Store hash in database
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO documents VALUES (?,?)",
                (file.filename, file_hash)
            )

            conn.commit()
            conn.close()

            message = "Watermark embedded and document secured successfully."

    return render_template("index.html", message=message)

# ---------------- VERIFY DOCUMENT ----------------

@app.route("/verify", methods=["POST"])
def verify():

    file = request.files["verify_file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(filepath)

    # Generate new hash
    new_hash = watermark_utils.generate_hash(filepath)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT hash FROM documents WHERE filename=?",
        (file.filename,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:

        original_hash = result[0]

        if original_hash == new_hash:
            status = "authentic"
        else:
            status = "tampered"

        return render_template(
            "verify_result.html",
            original_hash=original_hash,
            new_hash=new_hash,
            status=status
        )

    else:

        return render_template(
            "verify_result.html",
            original_hash="Not Found",
            new_hash=new_hash,
            status="tampered"
        )

# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)