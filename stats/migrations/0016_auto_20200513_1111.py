# Generated by Django 3.0.6 on 2020-05-13 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0015_agegrouppop_pct_pop'),
    ]

    operations = [
        migrations.AddField(
            model_name='statewideagedate',
            name='case_count',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='statewideagedate',
            name='death_count',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
