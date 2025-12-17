from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = "txs_fast.db"
orb_price = 0.0012

def datetimeformat(value):
    return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")

templates.env.filters['datetimeformat'] = datetimeformat


def get_wallet_data(address):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    address = address.lower()

    cur.execute("""
        SELECT tx_hash, block_number, timestamp, value_eth
        FROM transactions
        WHERE lower(from_address) = ?
        ORDER BY block_number
    """, (address,))
    rows = cur.fetchall()

    total_eth = sum(r[3] for r in rows)
    conn.close()

    return total_eth, rows


@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})


@app.post("/", response_class=HTMLResponse)
async def submit(request: Request):
    form = await request.form()
    address = form.get("address")

    total_eth, txs = get_wallet_data(address)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "address": address,
        "total_eth": total_eth,
        "transactions": txs,
        "results": True
    })
