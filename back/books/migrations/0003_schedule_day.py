# Generated by Django 4.2.16 on 2024-11-20 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_account_book_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='day',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
