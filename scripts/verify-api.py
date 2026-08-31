import json
import urllib.parse
import urllib.request

BASE = 'https://mitkapelim-api.onrender.com'
PASSWORD = 'מתקפלים123'


def get(path: str) -> tuple[int, str]:
    request = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.status, response.read().decode('utf-8')


status, body = get('/api/admin/summary?password=' + urllib.parse.quote(PASSWORD))
data = json.loads(body)
print('summary', status, 'leads=', len(data['leads']), 'views=', len(data['views']))
print('by_page pages=', len(data['by_page']))

status, body = get('/api/admin/leads.csv?password=' + urllib.parse.quote(PASSWORD))
print('leads csv', status, len(body.splitlines()), 'lines')

status, body = get('/api/admin/analytics.csv?password=' + urllib.parse.quote(PASSWORD))
print('analytics csv', status, len(body.splitlines()), 'lines')
