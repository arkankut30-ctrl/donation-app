# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect
import sqlite3
import qrcode
import os

app = Flask(__name__)
db_file = "donations.db"

CRYPTO_WALLETS = {
    "BTC": "bc1qre2ead3u4m2rek80vzme56qfa4y5m6xaeflymawf5ty8jqmf7q9v8nar",
    "ETH_ERC20": "0x023fc4502997bblb86d05c1eb17fd2272c169943",
    "USDT_TRON": "TNAyDqdZ6qqatc6Gh71kwjnhw4kbtF7s5M"
}

QR_FOLDER = "static/qr"
os.makedirs(QR_FOLDER, exist_ok=True)

for name, address in CRYPTO_WALLETS.items():
    img = qrcode.make(address)
    img.save(os.path.join(QR_FOLDER, f"{name}.png"))

def init_db():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor TEXT NOT NULL,
            amount TEXT NOT NULL,
            crypto_account TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_donations():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT donor, amount, crypto_account FROM donations")
    rows = c.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    donations = get_donations()
    return render_template("index.html", donations=donations, wallets=CRYPTO_WALLETS)

@app.route("/add", methods=["POST"])
def add_donation():
    donor = request.form["donor"]
    amount = request.form["amount"]
    crypto_account = request.form["crypto_account"]

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("INSERT INTO donations (donor, amount, crypto_account) VALUES (?, ?, ?)",
              (donor, amount, crypto_account))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/export")
def export_csv():
    return "✅ البيانات محفوظة في قاعدة بيانات SQLite (donations.db)"

if __name__ == "__main__":
    # host=0.0.0.0 يسمح باستقبال طلبات من خارج الجهاز (ضروري عند النشر)
    # المنفذ يُقرأ من متغير بيئة PORT الذي تحدده منصة الاستضافة تلقائيًا
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
