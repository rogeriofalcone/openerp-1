
openerp.web.formats = function(openerp) {
var _t = openerp.web._t;

/**
 * Intersperses ``separator`` in ``str`` at the positions indicated by
 * ``indices``.
 *
 * ``indices`` is an array of relative offsets (from the previous insertion
 * position, starting from the end of the string) at which to insert
 * ``separator``.
 *
 * There are two special values:
 *
 * ``-1``
 *   indicates the insertion should end now
 * ``0``
 *   indicates that the previous section pattern should be repeated (until all
 *   of ``str`` is consumed)
 *
 * @param {String} str
 * @param {Array<Number>} indices
 * @param {String} separator
 * @returns {String}
 */
openerp.web.intersperse = function (str, indices, separator) {
    separator = separator || '';
    var result = [], last = str.length;

    for(var i=0; i<indices.length; ++i) {
        var section = indices[i];
        if (section === -1 || last <= 0) {
            // Done with string, or -1 (stops formatting string)
            break;
        } else if(section === 0 && i === 0) {
            // repeats previous section, which there is none => stop
            break;
        } else if (section === 0) {
            // repeat previous section forever
            //noinspection AssignmentToForLoopParameterJS
            section = indices[--i];
        }
        result.push(str.substring(last-section, last));
        last -= section;
    }

    var s = str.substring(0, last);
    if (s) { result.push(s); }
    return result.reverse().join(separator);
};
/**
 * Insert "thousands" separators in the provided number (which is actually
 * a string)
 *
 * @param {String} num
 * @returns {String}
 */
openerp.web.insert_thousand_seps = function (num) {
    var negative = num[0] === '-';
    num = (negative ? num.slice(1) : num);
    return (negative ? '-' : '') + openerp.web.intersperse(
        num, _t.database.parameters.grouping, _t.database.parameters.thousands_sep);
};
/**
 * Formats a single atomic value based on a field descriptor
 *
 * @param {Object} value read from OpenERP
 * @param {Object} descriptor union of orm field and view field
 * @param {Object} [descriptor.widget] widget to use to display the value
 * @param {Object} descriptor.type fallback if no widget is provided, or if the provided widget is unknown
 * @param {Object} [descriptor.digits] used for the formatting of floats
 * @param {String} [value_if_empty=''] returned if the ``value`` argument is considered empty
 */
openerp.web.format_value = function (value, descriptor, value_if_empty) {
    // If NaN value, display as with a `false` (empty cell)
    if (typeof value === 'number' && isNaN(value)) {
        value = false;
    }
    //noinspection FallthroughInSwitchStatementJS
    switch (value) {
        case '':
            if (descriptor.type === 'char') {
                return '';
            }
            console.warn('Field', descriptor, 'had an empty string as value, treating as false...');
        case false:
        case Infinity:
        case -Infinity:
            return value_if_empty === undefined ?  '' : value_if_empty;
    }
    var l10n = _t.database.parameters;
    switch (descriptor.widget || descriptor.type) {
        case 'integer':
            return openerp.web.insert_thousand_seps(
                _.str.sprintf('%d', value));
        case 'float':
            var precision = descriptor.digits ? descriptor.digits[1] : 2;
            var formatted = _.str.sprintf('%.' + precision + 'f', value).split('.');
            formatted[0] = openerp.web.insert_thousand_seps(formatted[0]);
            return formatted.join(l10n.decimal_point);
        case 'float_time':
            return _.str.sprintf("%02d:%02d",
                    Math.floor(value),
                    Math.round((value % 1) * 60));
        case 'progressbar':
            return _.str.sprintf(
                '<progress value="%.2f" max="100.0">%.2f%%</progress>',
                    value, value);
        case 'many2one':
            // name_get value format
            return value[1];
        case 'datetime':
            if (typeof(value) == "string")
                value = openerp.web.auto_str_to_date(value);

            return value.format(l10n.date_format
                        + ' ' + l10n.time_format);
        case 'date':
            if (typeof(value) == "string")
                value = openerp.web.auto_str_to_date(value);
            return value.format(l10n.date_format);
        case 'time':
            if (typeof(value) == "string")
                value = openerp.web.auto_str_to_date(value);
            return value.format(l10n.time_format);
        case 'selection':
            // Each choice is [value, label]
            var result = _(descriptor.selection).detect(function (choice) {
                return choice[0] === value;
            });
            if (result) { return result[1]; }
            return;
        default:
            return value;
    }
};

openerp.web.parse_value = function (value, descriptor, value_if_empty) {
    var date_pattern = Date.normalizeFormat(_t.database.parameters.date_format),
        time_pattern = Date.normalizeFormat(_t.database.parameters.time_format);
    switch (value) {
        case false:
        case "":
            return value_if_empty === undefined ?  false : value_if_empty;
    }
    switch (descriptor.widget || descriptor.type) {
        case 'integer':
            var tmp;
            do {
                tmp = value;
                value = value.replace(openerp.web._t.database.parameters.thousands_sep, "");
            } while(tmp !== value);
            tmp = Number(value);
            if (isNaN(tmp))
                throw new Error(value + " is not a correct integer");
            return tmp;
        case 'float':
            var tmp = Number(value);
            if (!isNaN(tmp))
                return tmp;

            var tmp2 = value;
            do {
                tmp = tmp2;
                tmp2 = tmp.replace(openerp.web._t.database.parameters.thousands_sep, "");
            } while(tmp !== tmp2);
            var reformatted_value = tmp.replace(openerp.web._t.database.parameters.decimal_point, ".");
            var parsed = Number(reformatted_value);
            if (isNaN(parsed))
                throw new Error(value + " is not a correct float");
            return parsed;
        case 'float_time':
            var float_time_pair = value.split(":");
            if (float_time_pair.length != 2)
                return openerp.web.parse_value(value, {type: "float"});
            var hours = openerp.web.parse_value(float_time_pair[0], {type: "integer"});
            var minutes = openerp.web.parse_value(float_time_pair[1], {type: "integer"});
            return hours + (minutes / 60);
        case 'progressbar':
            return openerp.web.parse_value(value, {type: "float"});
        case 'datetime':
            var datetime = Date.parseExact(
                    value, (date_pattern + ' ' + time_pattern));
            if (datetime !== null)
                return openerp.web.datetime_to_str(datetime);
            datetime = Date.parse(value);
            if (datetime !== null)
                return openerp.web.datetime_to_str(datetime);
            throw new Error(value + " is not a valid datetime");
        case 'date':
            var date = Date.parseExact(value, date_pattern);
            if (date !== null)
                return openerp.web.date_to_str(date);
            date = Date.parse(value);
            if (date !== null)
                return openerp.web.date_to_str(date);
            throw new Error(value + " is not a valid date");
        case 'time':
            var time = Date.parseExact(value, time_pattern);
            if (time !== null)
                return openerp.web.time_to_str(time);
            time = Date.parse(value);
            if (time !== null)
                return openerp.web.time_to_str(time);
            throw new Error(value + " is not a valid time");
    }
    return value;
};

openerp.web.auto_str_to_date = function(value, type) {
    try {
        return openerp.web.str_to_datetime(value);
    } catch(e) {}
    try {
        return openerp.web.str_to_date(value);
    } catch(e) {}
    try {
        return openerp.web.str_to_time(value);
    } catch(e) {}
    throw new Error("'" + value + "' is not a valid date, datetime nor time");
};

openerp.web.auto_date_to_str = function(value, type) {
    switch(type) {
        case 'datetime':
            return openerp.web.datetime_to_str(value);
        case 'date':
            return openerp.web.date_to_str(value);
        case 'time':
            return openerp.web.time_to_str(value);
        default:
            throw new Error(type + " is not convertible to date, datetime nor time");
    }
};

/**
 * Formats a provided cell based on its field type
 *
 * @param {Object} row_data record whose values should be displayed in the cell
 * @param {Object} column column descriptor
 * @param {"button"|"field"} column.tag base control type
 * @param {String} column.type widget type for a field control
 * @param {String} [column.string] button label
 * @param {String} [column.icon] button icon
 * @param {String} [value_if_empty=''] what to display if the field's value is ``false``
 * @param {Boolean} [process_modifiers=true] should the modifiers be computed ?
 */
openerp.web.format_cell = function (row_data, column, value_if_empty, process_modifiers) {
    var attrs = {};
    if (process_modifiers !== false) {
        attrs = column.modifiers_for(row_data);
    }
    if (attrs.invisible) { return ''; }
    if (column.tag === 'button') {
        return [
            '<button type="button" title="', column.string || '', '">',
                '<img src="/web/static/src/img/icons/', column.icon, '.png"',
                    ' alt="', column.string || '', '"/>',
            '</button>'
        ].join('')
    }

    if (!row_data[column.id]) {
        return value_if_empty === undefined ? '' : value_if_empty;
    }
    return openerp.web.format_value(
            row_data[column.id].value, column, value_if_empty);
}
    
};
