import os
import django
import json
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from webapp.models import Workspace, Board, Group, Item, Column
from django.db.models import Q

User = get_user_model()

def run_tests():
    print(">>> Starting Comprehensive Feature Test")
    
    # 1. Setup User
    username = 'qatestuser'
    password = 'password123'
    email = 'qa@example.com'
    
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()
    
    # Force login for client
    client = Client()
    client.force_login(user) 
    print(f"[OK] User '{username}' ready.")

    # 2. Setup Board
    # Check for existing workspace or create
    org = user.owned_organizations.first()
    if not org:
        from core.models import Organization
        org = Organization.objects.create(name="QA Org", owner=user)
    
    workspace, _ = Workspace.objects.get_or_create(name="QA Workspace", organization=org)
    board, _ = Board.objects.get_or_create(name="QA Board", workspace=workspace, created_by=user)
    group, _ = Group.objects.get_or_create(board=board, title="QA Group")
    
    # Clean up previous items
    Item.objects.filter(group__board=board).delete()
    print("[OK] Board & Group ready.")

    # 3. Test Feature: Country Column
    print("\n--- Testing Country Column ---")
    # Add column
    col_country = Column.objects.create(board=board, title="Location", type="country", position=10)
    print(f"[OK] Country Column Created (ID: {col_country.id})")
    
    # Create Item
    item = Item.objects.create(group=group, name="Country Task", created_by=user, values={})
    
    # Update Country (Value format: "🇺🇸 US")
    target_country = "🇺🇸 US"
    url = f"/app/update_status/{item.id}/{col_country.id}/"
    resp = client.post(url, {'action_value': target_country}, HTTP_HOST='127.0.0.1:8000')
    
    # Verify DB update
    item.refresh_from_db()
    val = item.values.get(str(col_country.id))
    if val == target_country:
        print(f"[PASS] Database updated correctly to '{val}'")
    else:
        print(f"[FAIL] Database value is '{val}', expected '{target_country}'")

    # Verify HTML response contains the flag
    if target_country in resp.content.decode():
        print("[PASS] HTML response contains the selected country.")
    else:
        print("[FAIL] HTML response missing the expected country string.")

    # 4. Test Feature: Filters (Person Filter)
    print("\n--- Testing Person Filter ---")
    
    # Assign item to user
    col_person = Column.objects.create(board=board, title="Owner", type="person", position=11)
    item.values[str(col_person.id)] = username
    item.save()
    
    # Request Board with Filter
    filter_url = f"/app/board/{board.id}/?person={username}"
    resp_filter = client.get(filter_url, HTTP_HOST='127.0.0.1:8000')
    
    if item.name in resp_filter.content.decode():
        print(f"[PASS] Filtered view contains item '{item.name}'")
    else:
         print(f"[FAIL] Filtered view MISSING item '{item.name}'")
         
    # Request Board with WRONG Filter
    wrong_filter_url = f"/app/board/{board.id}/?person=wronguser"
    resp_wrong = client.get(wrong_filter_url, HTTP_HOST='127.0.0.1:8000')
    
    if item.name not in resp_wrong.content.decode():
        print(f"[PASS] Negative Filter works (Item hidden for wrong user)")
    else:
         print(f"[FAIL] Negative Filter FAILED (Item visible when it should be hidden)")

    # 5. Test My Work (Regression)
    print("\n--- Testing My Work View ---")
    resp_mywork = client.get("/app/my-work/", HTTP_HOST="127.0.0.1:8000")
    if resp_mywork.status_code == 200:
        print("[PASS] My Work page loads (200 OK)")
        if "My Work" in resp_mywork.content.decode():
             print("[PASS] 'My Work' title found in HTML")
    else:
        print(f"[FAIL] My Work page failed with {resp_mywork.status_code}")

    print("\n>>> Feature Verification Complete")

if __name__ == "__main__":
    run_tests()
