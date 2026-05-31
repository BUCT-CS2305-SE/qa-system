import urllib.request
import ssl

url = 'https://se-cs2305.yazs.top/docs'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request(url, headers={'User-Agent':'python-urllib/3'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = resp.read()
        text = data.decode('utf-8', errors='replace')
        print('STATUS', resp.status)
        print('LENGTH', len(data))
        print('---BEGIN---')
        print(text[:4000])
        print('---END---')
except Exception as e:
    print('ERROR', e)
