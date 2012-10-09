import unittest2

import openerp
import common

UID = common.ADMIN_USER_ID
DB = common.DB

class TestInherits(common.TransactionCase):
    """ test the behavior of the orm for models that use _inherits;
        specifically: res.users, that inherits from res.partner
    """

    def setUp(self):
        super(TestInherits, self).setUp()
        self.partner = self.registry('res.partner')
        self.user = self.registry('res.users')

    def test_create(self):
        """ creating a user should automatically create a new partner """
        partners_before = self.partner.search(self.cr, UID, [])
        foo_id = self.user.create(self.cr, UID, {'name': 'Foo', 'login': 'foo', 'password': 'foo'})
        foo = self.user.browse(self.cr, UID, foo_id)

        self.assertNotIn(foo.partner_id.id, partners_before)

    def test_create_with_ancestor(self):
        """ creating a user with a specific 'partner_id' should not create a new partner """
        par_id = self.partner.create(self.cr, UID, {'name': 'Foo'})
        partners_before = self.partner.search(self.cr, UID, [])
        foo_id = self.user.create(self.cr, UID, {'partner_id': par_id, 'login': 'foo', 'password': 'foo'})
        partners_after = self.partner.search(self.cr, UID, [])

        self.assertEqual(set(partners_before), set(partners_after))

        foo = self.user.browse(self.cr, UID, foo_id)
        self.assertEqual(foo.name, 'Foo')
        self.assertEqual(foo.partner_id.id, par_id)

    def test_read(self):
        """ inherited fields should be read without any indirection """
        foo_id = self.user.create(self.cr, UID, {'name': 'Foo', 'login': 'foo', 'password': 'foo'})
        foo_values, = self.user.read(self.cr, UID, [foo_id])
        partner_id = foo_values['partner_id'][0]
        partner_values, = self.partner.read(self.cr, UID, [partner_id])
        self.assertEqual(foo_values['name'], partner_values['name'])

        foo = self.user.browse(self.cr, UID, foo_id)
        self.assertEqual(foo.name, foo.partner_id.name)

    def test_copy(self):
        """ copying a user should automatically copy its partner, too """
        foo_id = self.user.create(self.cr, UID, {'name': 'Foo', 'login': 'foo', 'password': 'foo'})
        foo_before, = self.user.read(self.cr, UID, [foo_id])
        bar_id = self.user.copy(self.cr, UID, foo_id, {'login': 'bar', 'password': 'bar'})
        foo_after, = self.user.read(self.cr, UID, [foo_id])

        self.assertEqual(foo_before, foo_after)

        foo, bar = self.user.browse(self.cr, UID, [foo_id, bar_id])
        self.assertEqual(bar.login, 'bar')
        self.assertNotEqual(foo.id, bar.id)
        self.assertNotEqual(foo.partner_id.id, bar.partner_id.id)

    def test_copy_with_ancestor(self):
        """ copying a user with 'parent_id' in defaults should not duplicate the partner """
        foo_id = self.user.create(self.cr, UID, {'name': 'Foo', 'login': 'foo', 'password': 'foo'})
        par_id = self.partner.create(self.cr, UID, {'name': 'Bar'})

        foo_before, = self.user.read(self.cr, UID, [foo_id])
        partners_before = self.partner.search(self.cr, UID, [])
        bar_id = self.user.copy(self.cr, UID, foo_id, {'partner_id': par_id, 'login': 'bar'})
        foo_after, = self.user.read(self.cr, UID, [foo_id])
        partners_after = self.partner.search(self.cr, UID, [])

        self.assertEqual(foo_before, foo_after)
        self.assertEqual(set(partners_before), set(partners_after))

        foo, bar = self.user.browse(self.cr, UID, [foo_id, bar_id])
        self.assertNotEqual(foo.id, bar.id)
        self.assertEqual(bar.partner_id.id, par_id)
        self.assertEqual(bar.login, 'bar', "login is given from copy parameters")
        self.assertEqual(bar.password, foo.password, "password is given from original record")
        self.assertEqual(bar.name, 'Bar', "name is given from specific partner")



CREATE = lambda values: (0, False, values)
UPDATE = lambda id, values: (1, id, values)
DELETE = lambda id: (2, id, False)
FORGET = lambda id: (3, id, False)
LINK_TO = lambda id: (4, id, False)
DELETE_ALL = lambda: (5, False, False)
REPLACE_WITH = lambda ids: (6, False, ids)

def sorted_by_id(list_of_dicts):
    "sort dictionaries by their 'id' field; useful for comparisons"
    return sorted(list_of_dicts, key=lambda d: d.get('id'))

class TestO2MSerialization(common.TransactionCase):
    """ test the orm method 'write' on one2many fields """

    def setUp(self):
        super(TestO2MSerialization, self).setUp()
        self.partner = self.registry('res.partner')

    def test_no_command(self):
        " empty list of commands yields an empty list of records "
        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', [])

        self.assertEqual(results, [])

    def test_CREATE_commands(self):
        " returns the VALUES dict as-is "
        values = [{'foo': 'bar'}, {'foo': 'baz'}, {'foo': 'baq'}]
        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', map(CREATE, values))

        self.assertEqual(results, values)

    def test_LINK_TO_command(self):
        " reads the records from the database, records are returned with their ids. "
        ids = [
            self.partner.create(self.cr, UID, {'name': 'foo'}),
            self.partner.create(self.cr, UID, {'name': 'bar'}),
            self.partner.create(self.cr, UID, {'name': 'baz'})
        ]
        commands = map(LINK_TO, ids)

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', commands, ['name'])

        self.assertEqual(sorted_by_id(results), sorted_by_id([
            {'id': ids[0], 'name': 'foo'},
            {'id': ids[1], 'name': 'bar'},
            {'id': ids[2], 'name': 'baz'}
        ]))

    def test_bare_ids_command(self):
        " same as the equivalent LINK_TO commands "
        ids = [
            self.partner.create(self.cr, UID, {'name': 'foo'}),
            self.partner.create(self.cr, UID, {'name': 'bar'}),
            self.partner.create(self.cr, UID, {'name': 'baz'})
        ]

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', ids, ['name'])

        self.assertEqual(sorted_by_id(results), sorted_by_id([
            {'id': ids[0], 'name': 'foo'},
            {'id': ids[1], 'name': 'bar'},
            {'id': ids[2], 'name': 'baz'}
        ]))

    def test_UPDATE_command(self):
        " take the in-db records and merge the provided information in "
        id_foo = self.partner.create(self.cr, UID, {'name': 'foo'})
        id_bar = self.partner.create(self.cr, UID, {'name': 'bar'})
        id_baz = self.partner.create(self.cr, UID, {'name': 'baz', 'city': 'tag'})

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', [
                LINK_TO(id_foo),
                UPDATE(id_bar, {'name': 'qux', 'city': 'tagtag'}),
                UPDATE(id_baz, {'name': 'quux'})
            ], ['name', 'city'])

        self.assertEqual(sorted_by_id(results), sorted_by_id([
            {'id': id_foo, 'name': 'foo', 'city': False},
            {'id': id_bar, 'name': 'qux', 'city': 'tagtag'},
            {'id': id_baz, 'name': 'quux', 'city': 'tag'}
        ]))

    def test_DELETE_command(self):
        " deleted records are not returned at all. "
        ids = [
            self.partner.create(self.cr, UID, {'name': 'foo'}),
            self.partner.create(self.cr, UID, {'name': 'bar'}),
            self.partner.create(self.cr, UID, {'name': 'baz'})
        ]
        commands = [DELETE(ids[0]), DELETE(ids[1]), DELETE(ids[2])]

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', commands, ['name'])

        self.assertEqual(results, [])

    def test_mixed_commands(self):
        ids = [
            self.partner.create(self.cr, UID, {'name': name})
            for name in ['NObar', 'baz', 'qux', 'NOquux', 'NOcorge', 'garply']
        ]

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', [
                CREATE({'name': 'foo'}),
                UPDATE(ids[0], {'name': 'bar'}),
                LINK_TO(ids[1]),
                DELETE(ids[2]),
                UPDATE(ids[3], {'name': 'quux',}),
                UPDATE(ids[4], {'name': 'corge'}),
                CREATE({'name': 'grault'}),
                LINK_TO(ids[5])
            ], ['name'])

        self.assertEqual(sorted_by_id(results), sorted_by_id([
            {'name': 'foo'},
            {'id': ids[0], 'name': 'bar'},
            {'id': ids[1], 'name': 'baz'},
            {'id': ids[3], 'name': 'quux'},
            {'id': ids[4], 'name': 'corge'},
            {'name': 'grault'},
            {'id': ids[5], 'name': 'garply'}
        ]))

    def test_LINK_TO_pairs(self):
        "LINK_TO commands can be written as pairs, instead of triplets"
        ids = [
            self.partner.create(self.cr, UID, {'name': 'foo'}),
            self.partner.create(self.cr, UID, {'name': 'bar'}),
            self.partner.create(self.cr, UID, {'name': 'baz'})
        ]
        commands = map(lambda id: (4, id), ids)

        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', commands, ['name'])

        self.assertEqual(sorted_by_id(results), sorted_by_id([
            {'id': ids[0], 'name': 'foo'},
            {'id': ids[1], 'name': 'bar'},
            {'id': ids[2], 'name': 'baz'}
        ]))

    def test_singleton_commands(self):
        "DELETE_ALL can appear as a singleton"
        results = self.partner.resolve_2many_commands(
            self.cr, UID, 'address', [DELETE_ALL()], ['name'])

        self.assertEqual(results, [])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
