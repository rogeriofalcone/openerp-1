# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

import time
from report import report_sxw
import pooler
from mx import DateTime
from report.interface import report_rml
from tools import to_xml

#from addons.account.wizard import wizard_account_balance_report

class survey_analysis(report_rml):
    def create(self, cr, uid, ids, datas, context):
        rml=''
        surv_obj = pooler.get_pool(cr.dbname).get('survey')
        for survey in surv_obj.browse(cr,uid,ids):
            rml="""
                    <document filename="test.pdf">
                    <template pageSize="(595.0,842.0)" title="Test" author="Martin Simon" allowSplitting="20">
                        <pageTemplate id="first">
                          <frame id="first" x1="57.0" y1="57.0" width="481" height="728"/>
                    </pageTemplate>
  </template>
  <stylesheet>
    <blockTableStyle id="Standard_Outline">
      <blockAlignment value="LEFT"/>
      <blockValign value="TOP"/>
    </blockTableStyle>
    <blockTableStyle id="Table1">
      <blockAlignment value="LEFT"/>
      <blockValign value="TOP"/>
      <lineStyle kind="LINEBELOW" colorName="#e6e6e6"/>
    </blockTableStyle>
    <blockTableStyle id="Table2">
      <blockAlignment value="LEFT"/>
      <blockValign value="TOP"/>
    </blockTableStyle>
    <blockTableStyle id="Table3">
      <blockAlignment value="LEFT"/>
      <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="1,0" stop="2,-1"/>
      <blockValign value="TOP"/>
    </blockTableStyle>
    <blockTableStyle id="Table4">
      <blockAlignment value="LEFT"/>
      <blockValign value="TOP"/>
      <lineStyle kind="LINEBELOW" colorName="#000000" start="0,-1" stop="1,-1"/>
    </blockTableStyle>
    <blockTableStyle id="Table5">
      <blockAlignment value="LEFT"/>
      <blockValign value="TOP"/>
      <lineStyle kind="LINEBELOW" colorName="#8f8f8f" start="0,-1" stop="1,-1"/>
    </blockTableStyle>
    <initialize>
      <paraStyle name="all" alignment="justify"/>
    </initialize>
    <paraStyle name="P1" fontName="helvetica"/>
    <paraStyle name="answer_right" alignment="RIGHT" fontName="helvetica" fontSize="09.0" leftIndent="2.0"/>
    <paraStyle name="Standard1" fontName="helvetica-bold" alignment="RIGHT" fontSize="09.0"/>
    <paraStyle name="Standard" alignment="LEFT" fontName="Helvetica-Bold" fontSize="11.0"/>
    <paraStyle name="header1" fontName="Helvetica" fontSize="11.0"/>
    <paraStyle name="Standard2" fontName="Helvetica-bold" fontSize="11.0"/>
    <paraStyle name="response" fontName="Helvetica-oblique" fontSize="9.5"/>
    <paraStyle name="page" fontName="helvetica" fontSize="11.0" leftIndent="0.0"/>
    <paraStyle name="question" fontName="helvetica-boldoblique" fontSize="10.0" leftIndent="3.0"/>
    <paraStyle name="answer" fontName="helvetica" fontSize="09.0" leftIndent="2.0"/>
    <paraStyle name="Heading" fontName="Helvetica" fontSize="14.0" leading="17" spaceBefore="12.0" spaceAfter="6.0"/>
    <paraStyle name="Text body" fontName="helvetica" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="List" fontName="helvetica" spaceBefore="0.0" spaceAfter="6.0"/>
    <paraStyle name="Caption" fontName="helvetica" fontSize="12.0" leading="15" spaceBefore="6.0" spaceAfter="6.0"/>
    <paraStyle name="Title" fontName="helvetica" fontSize="20.0" leading="15" spaceBefore="6.0" spaceAfter="6.0" alignment="CENTER"/>
    <paraStyle name="Index" fontName="helvetica"/>
    <paraStyle name="Table Contents" fontName="helvetica"/>
  </stylesheet>
  <images/>
  <story>
                    <para style="Title"><u>Response Summary</u></para>
                    <para style="Standard"><font></font></para>
                    <para style="Standard"><font></font></para>
                    <para style="Standard"><font></font></para>
                    <para style="Standard"><font></font></para>
                    <para style="Standard"><font></font></para>
                    <para style="Standard"><font></font></para>
                    <!--para style="Standard">[[repeatIn(objects,'y')]]</para-->
                    <para style="Standard"><font></font></para>
                    <blockTable colWidths="95,215,150,40" style="Table2">
                      <tr>
                        <td><para style="Standard">Survey Title :-</para></td>
                        <td><para style="header1">""" + to_xml(survey.title) + """</para></td>
                        <td><para style="Standard">Total Started Survey :- </para></td>
                        <td><para style="header1">""" + str(survey.tot_start_survey)  + """</para></td>
                      </tr>
                      <tr>
                        <td><para style="Standard"></para></td>
                        <td><para style="header1"></para></td>
                        <td><para style="Standard">Total Completed Survey :-</para></td>
                        <td><para style="header1">""" + str(survey.tot_comp_survey) + """</para></td>
                      </tr>
                    </blockTable> """
            for page in survey.page_ids:
                rml += """ <blockTable colWidths="500" style="Table4">
#                              <tr>
#                                <td><para style="page">Page :- """ + to_xml(page.title) + """</para></td>
#                              </tr>
#                           </blockTable>"""
                for que in page.question_ids:
                    rml +="""<blockTable colWidths="500" style="Table5">
                              <tr>
                                <td><para style="question">Que: """+ to_xml(que.question) + """</para></td>
                              </tr>
                             </blockTable>"""
                    cols_widhts = []
                    if que.type in ['matrix_of_choices_only_one_ans','matrix_of_choices_only_multi_ans']:
                        cols_widhts.append(200)
                        for col in range(0, len(que.column_heading_ids)+1):
                            cols_widhts.append(float(300/(len(que.column_heading_ids)+1)))
                        colWidths = ",".join(map(str, cols_widhts))
                        matrix_ans = ['',]
                        
                        for col in que.column_heading_ids:
                            if col.title not in matrix_ans:
                                matrix_ans.append(col.title)
                        rml+="""<blockTable colWidths=" """ + colWidths + """ " style="Table1"><tr>"""
                        
                        for mat_col in matrix_ans:
                            rml+="""<td><para style="response">""" + to_xml(mat_col) + """</para></td>"""
                        rml+="""<td><para style="response">Response Count</para></td>"""
                        rml+="""</tr>"""
                        
                        for ans in que.answer_choice_ids:
                            rml+="""<tr><td><para style="answer">""" + to_xml(ans.answer) + """</para></td>"""
                            cr.execute("select count(id) from survey_response_answer sra where sra.answer_id = %d"%(ans.id))
                            tot_res = cr.fetchone()[0]
                            cr.execute("select count(id) ,sra.answer from survey_response_answer sra where sra.answer_id = %d group by sra.answer"%ans.id)
                            calc_res = cr.dictfetchall()
                            for mat_col in range(1, len(matrix_ans)):
                                percantage = 0
                                cal_count = 0
                                for cal in calc_res:
                                    if cal['answer'] == matrix_ans[mat_col]:
                                        cal_count = cal['count']
                                if tot_res:
                                    percantage = float(cal_count)*100 / tot_res 
                                rml += """<td color="#FFF435"><para style="answer">""" + str(percantage) +"% (" + str(cal_count) + """)</para></td>"""
                            
                            rml+="""<td><para style="response">""" + str(tot_res) + """</para></td>"""
                            rml += """</tr>"""
                        
                        rml+="""</blockTable>"""

                    elif que.type in['multiple_choice_only_one_ans', 'multiple_choice_multiple_ans', 'multiple_textboxes','date_and_time','date']:
                        rml +="""<blockTable colWidths="280.0,120,100.0" style="Table1">"""
                        rml += """ <tr> 
                             <td> <para style="Standard"> </para></td> 
                             <td> <para style="response">Response Percentage </para></td>
                             <td> <para style="response">Response Count</para></td>                 
                         </tr>"""
                        for ans in que.answer_choice_ids:
                            rml+="""<tr><td><para style="answer">""" + to_xml(ans.answer) + """</para></td>
                                    <td><para style="answer">""" + str(ans.average) + """%</para></td>
                                    <td><para style="answer">""" + str(ans.response) + """</para></td></tr>"""
                        rml+="""</blockTable>"""

                    elif que.type in['single_textbox']:
                        cr.execute("select count(id) from survey_response where question_id = %d and single_text!=''" % que.id)
                        rml +="""<blockTable colWidths="400.0,100.0" style="Table1">
                             <tr> 
                                 <td> <para style="Standard"> </para></td> 
                                 <td> <para style="response">Response Count</para></td>                 
                             </tr>
                            <tr><td><para style="answer"></para></td>
                                <td><para style="answer">""" + str(cr.fetchone()[0]) + """ </para></td></tr>
                            </blockTable>"""
                            
                    elif que.type in['comment']:
                        cr.execute("select count(id) from survey_response where question_id = %d and comment !=''" % que.id)
                        rml +="""<blockTable colWidths="400.0,100.0" style="Table1">
                             <tr> 
                                 <td> <para style="Standard"> </para></td> 
                                 <td> <para style="response">Response Count</para></td>                 
                             </tr>
                            <tr><td><para style="answer"></para></td>
                                <td><para style="answer">""" + str(cr.fetchone()[0]) + """ </para></td></tr>
                            </blockTable>"""
                            
                    elif que.type in['rating_scale']:
                        cols_widhts.append(200)
                        for col in range(0,len(que.column_heading_ids)+2):
                            cols_widhts.append(float(300/(len(que.column_heading_ids) +2)))
                        colWidths = ",".join(map(str, cols_widhts))
                        ans_td=''
                        que_td=''
                        matrix_ans = ['',]
                        for col in que.column_heading_ids:
                            if col.title not in matrix_ans:
                                matrix_ans.append(col.title)
                        rml+="""<blockTable colWidths=" """ + colWidths + """ " style="Table1"><tr>"""
                        for mat_col in matrix_ans:
                            rml+="""<td><para style="response">""" + to_xml(mat_col) + """</para></td>"""
                        rml+="""<td><para style="response">Rating Average</para></td>"""
                        rml+="""<td><para style="response">Response Count</para></td>"""
                        rml+="""</tr>"""
                        for ans in que.answer_choice_ids:
                            rml+="""<tr><td><para style="answer">""" + to_xml(ans.answer) + """</para></td>"""
                            res_count = 0
                            rating_weight_sum = 0
                            for mat_col in range(1, len(matrix_ans)):
                                cr.execute("select count(sra.answer_id) from survey_response sr, survey_response_answer sra\
                                     where sr.id = sra.response_id and  sra.answer_id = %d and sra.answer ='%s'"%(ans.id,matrix_ans[mat_col]))
                                tot_res = cr.fetchone()[0]
                                cr.execute("select count(sra.answer_id),sqc.rating_weight from survey_response sr, survey_response_answer sra ,\
                                        survey_question_column_heading sqc where sr.id = sra.response_id and \
                                        sqc.question_id = sr.question_id  and sra.answer_id = %d and sqc.title ='%s'\
                                        group by sra.answer_id,sqc.rating_weight"%(ans.id,matrix_ans[mat_col]))
                                col_weight =  cr.fetchone()
                                res_count = col_weight[0]
                                if tot_res:
                                    rating_weight_sum += col_weight[1] * tot_res
                                    tot_per = round((float(tot_res) * 100)/ int(res_count),2)
                                else:
                                    tot_res = 0
                                    tot_per = 0.0
                                rml+="""<td><para style="answer">""" + str(tot_per)+"%(" + str(tot_res) + """)</para></td>"""
                            percantage = 0.00
                            if res_count:
                                percantage = round((float(rating_weight_sum)/res_count),2)
                            rml+="""<td><para style="answer">""" + str(percantage) + """</para></td>"""
                            rml+="""<td><para style="answer">""" + str(res_count) + """</para></td></tr>"""
                        rml+="""</blockTable>"""
                    elif que.type in['matrix_of_drop_down_menus']:
                        for column in que.column_heading_ids:
                            rml+="""<blockTable colWidths="500" style="Table1"><tr>
                                <td><para style="answer">""" + to_xml(column.title) + """</para></td></tr></blockTable>"""
                            menu_choices = column.menu_choice.split('\n')
                            cols_widhts = []   
                            cols_widhts.append(200)
                            for col in range(0,len(menu_choices)+1):
                                cols_widhts.append(float(300/(len(menu_choices)+1)))
                            colWidths = ",".join(map(str, cols_widhts))
                            rml +="""<blockTable colWidths=" """ + colWidths + """ " style="Table1"><tr>
                                <td><para style="response"></para></td>"""
                            for menu in menu_choices:
                                rml+="""<td><para style="response">""" + to_xml(menu) + """</para></td>"""
                            rml += """<td><para style="response">Response Count</para></td></tr>"""
                            cr.execute("select count(id), sra.answer_id from survey_response_answer sra \
                                     where sra.answer='%s' group by sra.answer_id " %(column.title))
                            res_count = cr.dictfetchall()
                            cr.execute("select count(sra.id),sra.value_choice, sra.answer_id, sra.answer from survey_response_answer sra \
                                 where sra.answer='%s'  group by sra.value_choice ,sra.answer_id, sra.answer"%(column.title))
                            calc_percantage = cr.dictfetchall()
                            for ans in que.answer_choice_ids:
                                rml+="""<tr><td><para style="answer_right">""" + to_xml(ans.answer) + """</para></td>"""
                                for mat_col in range(0, len(menu_choices)):
                                    calc = 0
                                    response = 0
                                    for res in res_count:
                                        if res['answer_id'] == ans.id: response = res['count']
                                    for per in calc_percantage:
                                        if ans.id == per['answer_id'] and menu_choices[mat_col] == per['value_choice']:
                                            calc = per['count']
                                    percantage = 0.00
                                    if calc and response:
                                        percantage = (float(calc)* 100) / response
                                    rml+="""<td><para style="answer">""" +str(percantage)+"% (" +  str(calc) + """)</para></td>"""
                                response = 0
                                for res in res_count:
                                    if res['answer_id'] == ans.id: response = res['count']
                                rml += """<td><para style="response">""" + str(response) + """</para></td></tr>"""
                            rml += """</blockTable>"""
                    elif que.type in['numerical_textboxes']:
                        rml +="""<blockTable colWidths="240.0,20,100.0,70,70.0" style="Table1">"""
                        rml += """ <tr> 
                             <td> <para style="Standard"> </para></td> 
                             <td> <para style="Standard"> </para></td>
                             <td> <para style="response">Response Average</para></td>
                             <td> <para style="response">Response Total</para></td>
                             <td> <para style="response">Response Count</para></td>                 
                         </tr>"""
                        for ans in que.answer_choice_ids:
                            cr.execute("select answer from survey_response_answer where answer_id=%d group by answer" % ans.id)
                            tot_res = cr.dictfetchall()
                            total = 0
                            for  tot in tot_res:
                                total += int(tot['answer'])
                            length = len(tot_res)
                            rml+="""<tr><td><para style="answer">""" + to_xml(ans.answer) + """</para></td>
                                    <td> <para style="Standard"> </para></td>
                                    <td> <para style="answer">""" + str(float(total) / len(tot_res)) +"""</para></td>
                                    <td><para style="answer">""" + str(total) + """</para></td>
                                    <td><para style="answer">""" + str(len(tot_res)) + """</para></td></tr>"""
                        rml+="""</blockTable>"""


                    rml +="""<blockTable colWidths="300,100,100.0" style="Table3">
                        <tr>
                              <td><para style="Standard1"></para></td>
                              <td><para style="Standard1">Answered Question</para></td>
                              <td><para style="Standard1">""" + str(que.tot_resp) + """</para></td>
                        </tr>
                        <tr>
                            <td><para style="Standard1"></para></td>
                            <td><para style="Standard1">Skipped Question</para></td>
                            <td><para style="Standard1">""" + str(survey.tot_start_survey - que.tot_resp) + """</para></td>
                        </tr>
                        </blockTable>"""
        rml+="""</story></document>"""
        report_type = datas.get('report_type', 'pdf')
        create_doc = self.generators[report_type]
        pdf = create_doc(rml, title=self.title)
        return (pdf, report_type)
survey_analysis('report.survey.analysis', 'survey','','')