import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


DATA_FILE = Path(os.getenv('DATA_FILE', '/data/mitkapelim.json'))
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'מתקפלים123')

app = FastAPI(title='Mitkapelim API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv('CORS_ORIGINS', '*').split(',')],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


class Lead(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=50)
    quantity: str = Field(default='', max_length=50)
    project: str = Field(default='', max_length=100)
    notes: str = Field(default='', max_length=5000)
    source: str = Field(default='דף הבית', max_length=100)


class PageView(BaseModel):
    page: str = Field(min_length=1, max_length=200)
    referrer: str = Field(default='ישירה', max_length=1000)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_data() -> dict:
    if not DATA_FILE.exists():
        return {'leads': [], 'views': []}
    try:
        return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {'leads': [], 'views': []}


def write_data(data: dict) -> None:
    with tempfile.NamedTemporaryFile('w', delete=False, dir=str(DATA_FILE.parent), encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        temp_name = handle.name
    Path(temp_name).replace(DATA_FILE)


def append_record(collection: str, record: dict) -> int:
    data = read_data()
    items = data.setdefault(collection, [])
    items.insert(0, record)
    write_data(data)
    return len(items)


def require_admin(password: str | None, header_password: str | None) -> None:
    if (password or header_password) != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail='Unauthorized')


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/api/leads', status_code=201)
def create_lead(lead: Lead) -> dict[str, int]:
    record = {
        'name': lead.name,
        'phone': lead.phone,
        'quantity': lead.quantity,
        'project': lead.project,
        'notes': lead.notes,
        'source': lead.source,
        'created_at': now(),
    }
    return {'id': append_record('leads', record)}


@app.post('/api/analytics', status_code=201)
def create_page_view(view: PageView) -> dict[str, int]:
    record = {'page': view.page, 'referrer': view.referrer, 'created_at': now()}
    return {'id': append_record('views', record)}


@app.get('/api/admin/summary')
def summary(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> dict:
    require_admin(password, x_admin_password)
    data = read_data()
    leads = data.get('leads', [])
    views = data.get('views', [])
    by_page: dict[str, int] = {}
    for view in views:
        by_page[view['page']] = by_page.get(view['page'], 0) + 1
    return {'leads': leads, 'views': views, 'by_page': by_page}


def csv_response(filename: str, headers: list[str], rows: list[list[str]]) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return StreamingResponse(
        iter(['\ufeff' + output.getvalue()]),
        media_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@app.get('/api/admin/leads.csv')
def leads_csv(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> StreamingResponse:
    require_admin(password, x_admin_password)
    leads = read_data().get('leads', [])
    rows = [
        [row['created_at'], row['name'], row['phone'], row['quantity'], row['project'], row['notes'], row['source']]
        for row in leads
    ]
    return csv_response('pniyot-mitkapelim.csv', ['תאריך', 'שם', 'טלפון', 'כמות', 'פרויקט', 'הערות', 'מקור'], rows)


@app.get('/api/admin/analytics.csv')
def analytics_csv(password: str | None = None, x_admin_password: str | None = Header(default=None)) -> StreamingResponse:
    require_admin(password, x_admin_password)
    views = read_data().get('views', [])
    rows = [[row['page'], row['created_at'], row['referrer']] for row in views]
    return csv_response('analytics-mitkapelim.csv', ['דף', 'תאריך', 'מקור'], rows)
