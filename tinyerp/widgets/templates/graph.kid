<table width="100%" xmlns:py="http://purl.org/kid/ns#">
    <tr>
        <td align="center">
            <div id="${chart_name}" style="width: 500; height: 400"></div>
            <script py:if="chart_type=='bar'" type="text/javascript">
                new BarChart('${chart_name}', "${tg.url('/graph/bar', _terp_model=model, _terp_view_id=view_id, _terp_ids=ustr(ids), _terp_domain=ustr(domain), _terp_context=ustr(context))}");
            </script>
            <script py:if="chart_type=='pie'" type="text/javascript">
                new PieChart('${chart_name}', "${tg.url('/graph/pie', _terp_model=model, _terp_view_id=view_id, _terp_ids=ustr(ids), _terp_domain=ustr(domain), _terp_context=ustr(context))}");
            </script>
        </td>
    </tr>
</table>