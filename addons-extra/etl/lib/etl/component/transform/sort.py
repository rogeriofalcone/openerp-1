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
 To perform sort operation.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component

class sort(component):
    """
        This is an ETL Component that performs sort operation.

        Type                  : Data Component.
        Computing Performance : Semi-Streamline.
        Input Flows           : 1.
        * .*                  : The main data flow with input data.
        Output Flows          : 0-x.
        * .*                  : Returns the main flow with sort result.
    """

    def __init__(self, fieldname, name='component.transfer.sort'):
        """
        Required Parameters
        fieldname      : Specifies the field name according to which sorting process will be done.

        Extra Parameters
        name          : Name of the component.
        """
        super(sort, self).__init__(name )
        self._type = 'component.transfer.sort'
        self.fieldname = fieldname

    def __copy__(self):
        res = sort(self.fieldname, self.name)
        return res

    # Read all input channels, sort and write to 'main' channel
    def process(self):
        if self.is_start():
            self.warning('No any Input attached')
        if self.is_end():
            self.warning('No any Output attached')
        datas = []
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    datas.append(d)
        datas.sort(lambda x, y: cmp(x[self.fieldname], y[self.fieldname]))
        for d in datas:
            yield d, 'main'

def test():
    from etl_test import etl_test
    test = etl_test.etl_component_test(sort('name'))
    test.check_input({'main': [{'id': 1, 'name': 'OpenERP'}, {'id': 2, 'name': 'Fabien'}]})
    test.check_output([{'id': 2, 'name': 'Fabien'}, {'id': 1, 'name': 'OpenERP'}], 'main')
    res = test.output()

if __name__ == '__main__':
    test()
