# Generated by Django 2.0.5 on 2018-05-25 20:20

from django.db import migrations, models
import django.db.models.deletion
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField()),
                ('max_score', models.PositiveSmallIntegerField()),
                ('minutes_left', models.SmallIntegerField()),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Exam')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(),
        ),
    ]