
from datetime import datetime, timezone
from pathlib import Path
import csv, io, sqlite3

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="IQ Cloud Signals V2")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB = "signals_v2.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(""" CREATE TABLE IF NOT EXISTS scheduled_signals ( id INTEGER PRIMARY KEY AUTOINCREMENT, external_id TEXT, date TEXT, time TEXT, asset TEXT, direction TEXT, expiry TEXT, amount TEXT, status TEXT DEFAULT 'PENDING', result TEXT DEFAULT '', created_at TEXT ) """)
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/signals")
def signals():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(""" SELECT * FROM scheduled_signals ORDER BY date, time, id """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.delete("/api/signals")
def clear_signals():
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM scheduled_signals")
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    raw = await file.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    required = {"ID", "DATA", "HORA", "ATIVO", "DIREÇÃO", "EXPIRAÇÃO", "VALOR"}
    headers = set(reader.fieldnames or [])
    missing = required - headers
    if missing:
        return {"ok": False, "error": "Colunas ausentes: " + ", ".join(sorted(missing))}

    conn = sqlite3.connect(DB)
    count = 0
    for row in reader:
        if count >= 30:
            break
        conn.execute(""" INSERT INTO scheduled_signals (external_id, date, time, asset, direction, expiry, amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?) """, (
            row["ID"], row["DATA"], row["HORA"], row["ATIVO"],
            row["DIREÇÃO"].upper(), row["EXPIRAÇÃO"], row["VALOR"],
            datetime.now(timezone.utc).isoformat()
        ))
        count += 1
    conn.commit()
    conn.close()
    return {"ok": True, "imported": count}

@app.post("/api/signals/{signal_id}/cancel")
def cancel_signal(signal_id: int):
    conn = sqlite3.connect(DB)
    conn.execute(""" UPDATE scheduled_signals SET status='CANCELLED' WHERE id=? AND status='PENDING' """, (signal_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/health")
def health():
    return {
        "status": "ONLINE",
        "server_time": datetime.now(timezone.utc).isoformat(),
        "mode": "SCHEDULED-SIGNALS"
    }
