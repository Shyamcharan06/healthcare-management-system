from decouple import config
from django.contrib.auth.hashers import make_password
from django.db import migrations

ADMIN_USERNAME = config("ADMIN_USERNAME", default="admin")
ADMIN_PASSWORD = config("ADMIN_PASSWORD", default="")


def create_default_admin(apps, schema_editor):
    # Skip when no password is configured; use createsuperuser instead.
    if not ADMIN_PASSWORD:
        return
    User = apps.get_model("accounts", "User")
    if User.objects.filter(role="ADMIN").exists():
        return
    User.objects.create(
        username=ADMIN_USERNAME,
        first_name=ADMIN_USERNAME,
        password=make_password(ADMIN_PASSWORD),
        role="ADMIN",
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


def remove_default_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username=ADMIN_USERNAME, role="ADMIN").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
