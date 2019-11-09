# Generated by Django 2.2.4 on 2019-11-02 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0004_reachtime'),
    ]

    operations = [
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='imagepost',
            options={'verbose_name': 'Image post', 'verbose_name_plural': 'Image posts'},
        ),
        migrations.AlterModelOptions(
            name='reachtime',
            options={'verbose_name': 'Reach Time', 'verbose_name_plural': 'Reach Times'},
        ),
        migrations.AlterModelOptions(
            name='textpost',
            options={'verbose_name': 'Text post', 'verbose_name_plural': 'Text posts'},
        ),
        migrations.AddField(
            model_name='post',
            name='publish_at',
            field=models.ManyToManyField(blank=True, to='Post.Time'),
        ),
    ]
