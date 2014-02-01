# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
 Calculate total count of data while transferring.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component

class data_count(component):
    """
     Calculate total of data being transferred.

    """   
    def __init__(self, name='component.control.data_count'):        
        super(data_count, self).__init__(name=name)
        self._type = 'component.control.data_count'

    def __copy__(self):        
        res = data_count(name=self.name)
        return res

    def process(self):
        datas = {}
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    datas.setdefault(channel, 0)
                    datas[channel] += 1 
        for d in datas:
            yield {'channel': d, 'count': datas[d]}, 'main'

