# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-16 14:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("contests", "0004_auto_20170716_1813"), ("events", "0002_auto_20160118_1906")]

    operations = [
        migrations.RenameModel(old_name="Place", new_name="EventPlace"),
        migrations.AddField(
            model_name="event",
            name="semester",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contests.Semester",
                verbose_name="semester",
            ),
        ),
        migrations.RenameModel(old_name="Invitation", new_name="EventParticipant"),
        migrations.DeleteModel(name="OrganizerInvitation"),
        migrations.CreateModel(
            name="EventOrganizer",
            fields=[],
            options={
                "verbose_name": "ved\xfaci",
                "proxy": True,
                "verbose_name_plural": "ved\xfaci",
            },
            bases=("events.eventparticipant",),
        ),
    ]
