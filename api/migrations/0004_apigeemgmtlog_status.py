# Generated by Django 3.2 on 2021-05-07 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_apigeemgmtlog_destination'),
    ]

    operations = [
        migrations.AddField(
            model_name='apigeemgmtlog',
            name='status',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]