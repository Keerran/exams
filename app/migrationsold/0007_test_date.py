# Generated by Django 2.0.5 on 2018-05-25 22:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20180525_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]