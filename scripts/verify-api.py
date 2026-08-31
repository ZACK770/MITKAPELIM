import json
import urllib.parse
import urllib.request

BASE = 'https://mitkapelim-api.onrender.com'
PASSWORD = 'מתקפלים123'


def call(path: str, payload: dict | None = None, method: str = 'GET') -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
    headers = {'Content-Type': 'application/json'} if data else {}
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.status, response.read().decode('utf-8')


def admin(path: str, method: str = 'GET') -> tuple[int, str]:
    return call(path + ('&' if '?' in path else '?') + 'password=' + urllib.parse.quote(PASSWORD), method=method)


status, body = call('/health')
print('health', status, body)

status, body = call('/api/leads', {'name': 'בדיקת מערכת', 'phone': '02-6206070', 'quantity': '12', 'project': 'בית כנסת', 'notes': 'בדיקה', 'source': 'בדיקה'}, 'POST')
print('lead', status, body)

status, body = call('/api/analytics', {'page': 'בדיקה', 'referrer': 'ישירה'}, 'POST')
print('view', status, body)

status, body = admin('/api/admin/summary')
data = json.loads(body)
print('summary', status, 'leads=', len(data['leads']), 'views=', len(data['views']), 'pages=', len(data['by_page']))

status, body = admin('/api/admin/leads.csv')
print('leads csv', status, len(body.splitlines()), 'lines')

status, body = admin('/api/admin/analytics.csv')
print('analytics csv', status, len(body.splitlines()), 'lines')

status, body = admin('/api/admin/data', 'DELETE')
print('clear', status, body)

status, body = admin('/api/admin/summary')
data = json.loads(body)
print('after clear', status, 'leads=', len(data['leads']), 'views=', len(data['views']))
