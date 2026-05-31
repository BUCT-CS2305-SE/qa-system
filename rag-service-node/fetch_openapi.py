import urllib.request, ssl, json
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://se-cs2305.yazs.top/openapi.json'
req = urllib.request.Request(url, headers={'User-Agent':'python-urllib/3'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = resp.read().decode('utf-8', errors='replace')
        obj = json.loads(data)
        print(json.dumps(obj, ensure_ascii=False)[:8000])
except Exception as e:
    print('ERROR', e)
