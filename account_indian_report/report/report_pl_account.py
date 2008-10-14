import time
import pooler
import mx.DateTime
from report import report_sxw
from account import *

class report_pl_account(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_pl_account, self).__init__(cr, uid, name, context)
        self.debitbalance=0.0
        self.creditbalance=0.0
        self.result=[]
        self.count=0
        self.np=0.0
        self.localcontext.update({
            'time': time,
            'get_tplines': self._get_tplines,
            'get_lines': self._get_lines,
            'get_total': self._get_total, 
        })     
    def _get_tplines(self,form,ids={},level=1):
        if not ids:
            ids = self.ids
        if not ids:
            return []
        res={}
        self.result=[]
        dict=[]
        res1={}
        accounts = self.pool.get('account.account').browse(self.cr, self.uid, ids)
        for account in accounts:
                if account.code=='AC0':
                    continue
                res['id']=account.id
                res['code']=account.code
                res['name']=account.name
                res['debit']=account.debit
                res['credit']=account.credit
                res['progress']=account.balance
                res['level']=level
                self.result.append(res)
                res={}
                if account.child_id:
                        self.result[-1]['status']=1               
                        for x in account.child_id:
                            self.result +=self._get_tplines(form,[x.id],level+1)
                else:
                    self.result[-1]['status']=0
                dict+=self._get_lines(form,account)
        return self.result
    def _get_lines(self,form,obj):
        res={}
        account = self.pool.get('account.account').browse(self.cr, self.uid,obj['id'])
        query = self.pool.get('account.move.line')._query_get(self.cr, self.uid,context={'fiscalyear': form['fiscalyear'],'periods':form['periods'][0][2]})            
        self.cr.execute("SELECT l.date, j.name as jname,l.name as lname, l.debit, l.credit "\
                    "FROM account_move_line l, account_journal j "\
                    "WHERE l.journal_id = j.id "\
                        "AND account_id = %d AND "+query+" "\
                    "ORDER by l.id", (account.id,))
        res=self.cr.dictfetchall()
        sum = 0.0    
        for l in res:
            sum += l['debit'] - l ['credit']
            l['progress'] = sum 
            self.debitbalance+=l['debit']   
            self.creditbalance+=l['credit']
        if not res and form['empty_account']==0:
             for el in self.result:
               if el['code'] == obj['code']:
                   if el['status']==0:
                       self.result.remove(el)
                   else:
                       if el['progress']==0.00 and el['code'] <> '0':
                           self.result.remove(el)
        return res or ''        
    def _get_total(self):
        res={
             'debittot':0.0,
             'credittot':0.0,
             'netamt':0.0,
             'result':''
             }
        res['debittot']=self.debitbalance/2
        res['credittot']=self.creditbalance/2
        res['netamt']=(self.debitbalance-self.creditbalance)/2
        self.np=res['netamt']
        if res['netamt']<0:
            res['result']="Net Profit:"
        else:
            res['result']="Net Loss:"
        return res or '' 
report_sxw.report_sxw(
    'report.report.pl.account',
    'account.account',
    'addons/account_indian_report/report/report_pl_account.rml',
    parser=report_pl_account, header=False)
