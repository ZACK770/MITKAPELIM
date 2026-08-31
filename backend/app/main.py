import csv
import io
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE = DATA_DIR / "mitkapelim.sqlite3"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "מתקפלים123")

app = FastAPI(title="Mitkapelim API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=50)
    quantity: str = Field(default="", max_length=50)
    project: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=5000)
    source: str = Field(default="דף הבית", max_length=100)


class PageView(BaseModel):
    page: str = Field(min_length=1, max_length=200)
    referrer: str = Field(default="ישירה", max_length=1000)


def connection() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def initialize() -> None:
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              phone TEXT NOT NULL,
              quantity TEXT NOT NULL,
              project TEXT NOT NULL,
              notes TEXT NOT NULL,
              source TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS page_views (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              page TEXT NOT NULL,
              referrer TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_admin(password: str | None, header_password: str | None) -> None:
    if (password or header_password) != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")


initialize()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/leads", status_code=201)
def create_lead(lead: Lead) -> dict[str, int]:
    with connection() as db:
        cursor = db.execute(
            "INSERT INTO leads (name, phone, quantity, project, notes, source, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (lead.name, lead.phone, lead.quantity, lead.project, lead.notes, lead.source, now()),
        )
    return {"id": cursor.lastrowid}


@app.post("/api/analytics", status_code=201)
def create_page_view(view: PageView) -> dict[str, int]:
    with connection() as db:
        cursor = db.execute(
            "INSERT INTO page_views (page, referrer, created_at) VALUES (?, ?, ?)",
            (view.page, view.referrer, now()),
        )
    return {"id": cursor.lastrowid}


@app.get("/api/admin/summary")
def summary(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> dict:
    require_admin(password, x_admin_password)
    with connection() as db:
        leads = [dict(row) for row in db.execute("SELECT * FROM leads ORDER BY id DESC")]
        views = [dict(row) for row in db.execute("SELECT * FROM page_views ORDER BY id DESC")]
    by_page: dict[str, int] = {}
    for view in views:
        by_page[view["page"]] = by_page.get(view["page"], 0) + 1
    return {"leads": leads, "views": views, "by_page": by_page}


def csv_response(filename: str, headers: list[str], rows: list[list[str]]) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return StreamingResponse(
        iter(["\ufeff" + output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/admin/leads.csv")
def leads_csv(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> StreamingResponse:
    require_admin(password, x_admin_password)
    with connection() as db:
        rows = [
            [row["created_at"], row["name"], row["phone"], row["quantity"], row["project"], row["notes"], row["source"]]
            for row in db.execute("SELECT * FROM leads ORDER BY id DESC")
        ]
    return csv_response("pniyot-mitkapelim.csv", ["תאריך", "שם", "טלפון", "כמות", "פרויקט", "הערות", "מקור"], rows)


@app.get("/api/admin/analytics.csv")
def analytics_csv(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> StreamingResponse:
    require_admin(password, x_admin_password)
    with connection() as db:
        rows = [
            [row["page"], row["created_at"], row["referrer"]]
            for row in db.execute("SELECT * FROM page_views ORDER BY id DESC")
        ]
    return csv_response("analytics-mitkapelim.csv", ["דף", "תאריך", "מקור"], rows)
