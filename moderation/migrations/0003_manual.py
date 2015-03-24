from django.db import models, migrations


def load_data(apps, schema_editor):
    group = apps.get_model("auth", "Group")
    group(name='Moderator').save()


class Migration(migrations.Migration):
    dependencies = [
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
