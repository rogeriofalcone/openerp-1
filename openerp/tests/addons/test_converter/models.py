# -*- coding: utf-8 -*-
from openerp.osv import orm, fields

class test_model(orm.Model):
    _name = 'test_converter.test_model'

    _columns = {
        'char': fields.char(),
        'integer': fields.integer(),
        'float': fields.float(),
        'numeric': fields.float(digits=(16, 2)),
        'many2one': fields.many2one('test_converter.test_model.sub'),
        'binary': fields.binary(),
        'date': fields.date(),
        'datetime': fields.datetime(),
        'selection': fields.selection([
            (1, "réponse A"),
            (2, "réponse B"),
            (3, "réponse C"),
            (4, "réponse D"),
        ]),
        'selection_str': fields.selection([
            ('A', "Qu'il n'est pas arrivé à Toronto"),
            ('B', "Qu'il était supposé arriver à Toronto"),
            ('C', "Qu'est-ce qu'il fout ce maudit pancake, tabernacle ?"),
            ('D', "La réponse D"),
        ], string="Lorsqu'un pancake prend l'avion à destination de Toronto et "
                  "qu'il fait une escale technique à St Claude, on dit:"),
        'html': fields.html(),
        'text': fields.text(),
    }

class test_model_sub(orm.Model):
    _name = 'test_converter.test_model.sub'

    _columns = {
        'name': fields.char()
    }
