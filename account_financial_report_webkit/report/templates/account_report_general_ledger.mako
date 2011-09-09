<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.context_lang)%>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Chart of Account')}</div>
                <div class="act_as_cell">${_('Fiscal Year')}</div>
                <div class="act_as_cell">
                    %if filter_form(data) == 'filter_date':
                        ${_('Dates')}
                    %else:
                        ${_('Periods')}
                    %endif
                </div>
                <div class="act_as_cell">${_('Displayed Accounts')}</div>
                <div class="act_as_cell">${_('Target Moves')}</div>

            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ chart_account.name }</div>
                <div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell">
                    ${_('From:')}
                    %if filter_form(data) == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form(data) == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <div class="act_as_cell">
                    %if accounts(data):
                        ${', '.join([account.code for account in accounts(data)])}
                    %else:
                        ${_('All')}
                    %endif

                </div>
                <div class="act_as_cell">${ display_target_move(data) }</div>
            </div>
        </div>

        <!-- we use div with css instead of table for tabular data because div do not cut rows at half at page breaks -->
        %for account in objects:
          %if display_account_raw(data) == 'all' or (account.ledger_lines or account.init_balance.get('init_balance')):
              <%
              cumul_balance =  0.0
              cumul_balance_curr = 0.0
              %>
            <div class="act_as_table list_table" style="margin-top: 10px;">

                <div class="act_as_caption account_title">
                    ${account.code} - ${account.name}
                </div>
                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        ## date
                        <div class="act_as_cell first_column" style="width: 45px;">${_('Date')}</div>
                        ## period
                        <div class="act_as_cell" style="width: 45px;">${_('Period')}</div>
                        ## move
                        <div class="act_as_cell" style="width: 100px;">${_('Entry')}</div>
                        ## journal
                        <div class="act_as_cell" style="width: 50px;">${_('Journal')}</div>
                        ## partner
                        <div class="act_as_cell" style="width: 120px;">${_('Partner')}</div>
                        ## ref
                        <div class="act_as_cell" style="width: 100px;">${_('Ref')}</div>
                        ## label
                        <div class="act_as_cell" style="width: 170px;">${_('Label')}</div>
                        ## counterpart
                        <div class="act_as_cell" style="width: 100px;">${_('Counter part')}</div>
                        ## reconcile
                        <div class="act_as_cell" style="width: 20px;" >${_('Rec.')}</div>
                        ## balance
                        <div class="act_as_cell amount" style="width: 75px;">${_('Balance')}</div>
                        ## balance cumulated
                        <div class="act_as_cell amount" style="width: 75px;">${_('Cumul. Bal.')}</div>
                        %if amount_currency(data):
                            ## curency code
                            <div class="act_as_cell" style="width: 20px; text-align: center;">${_('Curr.')}</div>
                            ## currency balance
                            <div class="act_as_cell amount" style="width: 75px;">${_('Curr. Balance')}</div>
                            ## currency balance cumulated
                            <div class="act_as_cell amount" style="width: 75px;">${_('Curr. Cumul. Bal')}</div>
                        %endif
                    </div>
                </div>

                <div class="act_as_tbody">
                      <%
                      cumul_balance = account.init_balance.get('init_balance') or 0.0
                      cumul_balance_curr = account.init_balance.get('init_balance_currency') or 0.0
                      %>
                      %if initial_balance(data) and cumul_balance:
                        <div class="act_as_row initial_balance">
                          ## date
                          <div class="act_as_cell first_column"></div>
                          ## period
                          <div class="act_as_cell"></div>
                          ## move
                          <div class="act_as_cell"></div>
                          ## journal
                          <div class="act_as_cell"></div>
                          ## partner
                          <div class="act_as_cell"></div>
                          ## ref
                          <div class="act_as_cell"></div>
                          ## label
                          <div class="act_as_cell">${_('Balance brought forward')}</div>
                          ## counterpart
                          <div class="act_as_cell"></div>
                          ## reconcile
                          <div class="act_as_cell"></div>
                          ## balance
                          <div class="act_as_cell amount">${formatLang(cumul_balance) | amount }</div>
                          ## balance cumulated
                          <div class="act_as_cell amount">${formatLang(cumul_balance) | amount }</div>
                         %if amount_currency(data):
                              ## curency code
                              <div class="act_as_cell amount"></div>
                              ## currency balance
                              <div class="act_as_cell amount">${formatLang(cumul_balance_curr) | amount }</div>
                              %if account.currency_id:
                                  ## currency balance cumulated
                                  <div class="act_as_cell amount">${formatLang(cumul_balance_curr) | amount }</div>
                              %else:
                                <div class="act_as_cell amount">${formatLang(0.0) | amount }</div>
                              %endif
                         %endif

                        </div>
                      %endif
                      %for line in account.ledger_lines:
                      <div class="act_as_row lines">
                          ## date
                          <div class="act_as_cell first_column">${formatLang(line.get('ldate') or '', date=True)}</div>
                          ## period
                          <div class="act_as_cell">${line.get('period_code') or ''}</div>
                          ## move
                          <div class="act_as_cell">${line.get('move_name') or ''}</div>
                          ## journal
                          <div class="act_as_cell">${line.get('jcode') or ''}</div>
                          ## partner
                          <div class="act_as_cell">${line.get('partner_name') or ''}</div>
                          ## ref
                          <div class="act_as_cell">${line.get('lref') or ''}</div>
                          ## label
                          <div class="act_as_cell">${line.get('lname') or ''}</div>
                          ## counterpart
                          <div class="act_as_cell">${line.get('counterparts') or ''}</div>
                          ## reconcile
                          <div class="act_as_cell">${line.get('rec_name') or ''}</div>
                          ## balance
                          <div class="act_as_cell amount">${ formatLang(line.get('balance') or 0.0) | amount }</div>
                          ## balance cumulated
                          <% cumul_balance += line.get('balance') or 0.0 %>
                          <div class="act_as_cell amount">${ formatLang(cumul_balance) | amount }</div>
                          %if amount_currency(data):
                              ## curency code
                              <div class="act_as_cell" style="text-align: center;">${line.get('currency_code') or ''}</div>
                              ## currency balance
                              <div class="act_as_cell amount">${formatLang(line.get('amount_currency') or 0.0)  | amount }</div>
                              %if account.currency_id:
                              <% cumul_balance_curr += line.get('amount_currency') or 0.0 %>
                                  ## currency balance cumulated
                                  <div class="act_as_cell amount">${formatLang(cumul_balance_curr) | amount }</div>
                              %else:
                                  <div class="act_as_cell amount">${formatLang(0.0) | amount }</div>
                              %endif
                          %endif
                      </div>
                      %endfor
                </div>
            </div>
          %endif
        %endfor
    </body>
</html>
