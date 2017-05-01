#!/usr/bin/python
# ex:set fileencoding=utf-8:

from django.db import router
from django.db.migrations.operations.base import Operation

import os


class RoundcubeMigration(Operation):

    reduces_to_sql = True

    # If this is False, Django will refuse to reverse past this operation.
    reversible = False

    def __init__(self, name, state_operations=[]):
        self.name = name
        self.state_operations = state_operations

    def state_forwards(self, app_label, state):
        # The Operation should take the 'state' parameter (an instance of
        # django.db.migrations.state.ProjectState) and mutate it to match
        # any schema changes that have occurred.
        for state_operation in self.state_operations:
            state_operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.

        vendor = schema_editor.connection.vendor
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roundcube_migrations', vendor, '%s.sql' % self.name)

        data = []

        with open(path) as f:
            sql = []
            for l in f.readlines():
                line = l.rstrip()
                sql.append(line)
                if line.endswith(';'):
                    data.append("\n".join(sql))
                    sql = []

        for sql in data:
            schema_editor.execute(sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        raise NotImplementedError("You cannot reverse this operation")

    def describe(self):
        return "Roundcube migrations"
