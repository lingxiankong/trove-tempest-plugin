# Copyright 2014 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.common import utils
from tempest.lib import decorators
from testtools import testcase as testtools

from trove_tempest_plugin.tests import base_test


class DatabaseFlavorsTest(base_test.BaseDatabaseTest):

    @classmethod
    def setup_clients(cls):
        super(DatabaseFlavorsTest, cls).setup_clients()
        cls.client = cls.database_flavors_client

    @testtools.attr('smoke')
    @decorators.idempotent_id('c94b825e-0132-4686-8049-8a4a2bc09525')
    def test_get_db_flavor(self):
        # The expected flavor details should be returned
        flavor = (self.client.show_flavor(self.db_flavor_ref)
                  ['flavor'])
        self.assertEqual(self.db_flavor_ref, str(flavor['id']))
        self.assertIn('ram', flavor)
        self.assertIn('links', flavor)
        self.assertIn('name', flavor)

    @testtools.attr('smoke')
    @decorators.idempotent_id('685025d6-0cec-4673-8a8d-995cb8e0d3bb')
    def test_list_db_flavors(self):
        flavor = (self.client.show_flavor(self.db_flavor_ref)
                  ['flavor'])
        # List of all flavors should contain the expected flavor
        flavors = self.client.list_flavors()['flavors']
        self.assertIn(flavor, flavors)

    def _check_values(self, names, db_flavor, os_flavor, in_db=True):
        for name in names:
            self.assertIn(name, os_flavor)
            if in_db:
                self.assertIn(name, db_flavor)
                self.assertEqual(str(db_flavor[name]), str(os_flavor[name]),
                                 "DB flavor differs from OS on '%s' value"
                                 % name)
            else:
                self.assertNotIn(name, db_flavor)

    @testtools.attr('smoke')
    @decorators.idempotent_id('afb2667f-4ec2-4925-bcb7-313fdcffb80d')
    @utils.services('compute')
    def test_compare_db_flavors_with_os(self):
        db_flavors = self.client.list_flavors()['flavors']
        os_flavors = (self.os_flavors_client.list_flavors(detail=True)
                      ['flavors'])
        self.assertEqual(len(os_flavors), len(db_flavors),
                         "OS flavors %s do not match DB flavors %s" %
                         (os_flavors, db_flavors))
        for os_flavor in os_flavors:
            db_flavor =\
                self.client.show_flavor(os_flavor['id'])['flavor']
            if db_flavor['id']:
                self.assertIn('id', db_flavor)
                self.assertEqual(str(db_flavor['id']), str(os_flavor['id']),
                                 "DB flavor id differs from OS flavor id value"
                                 )
            else:
                self.assertIn('str_id', db_flavor)
                self.assertEqual(db_flavor['str_id'], str(os_flavor['id']),
                                 "DB flavor id differs from OS flavor id value"
                                 )

            self._check_values(['name', 'ram', 'vcpus',
                                'disk'], db_flavor, os_flavor)
            self._check_values(['swap'], db_flavor, os_flavor,
                               in_db=False)
