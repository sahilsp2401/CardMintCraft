# Generated by Django 5.0.3 on 2024-04-21 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardmaker', '0007_idcard'),
    ]

    operations = [
        migrations.RenameField(
            model_name='idcard',
            old_name='front_image',
            new_name='image',
        ),
    ]
