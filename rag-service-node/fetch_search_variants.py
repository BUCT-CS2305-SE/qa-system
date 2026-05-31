import json
import urllib.request
import urllib.parse
import ssl

base = 'https://se-cs2305.yazs.top'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

variants = [
    {'q': '女史箴图', 'lang':'zh'},
    {'q': '女史箴图卷', 'lang':'zh'},
    {'q': '女史箴图', 'lang':'en'},
    {'q': 'Nushi Zhen Tu', 'lang':'en'},
    {'title': '女史箴图', 'lang':'zh'},
]

def get(path):
    url = base + path
    req = urllib.request.Request(url, headers={'User-Agent':'python-urllib/3'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            return json.loads(data)
    except Exception as e:
        return {'error': str(e)}

for v in variants:
    if 'q' in v:
        q = urllib.parse.quote(v['q'])
        path = f"/api/search?q={q}&page=1&page_size=10&lang={v.get('lang','zh')}"
    else:
        title = urllib.parse.quote(v['title'])
        path = f"/api/search/advanced?title={title}&page=1&page_size=10&lang={v.get('lang','zh')}"
    print('---', path)
    out = get(path)
    print(json.dumps(out, ensure_ascii=False, indent=2)[:2000])
