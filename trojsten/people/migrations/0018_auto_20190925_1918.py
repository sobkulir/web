# Generated by Django 2.1.9 on 2019-09-25 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0017_auto_20180915_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='last name'),
        ),
    ]
