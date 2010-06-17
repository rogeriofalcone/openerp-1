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

if (typeof(openerp.ui) == "undefined") {
    throw "openerp.ui is required by 'openerp.ui.textarea'.";
}

openerp.ui.WaitBox = function(options) {
    this.__init__(options);
};

openerp.ui.WaitBox.prototype = {

    __init__ : function(options) {
        
        this.options = MochiKit.Base.update({
        }, options || {});

        this.layer = openobject.dom.get('WaitBoxLayer');
        this.box = openobject.dom.get('WaitBox');
        
        if (!this.layer) {
            var title = this.options.title || _("Please wait...");
            var desc = this.options.description || _("This operation may take a while...");
            
            var info = DIV(null,
                    DIV({'class': 'WaitTitle'}, title),
                    DIV({'class': 'WaitImage'}, desc));
        
            this.layer = DIV({id: 'WaitBoxLayer'});
            appendChildNodes(document.body, this.layer);
    
            this.box = DIV({id: 'WaitBox'});
            appendChildNodes(document.body, this.box);
        
            appendChildNodes(this.box, info);
        }
    },

    /**
     * Cancels and deletes the internal timer, if there is any.
     */
    clearTimeout : function () {
        clearTimeout(this.timeout);
        delete this.timeout;
    },

    show : function() {
        this.clearTimeout();
        
        var vd = elementDimensions(document.body);
        var md = elementDimensions(this.box);

        var x = (vd.w / 2) - (md.w / 2);
        var y = (vd.h / 2) - (md.h / 2);
        
        setElementPosition(this.box,{
            x: Math.max(0, x), y: Math.max(0, y)});

        showElement(this.layer);
        showElement(this.box);
    },

    /**
     * Shows the wait box after the specified delay, unless it's explicitly showed or hidden before that.
     *
     * Creates and sets an internal timer accessible via @property timeout, this is a normal setTimeout return
     * value.
     *
     * @param delay delay before actually showing the wait box, in milliseconds (same as setTimeout)
     * @returns this
     */
    showAfter : function(delay) {
        // in case we already have a timeout, override it?
        this.clearTimeout();
        this.timeout = setTimeout(jQuery.proxy(function () {
            this.show();
        }, this), delay);
        return this;
    },

    hide : function() {
        this.clearTimeout();
        hideElement(this.box);
        hideElement(this.layer);
    }
};
