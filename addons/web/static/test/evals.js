openerp.testing.section('eval.types', {
    dependencies: ['web.coresetup']
}, function (test) {
    test('strftime', function (instance) {
        var d = new Date();
        var context = instance.web.pyeval.context();
        strictEqual(
            py.eval("time.strftime('%Y')", context),
            String(d.getFullYear()));
        strictEqual(
            py.eval("time.strftime('%Y')+'-01-30'", context),
            String(d.getFullYear()) + '-01-30');
        strictEqual(
            py.eval("time.strftime('%Y-%m-%d %H:%M:%S')", context),
            _.str.sprintf('%04d-%02d-%02d %02d:%02d:%02d',
                d.getFullYear(), d.getMonth() + 1, d.getDate(),
                d.getHours(), d.getMinutes(), d.getSeconds()));
    });
});
openerp.testing.section('eval.contexts', {
    dependencies: ['web.coresetup']
}, function (test) {
    test('context_recursive', function (instance) {
        var context_to_eval = [{
            __ref: 'context',
            __debug: '{"foo": context.get("bar", "qux")}'
        }];
        deepEqual(
            instance.web.pyeval.eval('contexts', context_to_eval, {bar: "ok"}),
            {foo: 'ok'});
        deepEqual(
            instance.web.pyeval.eval('contexts', context_to_eval, {bar: false}),
            {foo: false});
        deepEqual(
            instance.web.pyeval.eval('contexts', context_to_eval),
            {foo: 'qux'});
    });
    test('context_sequences', function (instance) {
        // Context n should have base evaluation context + all of contexts
        // 0..n-1 in its own evaluation context
        var active_id = 4;
        var result = instance.web.pyeval.eval('contexts', [
            {
                "__contexts": [
                    {
                        "department_id": false,
                        "lang": "en_US",
                        "project_id": false,
                        "section_id": false,
                        "tz": false,
                        "uid": 1
                    },
                    { "search_default_create_uid": 1 },
                    {}
                ],
                "__eval_context": null,
                "__ref": "compound_context"
            },
            {
                "active_id": active_id,
                "active_ids": [ active_id ],
                "active_model": "purchase.requisition"
            },
            {
                "__debug": "{'record_id' : active_id}",
                "__id": "63e8e9bff8a6",
                "__ref": "context"
            }
        ]);

        deepEqual(result, {
            department_id: false,
            lang: 'en_US',
            project_id: false,
            section_id: false,
            tz: false,
            uid: 1,
            search_default_create_uid: 1,
            active_id: active_id,
            active_ids: [active_id],
            active_model: 'purchase.requisition',
            record_id: active_id
        });
    });
    test('non-literal_eval_contexts', function (instance) {
        var result = instance.web.pyeval.eval('contexts', [{
            "__ref": "compound_context",
            "__contexts": [
                {"__ref": "context", "__debug": "{'type':parent.type}",
                 "__id": "462b9dbed42f"}
            ],
            "__eval_context": {
                "__ref": "compound_context",
                "__contexts": [{
                        "__ref": "compound_context",
                        "__contexts": [
                            {"__ref": "context", "__debug": "{'type': type}",
                             "__id": "16a04ed5a194"}
                        ],
                        "__eval_context": {
                            "__ref": "compound_context",
                            "__contexts": [
                                {"lang": "en_US", "tz": false, "uid": 1,
                                 "journal_type": "sale", "section_id": false,
                                 "default_type": "out_invoice",
                                 "type": "out_invoice", "department_id": false},
                                {"id": false, "journal_id": 10,
                                 "number": false, "type": "out_invoice",
                                 "currency_id": 1, "partner_id": 4,
                                 "fiscal_position": false,
                                 "date_invoice": false, "period_id": false,
                                 "payment_term": false, "reference_type": "none",
                                 "reference": false, "account_id": 440,
                                 "name": false, "invoice_line": [],
                                 "tax_line": [], "amount_untaxed": 0,
                                 "amount_tax": 0, "reconciled": false,
                                 "amount_total": 0, "state": "draft",
                                 "residual": 0, "company_id": 1,
                                 "date_due": false, "user_id": 1,
                                 "partner_bank_id": false, "origin": false,
                                 "move_id": false, "comment": false,
                                 "payment_ids": [[6, false, []]],
                                 "active_id": false, "active_ids": [],
                                 "active_model": "account.invoice",
                                 "parent": {}}
                    ], "__eval_context": null}
                }, {
                    "id": false,
                    "product_id": 4,
                    "name": "[PC1] Basic PC",
                    "quantity": 1,
                    "uos_id": 1,
                    "price_unit": 100,
                    "account_id": 853,
                    "discount": 0,
                    "account_analytic_id": false,
                    "company_id": false,
                    "note": false,
                    "invoice_line_tax_id": [[6, false, [1]]],
                    "active_id": false,
                    "active_ids": [],
                    "active_model": "account.invoice.line",
                    "parent": {
                        "id": false, "journal_id": 10, "number": false,
                        "type": "out_invoice", "currency_id": 1,
                        "partner_id": 4, "fiscal_position": false,
                        "date_invoice": false, "period_id": false,
                        "payment_term": false, "reference_type": "none",
                        "reference": false, "account_id": 440, "name": false,
                        "tax_line": [], "amount_untaxed": 0, "amount_tax": 0,
                        "reconciled": false, "amount_total": 0,
                        "state": "draft", "residual": 0, "company_id": 1,
                        "date_due": false, "user_id": 1,
                        "partner_bank_id": false, "origin": false,
                        "move_id": false, "comment": false,
                        "payment_ids": [[6, false, []]]}
                }],
                "__eval_context": null
            }
        }]);
        deepEqual(result, {type: 'out_invoice'});
    });
});
openerp.testing.section('eval.contexts', {
    dependencies: ['web.coresetup', 'web.dates']
}, function (test) {
    test('current_date', function (instance) {
        var current_date = instance.web.date_to_str(new Date());
        var result = instance.web.pyeval.eval('domains',
            [[],{"__ref":"domain","__debug":"[('name','>=',current_date),('name','<=',current_date)]","__id":"5dedcfc96648"}],
            instance.web.pyeval.context());
        deepEqual(result, [
            ['name', '>=', current_date],
            ['name', '<=', current_date]
        ]);
    });
    test('context_freevar', function (instance) {
        var domains_to_eval = [{
            __ref: 'domain',
            __debug: '[("foo", "=", context.get("bar", "qux"))]'
        }, [['bar', '>=', 42]]];
        deepEqual(
            instance.web.pyeval.eval('domains', domains_to_eval, {bar: "ok"}),
            [['foo', '=', 'ok'], ['bar', '>=', 42]]);
        deepEqual(
            instance.web.pyeval.eval('domains', domains_to_eval, {bar: false}),
            [['foo', '=', false], ['bar', '>=', 42]]);
        deepEqual(
            instance.web.pyeval.eval('domains', domains_to_eval),
            [['foo', '=', 'qux'], ['bar', '>=', 42]]);
    });
});
openerp.testing.section('eval.groupbys', {
    dependencies: ['web.coresetup']
}, function (test) {
    test('groupbys_00', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            {group_by: ['bar', 'qux']},
            {group_by: null},
            {group_by: 'grault'}
        ]);
        deepEqual(result, ['foo', 'bar', 'qux', 'grault']);
    });
    test('groupbys_01', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            { __ref: 'context', __debug: '{"group_by": "bar"}' },
            {group_by: 'grault'}
        ]);
        deepEqual(result, ['foo', 'bar', 'grault']);
    });
    test('groupbys_02', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            {
                __ref: 'compound_context',
                __contexts: [ {group_by: 'bar'} ],
                __eval_context: null
            },
            {group_by: 'grault'}
        ]);
        deepEqual(result, ['foo', 'bar', 'grault']);
    });
    test('groupbys_03', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            {
                __ref: 'compound_context',
                __contexts: [
                    { __ref: 'context', __debug: '{"group_by": value}' }
                ],
                __eval_context: { value: 'bar' }
            },
            {group_by: 'grault'}
        ]);
        deepEqual(result, ['foo', 'bar', 'grault']);
    });
    test('groupbys_04', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            {
                __ref: 'compound_context',
                __contexts: [
                    { __ref: 'context', __debug: '{"group_by": value}' }
                ],
                __eval_context: { value: 'bar' }
            },
            {group_by: 'grault'}
        ], { value: 'bar' });
        deepEqual(result, ['foo', 'bar', 'grault']);
    });
    test('groupbys_05', function (instance) {
        var result = instance.web.pyeval.eval('groupbys', [
            {group_by: 'foo'},
            { __ref: 'context', __debug: '{"group_by": value}' },
            {group_by: 'grault'}
        ], { value: 'bar' });
        deepEqual(result, ['foo', 'bar', 'grault']);
    });
});
