# Generated by Django 5.0.3 on 2024-04-03 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardmaker', '0004_remove_visitingcard_image_visitingcard_back_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitingcard',
            name='id',
        ),
        migrations.AddField(
            model_name='visitingcard',
            name='visitingcard_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]