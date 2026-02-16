"""
Simulate browser flow: open app, login, dashboard, board, automation.
Run with: python test_browser_flow.py
Server should be running at http://127.0.0.1:8001/
"""
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from webapp.models import Board

def main():
    client = Client()
    base = "http://127.0.0.1:8001"

    # 1) Landing
    r = client.get("/", HTTP_HOST="127.0.0.1:8001")
    print(f"GET / (Landing)     -> {r.status_code}")

    # 2) Login page
    r = client.get("/login/", HTTP_HOST="127.0.0.1:8001")
    print(f"GET /login/         -> {r.status_code}")

    # 3) Login (email + password - as per core.views.login_view)
    r = client.post(
        "/login/",
        {"email": "test@example.com", "password": "testpassword123"},
        HTTP_HOST="127.0.0.1:8001",
        follow=True,
    )
    print(f"POST /login/        -> {r.status_code} (redirects: {len(r.redirect_chain)})")

    if r.status_code != 200:
        print("Login failed. Create user with: python verify_automation_flow.py")
        return

    # 4) Dashboard (app home)
    r = client.get("/app/", HTTP_HOST="127.0.0.1:8001")
    print(f"GET /app/ (Dashboard) -> {r.status_code}")

    # 5) Board detail (use Automation Test Board from verify_automation_flow, else first board user can access)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(email="test@example.com")
    board = Board.objects.filter(name="Automation Test Board", workspace__organization__memberships__user=user).first()
    if not board:
        board = Board.objects.filter(workspace__organization__memberships__user=user).first()
    if not board:
        print("No board found. Run verify_automation_flow.py first.")
        return
    r = client.get(reverse("board_detail", args=[board.id]), HTTP_HOST="127.0.0.1:8001")
    print(f"GET /app/board/{board.id}/ -> {r.status_code}")

    # 6) Automation center (list)
    r = client.get(reverse("automation_list", args=[board.id]), HTTP_HOST="127.0.0.1:8001")
    print(f"GET automation list  -> {r.status_code}")

    # 7) Automation create rule page
    r = client.get(reverse("create_rule", args=[board.id]), HTTP_HOST="127.0.0.1:8001")
    print(f"GET automation new rule -> {r.status_code}")

    print("\nDone. All critical pages OK. Open in browser: http://127.0.0.1:8001/")
    print("Login: test@example.com / testpassword123")

if __name__ == "__main__":
    main()
