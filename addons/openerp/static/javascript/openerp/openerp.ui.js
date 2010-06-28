////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
//
// $Id$
//
// Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
//
// The OpenERP web client is distributed under the "OpenERP Public License".
// It's based on Mozilla Public License Version (MPL) 1.1 with following 
// restrictions:
//
// -   All names, links and logos of Tiny, Open ERP and Axelor must be 
//     kept as in original distribution without any changes in all software 
//     screens, especially in start-up page and the software header, even if 
//     the application source code has been changed or updated or code has been 
//     added.
//
// -   All distributions of the software must keep source code with OEPL.
// 
// -   All integrations to any other software must keep source code with OEPL.
//
// If you need commercial licence to remove this kind of restriction please
// contact us.
//
// You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
//
////////////////////////////////////////////////////////////////////////////////

if (typeof(openobject.dom) == "undefined") {
    throw "openobject.dom is required by 'openerp.ui'.";
}

if (typeof(openerp) == "undefined") {
    openerp = {};
}

openerp.ui = {};

function toggle_sidebar() {
    function a() {
        jQuery('#tertiary').toggleClass('sidebar-open sidebar-closed');
    }
    if (typeof(Notebook) == "undefined") {
        a();
    } else {
        Notebook.adjustSize(a);
    }

    MochiKit.Signal.signal(document, 'toggle_sidebar');
}
