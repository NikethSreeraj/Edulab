from app.ui.web_app import app

client = app.test_client()
resp = client.get('/')
print('HOME_STATUS', resp.status_code)
print('HOME_HAS_TITLE', 'Edulab' in resp.get_data(as_text=True))
resp2 = client.post('/api/compile', json={'code': 'print(2+2)', 'lang': 'python'})
print('COMPILE_STATUS', resp2.status_code)
print('COMPILE_OUTPUT', resp2.get_json()['output'].strip())
