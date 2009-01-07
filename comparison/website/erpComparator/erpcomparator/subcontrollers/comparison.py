
import xml.dom.minidom

from turbojson import jsonify
from turbogears import expose
from turbogears import controllers

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common

class Comparison(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.comparison")
    def index(self, **kw):
        
        selected_items = []
        selected_items = kw.get('ids')
        
        selected_items = selected_items and eval(str(selected_items))
        
        model = 'comparison.factor'
        context = rpc.session.context
        
        proxy = rpc.RPCProxy(model)
        
        domain = [('parent_id', '=', False)]
        
        ids = proxy.search(domain, 0, 0, 0, context)
        
        view = proxy.fields_view_get(False, 'tree', context)
        fields = proxy.fields_get(False, rpc.session.context)
        
        field_parent = view.get("field_parent") or 'child_ids'
        
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        
        root = dom.childNodes[0]
        attrs = tools.node_attributes(root)
        
        self.headers = []
        self.parse(root, fields)
        
        fields = []
        
        item_model = 'comparison.item'
        
        proxy_item = rpc.RPCProxy(item_model)
        item_ids = proxy_item.search([])
        
        res = proxy_item.read(item_ids, ['name'])
        titles = []
        
        for r in res:
            title = {}
            title['sel'] = None
            if selected_items:
                item = {}
                for s in selected_items:
                    if r['id'] == s:
                        item['id'] = r['id']
                        item['type'] = 'char'
                        item['string'] = r['name']
                        item['name'] = r['name']
                        title['sel'] = True
                        
                        self.headers += [item]
            
            else:
                item = {}
                item['id'] = r['id']
                item['type'] = 'char'
                item['string'] = r['name']
                item['name'] = r['name']
                
                self.headers += [item]
            
            title['name'] = r['name']
            title['id'] = r['id']
            titles += [title]
            
        for field in self.headers:
            if field['name'] == 'name' or field['name'] == 'ponderation':
                fields += [field['name']]
        
        fields = jsonify.encode(fields)
        
        icon_name = self.headers[0].get('icon')
        
        self.url = '/comparison/data'
        self.url_params = dict(model=model, 
                                ids=ids,
                                fields=ustr(fields), 
                                domain=ustr(domain), 
                                context=ustr(context), 
                                field_parent=field_parent,
                                icon_name=icon_name)
        
        def _jsonify(obj):
            for k, v in obj.items():
                if isinstance(v, dict):
                    obj[k] = _jsonify(v)
            
            return jsonify.encode(obj)
        
        self.url_params = _jsonify(self.url_params)
        self.headers = jsonify.encode(self.headers)
        
        return dict(headers=self.headers, url_params=self.url_params, url=self.url, titles=titles, selected_items=selected_items)
    
    @expose('json')
    def data(self, ids, model, fields, field_parent=None, icon_name=None, domain=[], context={}, sort_by=None, sort_order="asc"):

        ids = ids or []
        
        if isinstance(ids, basestring):
            ids = [int(id) for id in ids.split(',')]

        if isinstance(fields, basestring):
            fields = eval(fields)

        if isinstance(domain, basestring):
            domain = eval(domain)
            
        if isinstance(context, basestring):
            context = eval(context)

        if field_parent and field_parent not in fields:
            fields.append(field_parent)

        proxy = rpc.RPCProxy(model)
        
        ctx = context or {}
        ctx.update(rpc.session.context.copy())

        if icon_name:
            fields.append(icon_name)

        fields_info = proxy.fields_get(fields, ctx)
        result = proxy.read(ids, fields, ctx)
        
        prx = rpc.RPCProxy('comparison.factor.result')
        rids = prx.search([])        
        res1 = prx.read(rids)
        
        if sort_by:
            result.sort(lambda a,b: self.sort_callback(a, b, sort_by, sort_order))

        # formate the data
        for field in fields:

            if fields_info[field]['type'] in ('float', 'integer'):
                for x in result:
                    if x[field]:
                        x[field] = '%s'%(x[field])

            if fields_info[field]['type'] in ('date',):
                for x in result:
                    if x[field]:
                        date = time.strptime(x[field], DT_FORMAT)
                        x[field] = time.strftime('%x', date)

            if fields_info[field]['type'] in ('datetime',):
                for x in result:
                    if x[field]:
                        date = time.strptime(x[field], DHM_FORMAT)
                        x[field] = time.strftime('%x %H:%M:%S', date)

            if fields_info[field]['type'] in ('one2one', 'many2one'):
                for x in result:
                    if x[field]:
                        x[field] = x[field][1]

            if fields_info[field]['type'] in ('selection'):
                for x in result:
                    if x[field]:
                        x[field] = dict(fields_info[field]['selection']).get(x[field], '')

        records = []
        for item in result:
            # empty string instead of bool and None
            for k, v in item.items():
                if v==None or (v==False and type(v)==bool):
                    item[k] = ''

            record = {}
            
            for i, j in item.items():
                for r in res1:
                    if j == r.get('factor_id')[1]:
                        item[r.get('item_id')[1]] = r.get('result') 

            record['id'] = item.pop('id')
#            record['action'] = tg_url('/tree/open', model=model, id=record['id'])
            record['target'] = None

            record['icon'] = None

            if icon_name and item.get(icon_name):
                icon = item.pop(icon_name)
                record['icon'] = icons.get_icon(icon)

                if icon == 'STOCK_OPEN':
                    record['action'] = None

            record['children'] = []

            if field_parent and field_parent in item:
                record['children'] = item.pop(field_parent) or None
                
            record['items'] = item
            records += [record]
            
        return dict(records=records)
    
    def parse(self, root, fields=None):

        for node in root.childNodes:

            if not node.nodeType==node.ELEMENT_NODE:
                continue

            attrs = tools.node_attributes(node)

            field = fields.get(attrs['name'])
            field.update(attrs)
            
            if field['name'] == 'name' or field['name'] == 'ponderation':
                self.headers += [field]
