# Generated by Django 3.0.6 on 2020-05-11 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0014_agegrouppop'),
    ]

    operations = [
        migrations.AddField(
            model_name='agegrouppop',
            name='pct_pop',
            field=models.IntegerField(null=True),
        ),
    ]
