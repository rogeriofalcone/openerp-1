import unittest2

import openerp.tests.common as common
from openerp.osv.orm import except_orm

class test_base(common.TransactionCase):

    def setUp(self):
        super(test_base,self).setUp()
        self.res_partner = self.registry('res.partner')
        self.res_users = self.registry('res.users')

        # samples use effective TLDs from the Mozilla public suffix
        # list at http://publicsuffix.org
        self.samples = [
            ('"Raoul Grosbedon" <raoul@chirurgiens-dentistes.fr> ', 'Raoul Grosbedon', 'raoul@chirurgiens-dentistes.fr'),
            ('ryu+giga-Sushi@aizubange.fukushima.jp', '', 'ryu+giga-Sushi@aizubange.fukushima.jp'),
            ('Raoul chirurgiens-dentistes.fr', 'Raoul chirurgiens-dentistes.fr', ''),
            (" Raoul O'hara  <!@historicalsociety.museum>", "Raoul O'hara", '!@historicalsociety.museum')
        ]

    def test_00_res_partner_name_create(self):
        cr, uid = self.cr, self.uid
        parse = self.res_partner._parse_partner_name
        for text, name, mail in self.samples:
            self.assertEqual((name,mail), parse(text), 'Partner name parsing failed')
            partner_id, dummy = self.res_partner.name_create(cr, uid, text)
            partner = self.res_partner.browse(cr, uid, partner_id)
            self.assertEqual(name or mail, partner.name, 'Partner name incorrect')
            self.assertEqual(mail or False, partner.email, 'Partner email incorrect')

    def test_10_res_partner_find_or_create(self):
        cr,uid = self.cr, self.uid
        email = self.samples[0][0]
        partner_id, dummy = self.res_partner.name_create(cr, uid, email)
        found_id = self.res_partner.find_or_create(cr, uid, email)
        self.assertEqual(partner_id, found_id, 'find_or_create failed')
        new_id = self.res_partner.find_or_create(cr, uid, self.samples[1][0])
        self.assertTrue(new_id > partner_id, 'find_or_create failed - should have created new one')
        new_id2 = self.res_partner.find_or_create(cr, uid, self.samples[2][0])
        self.assertTrue(new_id2 > new_id, 'find_or_create failed - should have created new one again')

    def test_15_res_partner_name_search(self):
        cr,uid = self.cr, self.uid
        for name, active in [
            ('"A Raoul Grosbedon" <raoul@chirurgiens-dentistes.fr>', False),
            ('B Raoul chirurgiens-dentistes.fr', True),
            ("C Raoul O'hara  <!@historicalsociety.museum>", True),
            ('ryu+giga-Sushi@aizubange.fukushima.jp', True),
        ]:
            partner_id, dummy = self.res_partner.name_create(cr, uid, name, context={'default_active': active})
        partners = self.res_partner.name_search(cr, uid, 'Raoul')
        self.assertEqual(len(partners), 2, 'Incorrect search number result for name_search')
        partners = self.res_partner.name_search(cr, uid, 'Raoul', limit=1)
        self.assertEqual(len(partners), 1, 'Incorrect search number result for name_search with a limit')
        self.assertEqual(partners[0][1], 'B Raoul chirurgiens-dentistes.fr', 'Incorrect partner returned, should be the first active')

    def test_20_res_partner_address_sync(self):
        cr, uid = self.cr, self.uid
        ghoststep = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                             {'name': 'GhostStep',
                                                                              'is_company': True,
                                                                              'street': 'Main Street, 10',
                                                                              'phone': '123456789',
                                                                              'email': 'info@ghoststep.com',
                                                                              'vat': 'BE0477472701',
                                                                              'type': 'default'}))
        p1 = self.res_partner.browse(cr, uid, self.res_partner.name_create(cr, uid, 'Denis Bladesmith <denis.bladesmith@ghoststep.com>')[0])
        self.assertEqual(p1.type, 'contact', 'Default type must be "contact"')
        p1phone = '123456789#34'
        p1.write({'phone': p1phone,
                  'parent_id': ghoststep.id,
                  'use_parent_address': True})
        p1.refresh()
        self.assertEqual(p1.street, ghoststep.street, 'Address fields must be synced')
        self.assertEqual(p1.phone, p1phone, 'Phone should be preserved after address sync')
        self.assertEqual(p1.type, 'contact', 'Type should be preserved after address sync')
        self.assertEqual(p1.email, 'denis.bladesmith@ghoststep.com', 'Email should be preserved after sync')

        # turn off sync
        p1street = 'Different street, 42'
        p1.write({'street': p1street,
                  'use_parent_address': False})
        p1.refresh(), ghoststep.refresh() 
        self.assertEqual(p1.street, p1street, 'Address fields must not be synced after turning sync off')
        self.assertNotEqual(ghoststep.street, p1street, 'Parent address must never be touched')

        # turn on sync again       
        p1.write({'use_parent_address': True})
        p1.refresh()
        self.assertEqual(p1.street, ghoststep.street, 'Address fields must be synced again')
        self.assertEqual(p1.phone, p1phone, 'Phone should be preserved after address sync')
        self.assertEqual(p1.type, 'contact', 'Type should be preserved after address sync')
        self.assertEqual(p1.email, 'denis.bladesmith@ghoststep.com', 'Email should be preserved after sync')

        # Modify parent, sync to children
        ghoststreet = 'South Street, 25'
        ghoststep.write({'street': ghoststreet})
        p1.refresh()
        self.assertEqual(p1.street, ghoststreet, 'Address fields must be synced automatically')
        self.assertEqual(p1.phone, p1phone, 'Phone should not be synced')
        self.assertEqual(p1.email, 'denis.bladesmith@ghoststep.com', 'Email should be preserved after sync')

        p1street = 'My Street, 11'
        p1.write({'street': p1street})
        ghoststep.refresh()
        self.assertEqual(ghoststep.street, ghoststreet, 'Touching contact should never alter parent')


    def test_30_res_partner_first_contact_sync(self):
        """ Test initial creation of company/contact pair where contact address gets copied to
        company """
        cr, uid = self.cr, self.uid
        ironshield = self.res_partner.browse(cr, uid, self.res_partner.name_create(cr, uid, 'IronShield')[0])
        self.assertFalse(ironshield.is_company, 'Partners are not companies by default')
        self.assertFalse(ironshield.use_parent_address, 'use_parent_address defaults to False')
        self.assertEqual(ironshield.type, 'contact', 'Default type must be "contact"')
        ironshield.write({'type': 'default'}) # force default type to double-check sync 
        p1 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                      {'name': 'Isen Hardearth',
                                                                       'street': 'Strongarm Avenue, 12',
                                                                       'parent_id': ironshield.id}))
        self.assertEquals(p1.type, 'contact', 'Default type must be "contact", not the copied parent type')
        ironshield.refresh()
        self.assertEqual(ironshield.street, p1.street, 'Address fields should be copied to company')
        self.assertTrue(ironshield.is_company, 'Company flag should be turned on after first contact creation')

    def test_40_res_partner_address_getc(self):
        """ Test address_get address resolution mechanism: it should first go down through descendants,
        stopping when encountering another is_copmany entity, then go up, stopping again at the first
        is_company entity or the root ancestor and if nothing matches, it should use the provided partner
        itself """
        cr, uid = self.cr, self.uid
        elmtree = self.res_partner.browse(cr, uid, self.res_partner.name_create(cr, uid, 'Elmtree')[0])
        branch1 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Branch 1',
                                                                                     'parent_id': elmtree.id,
                                                                                     'is_company': True}))
        leaf10 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Leaf 10',
                                                                                    'parent_id': branch1.id,
                                                                                    'type': 'invoice'}))
        branch11 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Branch 11',
                                                                                      'parent_id': branch1.id,
                                                                                      'type': 'other'}))
        leaf111 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Leaf 111',
                                                                                    'parent_id': branch11.id,
                                                                                    'type': 'delivery'}))
        branch11.write({'is_company': False}) # force is_company after creating 1rst child
        branch2 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Branch 2',
                                                                                     'parent_id': elmtree.id,
                                                                                     'is_company': True}))
        leaf21 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Leaf 21',
                                                                                    'parent_id': branch2.id,
                                                                                    'type': 'delivery'}))
        leaf22 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Leaf 22',
                                                                                    'parent_id': branch2.id}))
        leaf23 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid, {'name': 'Leaf 23',
                                                                                    'parent_id': branch2.id,
                                                                                    'type': 'default'}))
        # go up, stop at branch1
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf111.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf111.id,
                          'invoice': leaf10.id,
                          'contact': branch1.id,
                          'other': branch11.id,
                          'default': leaf111.id}, 'Invalid address resolution')
        self.assertEqual(self.res_partner.address_get(cr, uid, [branch11.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf111.id,
                          'invoice': leaf10.id,
                          'contact': branch1.id,
                          'other': branch11.id,
                          'default': branch11.id}, 'Invalid address resolution')

        # go down, stop at at all child companies
        self.assertEqual(self.res_partner.address_get(cr, uid, [elmtree.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': elmtree.id,
                          'invoice': elmtree.id,
                          'contact': elmtree.id,
                          'other': elmtree.id,
                          'default': elmtree.id}, 'Invalid address resolution')

        # go down through children
        self.assertEqual(self.res_partner.address_get(cr, uid, [branch1.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf111.id,
                          'invoice': leaf10.id,
                          'contact': branch1.id,
                          'other': branch11.id,
                          'default': branch1.id}, 'Invalid address resolution')
        self.assertEqual(self.res_partner.address_get(cr, uid, [branch2.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf21.id,
                          'invoice': leaf23.id,
                          'contact': branch2.id,
                          'other': leaf23.id,
                          'default': leaf23.id}, 'Invalid address resolution')

        # go up then down through siblings
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf21.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf21.id,
                          'invoice': leaf23.id,
                          'contact': branch2.id,
                          'other': leaf23.id,
                          'default': leaf23.id
                          }, 'Invalid address resolution, should scan commercial entity ancestor and its descendants')
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf22.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf21.id,
                          'invoice': leaf23.id,
                          'contact': leaf22.id,
                          'other': leaf23.id,
                          'default': leaf23.id}, 'Invalid address resolution, should scan commercial entity ancestor and its descendants')
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf23.id], ['delivery', 'invoice', 'contact', 'other', 'default']),
                         {'delivery': leaf21.id,
                          'invoice': leaf23.id,
                          'contact': branch2.id,
                          'other': leaf23.id,
                          'default': leaf23.id}, 'Invalid address resolution, `default` should only override if no partner with specific type exists')

        # empty adr_pref means only 'default'
        self.assertEqual(self.res_partner.address_get(cr, uid, [elmtree.id], []),
                        {'default': elmtree.id}, 'Invalid address resolution, no default means commercial entity ancestor')
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf111.id], []),
                        {'default': leaf111.id}, 'Invalid address resolution, no default means contact itself')
        branch11.write({'type': 'default'})
        self.assertEqual(self.res_partner.address_get(cr, uid, [leaf111.id], []),
                        {'default': branch11.id}, 'Invalid address resolution, branch11 should now be default')


    def test_50_res_partner_commercial_sync(self):    
        cr, uid = self.cr, self.uid
        p0 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                      {'name': 'Sigurd Sunknife',
                                                                       'email': 'ssunknife@gmail.com'}))
        sunhelm = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                           {'name': 'Sunhelm',
                                                                            'is_company': True,
                                                                            'street': 'Rainbow Street, 13',
                                                                            'phone': '1122334455',
                                                                            'email': 'info@sunhelm.com',
                                                                            'vat': 'BE0477472701',
                                                                            'child_ids': [(4, p0.id),
                                                                                          (0, 0, {'name': 'Alrik Greenthorn',
                                                                                                  'email': 'agr@sunhelm.com'})],
                                                                            }))
        p1 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                      {'name': 'Otto Blackwood',
                                                                       'email': 'otto.blackwood@sunhelm.com',
                                                                       'parent_id': sunhelm.id}))
        p11 = self.res_partner.browse(cr, uid, self.res_partner.create(cr, uid,
                                                                      {'name': 'Gini Graywool',
                                                                       'email': 'ggr@sunhelm.com',
                                                                       'parent_id': p1.id}))
        p2 = self.res_partner.browse(cr, uid, self.res_partner.search(cr, uid,
                                                                      [('email', '=', 'agr@sunhelm.com')])[0])

        for p in (p0, p1, p11, p2):
            p.refresh()
            self.assertEquals(p.commercial_partner_id, sunhelm, 'Incorrect commercial entity resolution')
            self.assertEquals(p.vat, sunhelm.vat, 'Commercial fields must be automatically synced')
        sunhelmvat = 'BE0123456789'
        sunhelm.write({'vat': sunhelmvat})
        for p in (p0, p1, p11, p2):
            p.refresh()
            self.assertEquals(p.vat, sunhelmvat, 'Commercial fields must be automatically and recursively synced')

        p1vat = 'BE0987654321'
        p1.write({'vat': p1vat})
        for p in (sunhelm, p0, p11, p2):
            p.refresh()
            self.assertEquals(p.vat, sunhelmvat, 'Sync to children should only work downstream and on commercial entities')

        # promote p1 to commercial entity
        vals = p1.onchange_type(is_company=True)['value']
        p1.write(dict(vals, parent_id=sunhelm.id,
                      is_company=True,
                      name='Sunhelm Subsidiary'))
        p1.refresh()
        self.assertEquals(p1.vat, p1vat, 'Setting is_company should stop auto-sync of commercial fields')
        self.assertEquals(p1.commercial_partner_id, p1, 'Incorrect commercial entity resolution after setting is_company')

        # writing on parent should not touch child commercial entities
        sunhelmvat2 = 'BE0112233445'
        sunhelm.write({'vat': sunhelmvat2})
        p1.refresh()
        self.assertEquals(p1.vat, p1vat, 'Setting is_company should stop auto-sync of commercial fields')
        p0.refresh()
        self.assertEquals(p0.vat, sunhelmvat2, 'Commercial fields must be automatically synced')

    def test_60_read_group(self):
        cr, uid = self.cr, self.uid
        for user_data in [
          {'name': 'Alice', 'login': 'alice', 'color': 1, 'function': 'Friend'},
          {'name': 'Bob', 'login': 'bob', 'color': 2, 'function': 'Friend'},
          {'name': 'Eve', 'login': 'eve', 'color': 3, 'function': 'Eavesdropper'},
          {'name': 'Nab', 'login': 'nab', 'color': 2, 'function': '5$ Wrench'},
        ]:
          self.res_users.create(cr, uid, user_data)

        groups_data = self.res_users.read_group(cr, uid, domain=[('login', 'in', ('alice', 'bob', 'eve'))], fields=['name', 'color', 'function'], groupby='function')
        self.assertEqual(len(groups_data), 2, "Incorrect number of results when grouping on a field")
        for group_data in groups_data:
          self.assertIn('color', group_data, "Aggregated data for the column 'color' is not present in read_group return values")
          self.assertEqual(group_data['color'], 3, "Incorrect sum for aggregated data for the column 'color'")

        groups_data = self.res_users.read_group(cr, uid, domain=[('login', 'in', ('alice', 'bob', 'eve'))], fields=['name', 'color'], groupby='name', orderby='name DESC, color asc')
        self.assertEqual(len(groups_data), 3, "Incorrect number of results when grouping on a field")
        self.assertEqual([user['name'] for user in groups_data], ['Eve', 'Bob', 'Alice'], 'Incorrect ordering of the list')

        groups_data = self.res_users.read_group(cr, uid, domain=[('login', 'in', ('alice', 'bob', 'eve', 'nab'))], fields=['function', 'color'], groupby='function', orderby='color ASC')
        self.assertEqual(len(groups_data), 3, "Incorrect number of results when grouping on a field")
        self.assertEqual(groups_data, sorted(groups_data, key=lambda x: x['color']), 'Incorrect ordering of the list')

class test_partner_recursion(common.TransactionCase):

    def setUp(self):
        super(test_partner_recursion,self).setUp()
        self.res_partner = self.registry('res.partner')
        cr, uid = self.cr, self.uid
        self.p1 = self.res_partner.name_create(cr, uid, 'Elmtree')[0]
        self.p2 = self.res_partner.create(cr, uid, {'name': 'Elmtree Child 1', 'parent_id': self.p1})
        self.p3 = self.res_partner.create(cr, uid, {'name': 'Elmtree Grand-Child 1.1', 'parent_id': self.p2})

    # split 101, 102, 103 tests to force SQL rollback between them

    def test_101_res_partner_recursion(self):
        cr, uid, p1, p3 = self.cr, self.uid, self.p1, self.p3
        self.assertRaises(except_orm, self.res_partner.write, cr, uid, [p1], {'parent_id': p3})

    def test_102_res_partner_recursion(self):
        cr, uid, p2, p3 = self.cr, self.uid, self.p2, self.p3
        self.assertRaises(except_orm, self.res_partner.write, cr, uid, [p2], {'parent_id': p3})

    def test_103_res_partner_recursion(self):
        cr, uid, p3 = self.cr, self.uid, self.p3
        self.assertRaises(except_orm, self.res_partner.write, cr, uid, [p3], {'parent_id': p3})

    def test_104_res_partner_recursion_indirect_cycle(self):
        """ Indirect hacky write to create cycle in children """
        cr, uid, p2, p3 = self.cr, self.uid, self.p2, self.p3
        p3b = self.res_partner.create(cr, uid, {'name': 'Elmtree Grand-Child 1.2', 'parent_id': self.p2})
        self.assertRaises(except_orm, self.res_partner.write, cr, uid, [p2],
                          {'child_ids': [(1, p3, {'parent_id': p3b}), (1, p3b, {'parent_id': p3})]})

    def test_110_res_partner_recursion_multi_update(self):
        """ multi-write on several partners in same hierarchy must not trigger a false cycle detection """
        cr, uid, p1, p2, p3 = self.cr, self.uid, self.p1, self.p2, self.p3
        self.assertTrue(self.res_partner.write(cr, uid, [p1,p2,p3], {'phone': '123456'}))

class test_translation(common.TransactionCase):

    def setUp(self):
        super(test_translation, self).setUp()
        self.res_category = self.registry('res.partner.category')
        self.ir_translation = self.registry('ir.translation')
        cr, uid = self.cr, self.uid
        self.registry('ir.translation').load_module_terms(cr, ['base'], ['fr_FR'])
        self.cat_id = self.res_category.create(cr, uid, {'name': 'Customers'})
        self.ir_translation.create(cr, uid, {'name': 'res.partner.category,name', 'module':'base', 
            'value': 'Clients', 'res_id': self.cat_id, 'lang':'fr_FR', 'state':'translated', 'type': 'model'})

    def test_101_create_translated_record(self):
        cr, uid = self.cr, self.uid
        
        no_context_cat = self.res_category.browse(cr, uid, self.cat_id)
        self.assertEqual(no_context_cat.name, 'Customers', "Error in basic name_get")

        fr_context_cat = self.res_category.browse(cr, uid, self.cat_id, context={'lang':'fr_FR'})
        self.assertEqual(fr_context_cat.name, 'Clients', "Translation not found")

    def test_102_duplicate_record(self):
        cr, uid = self.cr, self.uid
        self.new_cat_id = self.res_category.copy(cr, uid, self.cat_id, context={'lang':'fr_FR'})

        no_context_cat = self.res_category.browse(cr, uid, self.new_cat_id)
        self.assertEqual(no_context_cat.name, 'Customers', "Duplication did not set untranslated value")

        fr_context_cat = self.res_category.browse(cr, uid, self.new_cat_id, context={'lang':'fr_FR'})
        self.assertEqual(fr_context_cat.name, 'Clients', "Did not found translation for initial value")

    def test_103_duplicate_record_fr(self):
        cr, uid = self.cr, self.uid
        self.new_fr_cat_id = self.res_category.copy(cr, uid, self.cat_id, default={'name': 'Clients (copie)'}, context={'lang':'fr_FR'})

        no_context_cat = self.res_category.browse(cr, uid, self.new_fr_cat_id)
        self.assertEqual(no_context_cat.name, 'Customers', "Duplication erased original untranslated value")

        fr_context_cat = self.res_category.browse(cr, uid, self.new_fr_cat_id, context={'lang':'fr_FR'})
        self.assertEqual(fr_context_cat.name, 'Clients (copie)', "Did not used default value for translated value")

test_state = None
#: Stores state information across multiple test classes
def setUpModule():
    global test_state
    test_state = {}
def tearDownModule():
    global test_state
    test_state = None

class TestPhaseInstall00(unittest2.TestCase):
    """
    WARNING: Relies on tests being run in alphabetical order
    """
    @classmethod
    def setUpClass(cls):
        cls.state = None

    def test_00_setup(self):
        type(self).state = 'init'

    @common.at_install(False)
    def test_01_no_install(self):
        type(self).state = 'error'

    def test_02_check(self):
        self.assertEqual(
            self.state, 'init',
            "Testcase state should not have been transitioned from 00")

class TestPhaseInstall01(unittest2.TestCase):
    at_install = False

    def test_default_norun(self):
        self.fail("An unmarket test in a non-at-install case should not run")

    @common.at_install(True)
    def test_set_run(self):
        test_state['set_at_install'] = True

class TestPhaseInstall02(unittest2.TestCase):
    """
    Can't put the check for test_set_run in the same class: if
    @common.at_install does not work for test_set_run, it won't work for
    the other one either. Thus move checking of whether test_set_run has
    correctly run indeed to a separate class.

    Warning: relies on *classes* being run in alphabetical order in test
    modules
    """
    def test_check_state(self):
        self.assertTrue(
            test_state.get('set_at_install'),
            "The flag should be set if local overriding of runstate")

if __name__ == '__main__':
    unittest2.main()
