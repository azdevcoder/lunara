import sys
sys.path.insert(0, r'C:\Users\PC-68\Desktop\opencode\lunara')
from app import create_app

app = create_app()

# Test client
with app.test_client() as client:
    # First, GET the login page to set CSRF token in session
    resp = client.get('/login')
    print(f"GET /login: {resp.status_code}")
    
    # Now get the CSRF token from the session
    with client.session_transaction() as sess:
        csrf_token = sess.get('_csrf', '')
    print(f"CSRF token after GET /login: {csrf_token}")
    
    # Now POST to login with the CSRF token
    resp = client.post('/login', data={
        'email': 'ana.teste@lunara.app',
        'password': 'lunara1234',
        '_csrf': csrf_token
    }, follow_redirects=False)
    print(f"POST /login: {resp.status_code} - {resp.location}")
    
    # If login succeeded, test the save functions
    if resp.status_code == 302:
        print("Login successful!")
        
        # Test GET /registro/2026-10-14
        resp = client.get('/registro/2026-10-14')
        print(f"GET /registro/2026-10-14: {resp.status_code}")
        
        # Get CSRF token for this request
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        print(f"CSRF token: {csrf_token}")
        
        # Test POST /registro/2026-10-14 (save log)
        resp = client.post('/registro/2026-10-14', data={
            'flow': 'medium',
            'moods': 'happy',
            'symptoms': 'cramps',
            'energy': '3',
            'sleep_hours': '8',
            'water_ml': '2000',
            'weight_kg': '60',
            'temperature': '36.5',
            'sex': 'feminino',
            'discharge': '',
            'cravings': 'doces',
            'exercise': 'caminhada',
            'medication': '',
            'pill_taken': 'on',
            'notes': 'Teste de salvamento',
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /registro/2026-10-14: {resp.status_code} - {resp.location}")
        
        # Verify the log was saved by checking /saude
        resp = client.get('/saude')
        print(f"GET /saude after log save: {resp.get_json()}")
        
        # Test quick water
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/quick/water', data={
            '_csrf': csrf_token,
            'delta': '250'
        }, follow_redirects=True)
        print(f"POST /quick/water: {resp.status_code} - {resp.location}")
        
        # Test quick mood
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/quick/mood', data={
            '_csrf': csrf_token,
            'mood': 'happy'
        }, follow_redirects=True)
        print(f"POST /quick/mood: {resp.status_code} - {resp.location}")
        
        # Test quick pill
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/quick/pill', data={
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /quick/pill: {resp.status_code} - {resp.location}")
        
        # Test period start
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/periodo/iniciar', data={
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /periodo/iniciar: {resp.status_code} - {resp.location}")
        
        # Test profile update
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/perfil', data={
            'action': 'profile',
            'name': 'Ana Teste',
            'email': 'ana.teste@lunara.app',
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /perfil (profile): {resp.status_code} - {resp.location}")
        
        # Test cycle settings
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/perfil', data={
            'action': 'cycle',
            'cycle_length': '28',
            'period_length': '5',
            'last_period_start': '2026-10-14',
            'seed_period': 'on',
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /perfil (cycle): {resp.status_code} - {resp.location}")
        
        # Test pregnancy mode
        with client.session_transaction() as sess:
            csrf_token = sess.get('_csrf', '')
        resp = client.post('/perfil', data={
            'action': 'pregnancy',
            'pregnancy_mode': 'on',
            'due_date': '2027-06-20',
            '_csrf': csrf_token
        }, follow_redirects=True)
        print(f"POST /perfil (pregnancy): {resp.status_code} - {resp.location}")
    else:
        print("Login failed")