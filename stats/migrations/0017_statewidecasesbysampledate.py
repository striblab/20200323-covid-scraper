# Generated by Django 3.0.6 on 2020-05-14 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0016_auto_20200513_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatewideCasesBySampleDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_date', models.DateField()),
                ('new_cases', models.IntegerField(default=0)),
                ('total_cases', models.IntegerField(default=0)),
                ('scrape_date', models.DateField()),
            ],
        ),
    ]
