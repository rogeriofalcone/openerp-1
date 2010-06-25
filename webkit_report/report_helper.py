# -*- encoding: utf-8 -*-
#
#  report_helper.py
#
#  Created by Nicolas Bessi  
#
#  Copyright (c) 2010 CamptoCamp. All rights reserved.
##############################################################################
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
##############################################################################
"""Various helper that can be called inside HTML"""
import netsvc
from osv import fields, osv
import pooler
import base64

class WebKitHelper(object):
    """Set of usefull report helper"""
    def __init__(self, cursor, uid, report_id, context):
        "constructor"
        self.cursor = cursor
        self.uid = uid
        self.pool = pooler.get_pool(self.cursor.dbname)
        self.report_id = report_id
        
    def embeed_image(self, extention, img, width=0, height=0) :
        "Transform a DB image into an embeeded HTML image"
        try:
            if width :
                width = 'width="%spx"'%(width)
            else :
                width = ' '
            if height :
                height = 'width="%spx"'%(height)
            else :
                height = ' '
            toreturn = '<img %s %s src="data:image/%s;base64,%s">'%(
                width,
                height,
                extention, 
                str(img))
            return toreturn
        except Exception, exp:
            print exp
            return 'No image'
            
            
    def get_logo_by_name(self, name):
        """Return logo by name"""
        header_obj = self.pool.get('ir.header_img')
        header_img_id = header_obj.search(
                                            self.cursor, 
                                            self.uid, 
                                            [('name','=',name)]
                                        )
        if not header_img_id :
            return u''
        if isinstance(header_img_id, list):
            header_img_id = header_img_id[0]

        head = header_obj.browse(self.cursor, self.uid, header_img_id)
        return (head.img, head.extention)
            
    def embeed_logo_by_name(self, name) :
        """Return HTML embeeded logo by name"""
        img, extention = self.get_logo_by_name(name)
        return self.embeed_image(extention, img)
        