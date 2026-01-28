import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def verify_pages():
    client = Client()
    
    # 1. Test Public Page (Login)
    response = client.get('/login/', HTTP_HOST='127.0.0.1:8000')
    print(f"Login Page: {response.status_code}")
    
    # 2. Login
    username = 'testuser'
    password = 'testpassword123'
    login_success = client.login(username=username, password=password, HTTP_HOST='127.0.0.1:8000')
    print(f"Login Successful: {login_success}")
    
    if login_success:
        # 3. Test Dashboard
        resp_dash = client.get('/', HTTP_HOST='127.0.0.1:8000') # assuming root is dashboard or redirect
        print(f"Root/Dashboard: {resp_dash.status_code}")
        
        # 4. Test My Work (Critical Fix)
        resp_my_work = client.get('/app/my-work/', HTTP_HOST='127.0.0.1:8000')
        print(f"My Work Page: {resp_my_work.status_code}")
        
    else:
        print("Skipping authenticated checks due to login failure.")

if __name__ == '__main__':
    verify_pages()
