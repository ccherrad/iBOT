# Generated by Django 2.2.4 on 2019-11-07 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chatbot', '0007_message_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='payment_succeeded',
            field=models.BooleanField(default=False),
        ),
    ]