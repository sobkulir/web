from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand, CommandError
from django.utils.six.moves import input
from django.db import connections
from django.db.models import Q

from trojsten.regal.people.models import (User, UserProperty, Address,
    School)


# Kaspar property IDs
EMAIL_PROP = 1
BIRTHDAY_PROP = 2
# Labels for auto-generated properties
KASPAR_ID_LABEL = "kaspar ID"
KASPAR_NOTE_LABEL = "kaspar note"


class Command(NoArgsCommand):
    help = 'Imports people and their related info from kaspar.'

    def handle_noargs(self, **options):
        self.verbosity = options['verbosity']
        kaspar = connections['kaspar']
        c = kaspar.cursor()

        if self.verbosity >= 1:
            self.stdout.write("Migrating schools...")

        c.execute("""
            SELECT school_id, short, name, addr_name, addr_street,
                   addr_city, addr_zip
            FROM schools;
        """)
        school_id_map = dict()
        for row in c:
            kaspar_id, abbr, name, addr_name, street, city, zip_code = row
            candidates = School.objects.filter(
                Q(abbreviation__iexact=abbr) |
                Q(abbreviation__iexact=abbr + '?')
            )
            if len(candidates) == 1:
                if self.verbosity >= 2:
                    self.stdout.write("Matched %r to %s" % (row,
                                                            candidates[0]))
                school_id_map[kaspar_id] = candidates[0]
            elif len(candidates) > 1:
                self.stdout.write("Multiple candidates for %r:\n%s" % (
                    row,
                    "\n".join(("%02d: %s" % i, candidate)
                              for i, candidate in enumerate(candidates))
                ))
                try:
                    choice = int(input("Choice (empty to create new): "))
                except ValueError:
                    school_id_map[kaspar_id] = self.create_school(*row)
                else:
                    school_id_map[kaspar_id] = choices[choice]
            else:
                school_id_map[kaspar_id] = self.create_school(*row)

        if self.verbosity >= 1:
            self.stdout.write("Migrating people...")

        c.execute("""
            SELECT man_id, firstname, lastname, school_id, finish, note
            FROM people;
        """)
        man_id_map = dict()
        for row in c:
            man_id, first_name, last_name, school_id = row[0:4]
            grad_year, note = row[4:]

            new_user_args = {
                'first_name': first_name,
                'last_name': last_name,
                'username': first_name + last_name,
                'is_active': False,
            }

            if grad_year:
                new_user_args['graduation'] = grad_year

            # The following takes O(N) queries and I don't care --
            # it's a one-time background job anyway.
            d = kaspar.cursor()
            d.execute("""
                SELECT ppt_id, value
                FROM people_prop
                WHERE man_id = ? AND ppt_id IN [?, ?]
            """, (man_id, EMAIL_PROP, BIRTHDAY_PROP)
            for prop_id, value in d:
                if prop_id == EMAIL_PROP:
                    new_user_args['email'] = value
                elif prop_id == BIRTHDAY_PROP:
                    new_user_args['birth_date'] = value
            d.close()
            del d

            new_user = User.objects.create(**new_user_args)
            man_id_map[man_id] = new_user

            new_user.properties.create(key=KASPAR_ID_LABEL,
                                       value=man_id)
            if note:
                new_user.properties.create(key=KASPAR_NOTE_LABEL,
                                           value=note)

    def create_school(self, kaspar_id, abbr, name, addr_name, street,
                      city, zip_code):
        abbr += '?' # Question mark denotes schools needing review.
        school = School.objects.create(abbreviation=abbr,
                                       verbose_name=name,
                                       addr_name=addr_name,
                                       street=street,
                                       city=city,
                                       zip_code=zip_code)
        if self.verbosity >= 2:
            self.stdout.write("Created new school %s" % school)
        return school
