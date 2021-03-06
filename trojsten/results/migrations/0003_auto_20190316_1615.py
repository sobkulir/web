# Generated by Django 2.1.5 on 2019-03-16 15:15

import django.contrib.postgres.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("results", "0002_auto_20180219_2151")]

    operations = [
        migrations.AlterField(
            model_name="results",
            name="serialized_results",
            field=django.contrib.postgres.fields.JSONField(blank=True),
        ),
        migrations.RunSQL(
            "alter table results_results alter column serialized_results type jsonb "
            'using "serialized_results"::text::jsonb;',
            reverse_sql="",
        ),
    ]
