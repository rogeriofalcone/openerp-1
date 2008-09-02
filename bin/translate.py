# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
##############################################################################

import sys,os
import locale
import release
import gettext
import gtk
import logging

#from tools import call_log
#locale.setlocale = call_log(locale.setlocale)
#locale.getdefaultlocale = call_log(locale.getdefaultlocale)

_LOCALE2WIN32 = {
    'af_ZA': 'Afrikaans_South Africa',
    'sq_AL': 'Albanian_Albania',
    'ar_SA': 'Arabic_Saudi Arabia',
    'eu_ES': 'Basque_Spain',
    'be_BY': 'Belarusian_Belarus',
    'bs_BA': 'Serbian (Latin)',
    'bg_BG': 'Bulgarian_Bulgaria',
    'ca_ES': 'Catalan_Spain',
    'hr_HR': 'Croatian_Croatia',
    'zh_CN': 'Chinese_China',
    'zh_TW': 'Chinese_Taiwan',
    'cs_CZ': 'Czech_Czech Republic',
    'da_DK': 'Danish_Denmark',
    'nl_NL': 'Dutch_Netherlands',
    'et_EE': 'Estonian_Estonia',
    'fa_IR': 'Farsi_Iran',
    'ph_PH': 'Filipino_Philippines',
    'fi_FI': 'Finnish_Finland',
    'fr_FR': 'French_France',
    'fr_BE': 'French_France',
    'fr_CH': 'French_France',
    'fr_CA': 'French_France',
    'ga': 'Scottish Gaelic',
    'gl_ES': 'Galician_Spain',
    'ka_GE': 'Georgian_Georgia',
    'de_DE': 'German_Germany',
    'el_GR': 'Greek_Greece',
    'gu': 'Gujarati_India',
    'he_IL': 'Hebrew_Israel',
    'hi_IN': 'Hindi',
    'hu': 'Hungarian_Hungary',
    'is_IS': 'Icelandic_Iceland',
    'id_ID': 'Indonesian_indonesia',
    'it_IT': 'Italian_Italy',
    'ja_JP': 'Japanese_Japan',
    'kn_IN': 'Kannada',
    'km_KH': 'Khmer',
    'ko_KR': 'Korean_Korea',
    'lo_LA': 'Lao_Laos',
    'lt_LT': 'Lithuanian_Lithuania',
    'lat': 'Latvian_Latvia',
    'ml_IN': 'Malayalam_India',
    'id_ID': 'Indonesian_indonesia',
    'mi_NZ': 'Maori',
    'mn': 'Cyrillic_Mongolian',
    'no_NO': 'Norwegian_Norway',
    'nn_NO': 'Norwegian-Nynorsk_Norway',
    'pl': 'Polish_Poland',
    'pt_PT': 'Portuguese_Portugal',
    'pt_BR': 'Portuguese_Brazil',
    'ro_RO': 'Romanian_Romania',
    'ru_RU': 'Russian_Russia',
    'mi_NZ': 'Maori',
    'sr_CS': 'Serbian (Cyrillic)_Serbia and Montenegro',
    'sk_SK': 'Slovak_Slovakia',
    'sl_SI': 'Slovenian_Slovenia',
    'es_ES': 'Spanish_Spain',
    'sv_SE': 'Swedish_Sweden',
    'ta_IN': 'English_Australia',
    'th_TH': 'Thai_Thailand',
    'mi_NZ': 'Maori',
    'tr_TR': 'Turkish_Turkey',
    'uk_UA': 'Ukrainian_Ukraine',
    'vi_VN': 'Vietnamese_Viet Nam',
}

def setlang(lang=None):
    APP = release.name
    DIR = os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]), 'share/locale')
    if not os.path.isdir(DIR):
        DIR = os.path.join(sys.prefix, 'share/locale')
    if not os.path.isdir(DIR):
        gettext.install(APP, unicode=1)
        return False
    if lang:
        lc, encoding = locale.getdefaultlocale()
        if encoding == 'utf':
            encoding = 'UTF-8'
        if encoding == 'cp1252':
            encoding = '1252'
        if not encoding:
            encoding = 'UTF-8'

        lang2 = lang
        if os.name == 'nt':
            lang2 = _LOCALE2WIN32.get(lang, lang)
            os.environ['LANG'] = lang
        elif os.name == 'mac':
            encoding = 'UTF-8'

        lang_enc = lang2 + '.' + encoding
        try:
            locale.setlocale(locale.LC_ALL, lang_enc)
        except:
            logging.getLogger('translate').warning(
                    _('Unable to set locale %s') % lang_enc)

        lang = gettext.translation(APP, DIR, languages=[lang], fallback=True)
        lang.install(unicode=1)
    else:
        try:
            if os.name == 'nt':
                os.environ['LANG'] = ''
            locale.setlocale(locale.LC_ALL, '')
        except:
            logging.getLogger('translate').warning( _('Unable to set locale !'))
        gettext.bindtextdomain(APP, DIR)
        gettext.textdomain(APP)
        gettext.install(APP, unicode=1)
    gtk.glade.bindtextdomain(APP, DIR)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

