# Generated by Django 5.0.3 on 2024-04-03 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardmaker', '0005_remove_visitingcard_id_visitingcard_visitingcard_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitingcard',
            name='visitingcard_id',
        ),
        migrations.AddField(
            model_name='visitingcard',
            name='id',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]