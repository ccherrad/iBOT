# Generated by Django 2.2.4 on 2019-11-01 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Page', '0003_auto_20191031_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='subscription_chanllenge',
            field=models.CharField(blank=True, max_length=45),
        ),
    ]