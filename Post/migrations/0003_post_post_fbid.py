# Generated by Django 2.2.4 on 2019-10-31 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0002_imagepost_textpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_fbid',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]