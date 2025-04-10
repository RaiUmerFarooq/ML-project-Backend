# Generated by Django 5.1.7 on 2025-03-25 20:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('roll_number', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Marks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_type', models.CharField(choices=[('assignment', 'Assignment'), ('quiz', 'Quiz'), ('sessional', 'Sessional')], default='quiz', max_length=20)),
                ('assessment_number', models.IntegerField(default=1)),
                ('marks', models.FloatField()),
                ('max_marks', models.FloatField(default=100)),
                ('date', models.DateField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.student')),
            ],
            options={
                'unique_together': {('student', 'course', 'assessment_type', 'assessment_number', 'date')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_present', models.BooleanField(default=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.student')),
            ],
            options={
                'unique_together': {('student', 'date')},
            },
        ),
    ]
