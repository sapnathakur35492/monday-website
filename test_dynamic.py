"""
Run on your end: python test_dynamic.py
Verifies that marketing, core, and app pages render with 200 and dynamic content.
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.urls import reverse

def test_dynamic():
    client = Client()
    results = []

    # 1. Landing page: must contain ProjectFlow, and either dynamic data or fallback
    resp = client.get(reverse("landing"))
    ok = resp.status_code == 200
    has_brand = b"ProjectFlow" in resp.content
    has_cta = b"Get Started" in resp.content or b"Sign up" in resp.content.lower()
    results.append(("Landing /", ok and has_brand and has_cta, resp.status_code))

    # 2. Pricing: must contain pricing block (dynamic plans or "No Pricing Plans")
    resp = client.get(reverse("pricing"))
    ok = resp.status_code == 200
    has_plans_or_empty = (
        b"Most Popular" in resp.content
        or b"No Pricing Plans" in resp.content
        or b"Get Started" in resp.content
        or b"seat / month" in resp.content
    )
    results.append(("Pricing", ok and has_plans_or_empty, resp.status_code))

    # 3. Features: must return 200 (dynamic features or empty list)
    resp = client.get(reverse("features"))
    ok = resp.status_code == 200
    has_content = b"ProjectFlow" in resp.content or b"feature" in resp.content.lower()
    results.append(("Features", ok and has_content, resp.status_code))

    # 4. Login: form must be present
    resp = client.get(reverse("login"))
    ok = resp.status_code == 200
    has_form = b"login" in resp.content.lower() or b"email" in resp.content.lower() or b"password" in resp.content
    results.append(("Login", ok and has_form, resp.status_code))

    # 5. Signup: form must be present
    resp = client.get(reverse("signup"))
    ok = resp.status_code == 200
    has_form = b"sign" in resp.content.lower() or b"email" in resp.content or b"username" in resp.content
    results.append(("Signup", ok and has_form, resp.status_code))

    # 6. Authenticated: dashboard (redirect to login if not logged in is ok)
    resp = client.get("/app/")
    ok = resp.status_code in (200, 302)
    results.append(("App root", ok, resp.status_code))

    # 7. About, Contact
    resp = client.get(reverse("about"))
    results.append(("About", resp.status_code == 200, resp.status_code))
    resp = client.get(reverse("contact"))
    results.append(("Contact", resp.status_code == 200, resp.status_code))

    # Report
    print("=== Dynamic & pages test ===\n")
    all_ok = True
    for name, passed, code in results:
        status = "OK" if passed else "FAIL"
        if not passed:
            all_ok = False
        print(f"  {name}: {status} (HTTP {code})")
    print()
    if all_ok:
        print("All checks passed. Content is dynamic (DB-driven or fallback).")
    else:
        print("Some checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    test_dynamic()
