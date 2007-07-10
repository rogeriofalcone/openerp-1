###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################################################

"""
This module implementes widget parser for form view, and
several widget components.
"""

import xml.dom.minidom

import turbogears as tg
import cherrypy

from tinyerp import icons
from tinyerp import tools
from tinyerp import rpc

from interface import TinyField
from interface import TinyWidget
from interface import TinyInputWidget
from interface import TinyCompoundWidget

import validators as tiny_validators

class Frame(TinyCompoundWidget):
    """Frame widget layouts the widgets in a table.
    """

    template = "tinyerp.widgets.templates.frame"

    params = ['table']
    member_widgets = ['children']

    table = []

    def __init__(self, attrs, children):
        """Create new instance of Frame widget."

        @param attrs: attributes
        @param children: child widgets

        @return: an instance of Frame widget
        """

        super(Frame, self).__init__(attrs)

        self.columns = int(attrs.get('col', 4))
        self.nolabel = True
        
        self.x = 0
        self.y = 0
        
        self.add_row()

        self.children = children

        for child in children:

            string = not child.nolabel and child.string
            rowspan = child.rowspan or 1
            colspan = child.colspan or 1
            
            if isinstance(child, Button) and not child.visible:
                continue
            
            if isinstance(child, NewLine):
                self.add_row()
            else:
                self.add(child, string, rowspan, colspan)

        self.fields = []

        # properly distribute widths to columns

        mx = 1
        for row in self.table:
            if len(row) > mx:
                mx = len(row)

        for row in self.table:           
                       
            sn = len([w for a, w in row if isinstance(w, basestring)])
            pn = len([w for a, w in row if isinstance(w, Image)])
            
            sw = 10                                  # label width            
            ww = (100.00 - sw * sn) / (mx - sn - pn) # widget width
                        
            for a, wid in row:
                if isinstance(wid, basestring):
                    w = sw
                elif isinstance(wid, Image):                    
                    w = 0
                else:
                    c = a.get('colspan', 1)
                    if c > mx:
                        c = 1
                        
                    w = ww * c

                a['width'] = '%d%%' % (w)

    def add_row(self):
        self.table.append([])

        self.x = 0
        self.y += 1
            
    def add(self, widget, label=None, rowspan=1, colspan=1):

        if colspan > self.columns:
            colspan = self.columns
                        
        a = label and 1 or 0
                
        if colspan + self.x + a > self.columns:
            self.add_row()

        if colspan == 1 and a == 1:
            colspan = 2
            
        tr = self.table[-1]
        
        if label: 
            colspan -= 1            
            attrs = {'class': 'label'}
            td = [attrs, label]
            tr.append(td)            

        if isinstance(widget, TinyInputWidget) and hasattr(cherrypy.request, 'terp_validators') and widget.name and widget.validator and not widget.readonly:
            cherrypy.request.terp_validators[str(widget.name)] = widget.validator
            cherrypy.request.terp_fields += [widget]

        attrs = {'class': 'item'}
        if rowspan > 1: attrs['rowspan'] = rowspan
        if colspan > 1: attrs['colspan'] = colspan        

        td = [attrs, widget]
        tr.append(td)

        self.x += colspan + a
        
class Notebook(TinyCompoundWidget):
    """Notebook widget, contains list of frames. Each frame will be displayed as a
    page of the the Notebook.
    """

    template = "tinyerp.widgets.templates.notebook"
    
    member_widgets = ['_notebook_', "children"]
    _notebook_ = tg.widgets.Tabber(use_cookie=True)
    _notebook_.css = [tg.widgets.CSSLink('tinyerp', 'css/tabs.css')]

    def __init__(self, attrs, children):
        super(Notebook, self).__init__(attrs)
        self.children = children
        self.nolabel = True
                
        self.colspan = attrs.get('colspan', 3)

class Separator(TinyField):
    """Separator widget.
    """

    params = ['string']
    template = "tinyerp.widgets.templates.separator"

    def __init__(self, attrs={}):
        super(Separator, self).__init__(attrs)

        self.colspan = 4
        self.rowspan = 1
        self.nolabel = True

class NewLine(TinyField):
    """NewLine widget just tells the Frame widget to start new row during
    layout process.
    """
    template = """ <span/> """

class Label(TinyField):

    template = """
        <div style="text-align: center; width: 100%" xmlns:py="http://purl.org/kid/ns#">
            ${field_value}
        </div>   """

    params = ["field_value"]

    def __init__(self, attrs={}):
        super(Label, self).__init__(attrs)

        self.nolabel = True
        self.field_value = self.string

    def set_value(self, value):
        self.field_value = unicode(value or '', 'utf-8')

class Char(TinyField):
    template = "tinyerp.widgets.templates.char"
    params = ['invisible']
    invisible = False
    
    def __init__(self, attrs={}):
        super(Char, self).__init__(attrs)
        self.validator = tiny_validators.String()        
        self.invisible = attrs.get('invisible', False)

    def set_value(self, value):
        self.default = value

class Email(TinyField):
    template = "tinyerp.widgets.templates.email"

    def __init__(self, attrs={}):
        super(Email, self).__init__(attrs)
        self.validator = tiny_validators.Email()

    def set_value(self, value):
        if value:
            self.default = value

class Text(TinyField):
    template = "tinyerp.widgets.templates.text"

    def __init__(self, attrs={}):
        super(Text, self).__init__(attrs)
        self.validator = tiny_validators.String()

    def set_value(self, value):
        self.default = value

class Integer(TinyField):
    template = "tinyerp.widgets.templates.integer"

    def __init__(self, attrs={}):
        super(Integer, self).__init__(attrs)
        self.validator = tiny_validators.Int()
        
        if not self.default:
            self.default = 0

    def set_value(self, value):
        if value:
            self.default = int(value)

class Boolean(TinyField):
    template = "tinyerp.widgets.templates.boolean"

    def __init__(self, attrs={}):
        super(Boolean, self).__init__(attrs)
        self.validator = tiny_validators.Bool()

    def set_value(self, value):
        self.default = value or ''

class Float(TinyField):
    template = "tinyerp.widgets.templates.float"

    def __init__(self, attrs={}):
        super(Float, self).__init__(attrs)
        self.validator = tiny_validators.Float()
        
        if not self.default:
            self.default = 0.0

    def set_value(self, value):
        self.default = value

class FloatTime(TinyField):
    template = "tinyerp.widgets.templates.floattime"

    def __init__(self, attrs={}):
        super(FloatTime, self).__init__(attrs)
        self.validator = tiny_validators.Float()

    def set_value(self, value):
        self.default = value

class Selection(TinyField):
    template = "tinyerp.widgets.templates.selection"
    
    params = ['options']
    options = []

    def __init__(self, attrs={}):
        super(Selection, self).__init__(attrs)
        self.options = attrs.get('selection', [])
        self.validator = tiny_validators.Selection()
        
    def set_value(self, value):       
        super(Selection, self).set_value(value)
        
class DateTime(TinyInputWidget, tg.widgets.CalendarDatePicker):
    template = "tinyerp.widgets.templates.datetime"

    params = ["format"]

    format = "%Y-%m-%d %H:%M:%S"
    picker_shows_time = True
    button_text = 'Select'

    css = [tg.widgets.CSSLink(tg.widgets.base.static, "calendar/skins/aqua/theme.css")]

    def __init__(self, attrs={}):
        TinyInputWidget.__init__(self, attrs)
        tg.widgets.CalendarDatePicker.__init__(self, name=self.name, not_empty=False)

        if attrs['type'] == 'date':
            self.format = "%Y-%m-%d"
            self.picker_shows_time = False
        elif attrs['type'] == 'time':
            self.format = "%H:%M:%S"

        self.validator = tiny_validators.DateTime(format=self.format)

    def set_value(self, value):
        self._default = value

class Binary(TinyField):
    template = "tinyerp.widgets.templates.binary"
    params = ["name", "text", "readonly"]
    
    text = None
    file_upload = True

    def __init__(self, attrs={}):
        super(Binary, self).__init__(attrs)
        self.validator = tiny_validators.Binary()

    def set_value(self, value):            
        if value:
            #super(Binary, self).set_value("%s bytes" % len(value))
            self.text = "%s bytes" % len(value)
            
class Url(TinyField):
    template = "tinyerp.widgets.templates.url"

    def __init__(self, attrs={}):
        super(Url, self).__init__(attrs)
        self.validator = tiny_validators.Url()

    def set_value(self, value):
        if value:
            super(Url, self).set_value(value)
            
class Hidden(TinyField):
    template = "tinyerp.widgets.templates.hidden"
    wid = None

    def __init__(self, attrs={}):
        super(Hidden, self).__init__(attrs)       
        self.wid = widgets_type[self.kind](attrs)        
        self.validator = self.wid.validator

    def set_value(self, value):
        self.wid.set_value(value)
        self.default = self.wid.default

class Button(TinyField):
    """Button widget

    @todo: use states
    @todo: actions
    """

    template = "tinyerp.widgets.templates.button"
    params = ["name", "string", "model", "btype", "id", "confirm", "icon"]

    visible = True

    def __init__(self, current_model, id=None, attrs={}):

        TinyField.__init__(self, attrs)

        self.btype = attrs.get('type', 'workflow')
        self.confirm = attrs.get('confirm', None)

        self.model = current_model
        self.id = id

        self.nolabel = True
        if 'icon' in attrs:
            self.icon = icons.get_icon(attrs['icon'])

    def set_state(self, state):
        if self.states:
            self.visible = state in self.states

class Image(TinyField):

    template = """
        <span xmlns:py="http://purl.org/kid/ns#" py:strip="">
            <img align="left" src="${src}" width="${size}" height="${size}"/>
        </span>
        """

    params = ["src", "size"]
    src = ""
    size = None
    
    def __init__(self, attrs={}):
        icon = attrs.get('name')
        attrs['name'] = attrs.get('name', 'Image').replace("-","_")

        TinyField.__init__(self, attrs)
        
        self.src =  icons.get_icon(icon)        
        self.size = attrs.get('size')        
        self.size = (self.size or None) and int(self.size)
                
class Group(TinyCompoundWidget):
    template = """
    <span xmlns:py="http://purl.org/kid/ns#" py:strip="">
        <fieldset py:if="string">
            <legend py:content="string" />
            ${frame.display(value_for(frame), **params_for(frame))}
        </fieldset>
        <span py:replace="frame.display()" py:if="not string"/>
    </span>
    """

    params = ["string"]
    member_widgets = ["frame"]
    frame = None

    def __init__(self, attrs, children):
        TinyCompoundWidget.__init__(self, attrs)

        self.frame = Frame(attrs, children)
        self.nolabel = True

class HPaned(TinyCompoundWidget):

    template = """
        <span xmlns:py="http://purl.org/kid/ns#" py:strip="">
            <table width="100%" class="hpaned">
                <tr>
                    <td valign="top" py:for="child in children" py:content="child.display(value_for(child), **params_for(child))"></td>
                </tr>
            </table>
        </span>
        """

    member_widgets = ["children"]

    def __init__(self, attrs, children):
        super(HPaned, self).__init__(attrs)
        self.children = children
        self.nolabel = True

class VPaned(TinyCompoundWidget):

    template = """
        <span xmlns:py="http://purl.org/kid/ns#" py:strip="">
            <table width="100%" class="hpaned">
                <tr py:for="child in children">
                    <td valign="top" py:content="child.display(value_for(child), **params_for(child))"></td>
                </tr>
            </table>
        </span>
        """

    member_widgets = ["children"]

    def __init__(self, attrs, children):
        super(VPaned, self).__init__(attrs)
        self.children = children
        self.nolabel = True

class Form(TinyCompoundWidget):
    """A generic form widget
    """

    template = """
        <span xmlns:py="http://purl.org/kid/ns#" py:if="frame" py:replace="frame.display(value_for(frame), **params_for(frame))"/>
        """

    member_widgets = ['frame']
    frame = None

    def __init__(self, prefix, model, view, ids=[], domain=[], context={}, editable=True, nodefault=False):
        super(Form, self).__init__()

        fields = view['fields']
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        root = dom.childNodes[0]
        attrs = tools.node_attributes(root)
        self.string = attrs.get('string', '')

        self.model = model
        self.id = None
        self.editable = editable
        
        proxy = rpc.RPCProxy(model)

        ctx = rpc.session.context.copy()
        ctx.update(context)

        values = {}
        if ids:
            values = proxy.read(ids[:1], fields.keys(), ctx)[0]
            self.id = ids[:1]

        elif 'datas' in view: # wizard data
            values = {}

            for f in fields:
                if 'value' in fields[f]:
                    values[f] = fields[f]['value']

            values.update(view['datas'])

        elif not nodefault: # default
            values = proxy.default_get(fields.keys(), ctx)

        elif 'state' in fields: # if nodefault and state get state only
            values = proxy.default_get(['state'], ctx)

        self.frame = self.parse(prefix, dom, fields, values)[0]

    def parse(self, prefix='', root=None, fields=None, values={}):

        views = []

        for node in root.childNodes:

            if not node.nodeType==node.ELEMENT_NODE:
                continue

            attrs = tools.node_attributes(node)

            attrs['prefix'] = prefix
            attrs['editable'] = self.editable
            
            if 'state' in values:
                attrs['state'] = values['state']

            attrs['model'] = attrs.get('model', self.model)
            #attrs['readonly'] = attrs.get('readonly', self.readonly)   #(For testing Binary widget remove coment...)

            if node.localName=='image':
                views += [Image(attrs)]

            elif node.localName=='separator':
                views += [Separator(attrs)]

            elif node.localName=='label':
                views += [Label(attrs)]

            elif node.localName=='newline':
                views += [NewLine(attrs)]

            elif node.localName=='button':
                views += [Button(self.model, self.id, attrs)]

            elif node.localName == 'form':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [Frame(attrs, n)]

            elif node.localName == 'notebook':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                nb = Notebook(attrs, n)
                nb.name = prefix.replace('/', '_') + '_notebook'
                views += [nb]

            elif node.localName == 'page':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [Frame(attrs, n)]

            elif node.localName=='group':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [Group(attrs, n)]

            elif node.localName == 'field':
                name = attrs['name']

                if attrs.get('widget', False):
                    if attrs['widget']=='one2many_list':
                        attrs['widget']='one2many'
                    attrs['type'] = attrs['widget']

                # XXX: update widgets also
                attrs['value'] = values.get(name, None)

                try:
                    fields[name].update(attrs)
                except:
                    print "-"*30,"\n malformed tag for :", attrs
                    print "-"*30
                    raise

                kind = fields[name]['type']

                if kind not in widgets_type:
                    continue

                field = widgets_type[kind](attrs=fields[name])

                if values.has_key(name) and isinstance(field, TinyInputWidget):
                    field.set_value(values[name])

                views += [field]

            elif node.localName=='hpaned':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [HPaned(attrs, n)]

            elif node.localName=='vpaned':
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [VPaned(attrs, n)]

            elif node.localName in ('child1', 'child2'):
                n = self.parse(prefix=prefix, root=node, fields=fields, values=values)
                views += [Frame(attrs, n)]

            elif node.localName=='action':
                views += [Action(attrs)]

        return views

from action import Action
from many2one import M2O
from one2many import O2M
from many2many import M2M
from reference import Reference
from texttag import TinyMCE

widgets_type = {
    'date': DateTime,
    'time': DateTime,
    'float_time': FloatTime,
    'datetime': DateTime,
    'float': Float,
    'integer': Integer,
    'selection': Selection,
    'char': Char,
    'boolean': Boolean,
    'button': Button,
    'reference': Reference,
    'binary': Binary,
    #'picture': Picture,
    'text': Text,
    'text_tag': TinyMCE,
    'one2many': O2M,
    'one2many_form': O2M,
    'one2many_list': O2M,
    'many2many': M2M,
    'many2one': M2O,
    'email' : Email,
    'url' : Url,
    'image' : Image
}
