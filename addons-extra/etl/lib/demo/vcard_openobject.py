#!/usr/bin/python
import sys
sys.path.append('..')

import etl

filevcard = etl.connector.localfile('input/contacts.vcf')
vcard_in1 = etl.component.input.vcard_in(filevcard)
ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin', 'admin', con_type='xmlrpc')

map = etl.component.transform.map({'main':{
    'id': "tools.uniq_id(main.get('org', 'anonymous'), prefix='partner_')",
    'address_id': "tools.uniq_id(main.get('fn', 'anonymous'), prefix='contact_')",
    'name': "main.get('org',['anonymous'])[0]",
    'contact_name': "main.get('fn','anonymous')",
    'email': "main.get('email','').upper()"
}})

oo_out= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name'}
)

oo_out2= etl.component.output.openobject_out(
     ooconnector,
     'res.partner.address',
     {'name': 'contact_name', 'id':'address_id', 'partner_id:id':'id','email':'email'}
)
log1=etl.component.transform.logger(name='vCard->Oo')

tran=etl.transition(vcard_in1,map)
tran=etl.transition(map,log1)
tran=etl.transition(log1,oo_out)
tran=etl.transition(oo_out,oo_out2)

log2=etl.component.transform.logger(name='Count')

count = etl.component.control.data_count()
tran=etl.transition(map, count, channel_destination='gmail')
tran=etl.transition(oo_out, count, channel_destination='partner')
tran=etl.transition(oo_out2, count, channel_destination='address')
tran=etl.transition(count, log2)


job1=etl.job([vcard_in1,oo_out,oo_out2, log2,count])
job1.run()
print job1.get_statitic_info()
