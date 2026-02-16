import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from core.models import Organization, Membership
from webapp.models import Workspace, Board, Group, Column, Item, ItemUpdate
from automation.models import AutomationRule, AutomationLog


def main():
    User = get_user_model()

    # 1) Ensure test user exists (reuse by username OR email)
    username = "testuser"
    password = "testpassword123"
    email = "test@example.com"

    user = User.objects.filter(username=username).first() or User.objects.filter(
        email=email
    ).first()
    if not user:
        user = User.objects.create_user(username=username, email=email, password=password)
    else:
        # Make sure password is known so you can log in via UI
        user.set_password(password)
        user.save()

    print(f"Using user: {user.username} ({user.email})")

    # 2) Ensure organization, membership, workspace, board
    org, _ = Organization.objects.get_or_create(
        owner=user, defaults={"name": "Automation Org"}
    )
    Membership.objects.get_or_create(
        user=user, organization=org, defaults={"role": "admin"}
    )

    ws = Workspace.objects.filter(organization=org, name="Automation Workspace").first()
    if not ws:
        ws = Workspace.objects.create(organization=org, name="Automation Workspace")

    board, _ = Board.objects.get_or_create(
        workspace=ws,
        name="Automation Test Board",
        defaults={"created_by": user, "type": "table", "privacy": "team"},
    )
    if not board.created_by:
        board.created_by = user
        board.save()

    # 3) Ensure columns similar to create_board defaults
    text_col = board.columns.filter(type="text").first()
    status_col = board.columns.filter(type="status").first()

    if text_col is None:
        text_col = Column.objects.create(
            board=board, title="Task Name", type="text", position=0
        )
    if status_col is None:
        status_col = Column.objects.create(
            board=board,
            title="Status",
            type="status",
            position=1,
            settings={"choices": ["Not Started", "Working on it", "Done", "On Hold"]},
        )

    # 4) Ensure a group
    group, _ = Group.objects.get_or_create(
        board=board, title="Tasks", defaults={"color": "#6366f1", "position": 0}
    )

    # 5) Create or reset an automation rule:
    # WHEN status changes to Done -> CREATE UPDATE
    rule, _ = AutomationRule.objects.get_or_create(
        board=board,
        trigger_type="status_change",
        action_type="create_update",
        defaults={
            "name": "When Status is Done -> Create update",
            "is_active": True,
            "trigger_config": {},
            "action_config": {},
        },
    )
    # Make sure configs match current columns
    rule.is_active = True
    rule.trigger_config = {"column_id": str(status_col.id), "value": "Done"}
    rule.action_config = {"message": "Item {item.name} marked as Done 🎉"}
    rule.save()

    # Clean previous logs for this rule
    AutomationLog.objects.filter(rule=rule).delete()

    # 6) Create an item with NOT Done status
    values = {str(status_col.id): "Working on it"}
    item = Item.objects.create(
        group=group,
        name="Automation flow test item",
        created_by=user,
        values=values,
        position=1,
    )

    # 7) Change status to Done to trigger automation
    item.values[str(status_col.id)] = "Done"
    item.save()  # signals + AutomationEngine should fire here

    # 8) Check results
    updates = ItemUpdate.objects.filter(item=item).order_by("-created_at")
    logs = AutomationLog.objects.filter(rule=rule).order_by("-executed_at")

    print("=== Automation Verification ===")
    print(f"Board ID: {board.id}")
    print(f"Status column ID: {status_col.id}")
    print(f"Item ID: {item.id}, name: {item.name}")
    print(f"Item status after save: {item.values.get(str(status_col.id))}")
    print(f"Item updates count: {updates.count()}")
    if updates.exists():
        # Avoid Windows console emoji encoding issues
        body = updates.first().body
        safe_body = body.encode("ascii", "ignore").decode("ascii")
        print(f"Latest update body (ascii): {safe_body}")
    print(f"Automation logs count: {logs.count()}")
    if logs.exists():
        last = logs.first()
        print(f"Last log status: {last.status}, meta: {last.meta}")


if __name__ == "__main__":
    main()

