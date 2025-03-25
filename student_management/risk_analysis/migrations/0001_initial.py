# Generated by Django 5.1.7 on 2025-03-25 20:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentRisk',
            fields=[
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='attendance.student')),
                ('risk_level', models.CharField(max_length=50)),
                ('confidence', models.FloatField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
