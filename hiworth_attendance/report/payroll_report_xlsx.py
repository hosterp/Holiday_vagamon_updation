from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import logging
from datetime import datetime,timedelta
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
from cStringIO import StringIO

from openerp.report.report_sxw import report_sxw
from openerp.api import Environment

class PayRollReport(ReportXlsx):
    
    def generate_xlsx_report(self,workbook, data,lines):
        #We can recieve the data entered in the wizard here as data
        worksheet= workbook.add_worksheet("payroll_report.xlsx")
        
        boldc = workbook.add_format({'bold': True, 'align': 'center'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        centerb = workbook.add_format({'align': 'center', 'bold': True})
        center = workbook.add_format({'align': 'center'})
        right = workbook.add_format({'align': 'right'})
        bolde = workbook.add_format({'bold': True, 'font_color': 'brown'})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        })

        row = 7
        col = 0
        new_row = row
        inv = lines
        worksheet.set_column('B:B', 20)
        worksheet.set_row('2', boldc)

        worksheet.merge_range('A1:AD1', "PROVIDENT FUND & ESI CALCULATION CHART & PAY ROLL FOR THE MONTH", boldc)

        worksheet.write('A2', 'Company Name.:', boldc)
        worksheet.write('B2', inv.company_person_id.name or '', boldc)
        worksheet.write('C2', 'Date From:', boldc)
        worksheet.merge_range('D2:K2', inv.start_date or '', boldc)
        worksheet.write('L2', 'Date To:', boldc)
        worksheet.write('M2', inv.end_date or '', boldc)
       
        worksheet.merge_range('A3:Q3', 'Deduction Summary', boldc)

        worksheet.merge_range('A4:A7', 'Sl No.', boldc)
        worksheet.merge_range('B4:B7', 'Employee Name', boldc)
        worksheet.merge_range('C4:C7', 'Designation of Employee', boldc)
        worksheet.merge_range('D4:D7', 'Staff donation', boldc)
        worksheet.merge_range('E4:E7', 'PF Amt', boldc)
        worksheet.merge_range('F4:F7', 'ESI Amt', boldc)
        worksheet.merge_range('G4:G7', 'Mobile Over', boldc)
        worksheet.merge_range('H4:H7', 'Society Kit', boldc)
        worksheet.merge_range('I4:I7', 'Canteen Food', boldc)

        worksheet.merge_range('J4:J7', 'LIC Amt', boldc)
        worksheet.merge_range('K4:K7', 'MediClaim Amt', boldc)
        worksheet.merge_range('L4:L7', 'Loan Refund', boldc)

        worksheet.merge_range('M4:M7', 'Fine', boldc)
        worksheet.merge_range('N4:N7', 'Chitty', boldc)
        worksheet.merge_range('O4:O7', 'Total Deduction', boldc)

        worksheet.merge_range('P3:AG3', 'PROVIDENT FUND & ESI CALCULATION CHART & PAY ROLL FOR THE MONTH', boldc)
        worksheet.merge_range('Q4:Q7', 'Days In Month', boldc)
        worksheet.merge_range('R4:R7', 'Attendance', boldc)
        worksheet.merge_range('S4:S7', 'Wages Due', boldc)
        worksheet.merge_range('T4:T7', 'PF Wages', boldc)
        worksheet.merge_range('U4:U7', 'EDLI @  0.50%', boldc)
        worksheet.merge_range('V4:V7', 'EPF @ 12%', boldc)
        worksheet.merge_range('W4:W7', 'EPF @ 3.67 %', boldc)
        worksheet.merge_range('X4:X7', 'EPS @ 8.33% %', boldc)
        worksheet.merge_range('Y4:Y7', 'ESI @ 0.75%', boldc)
        worksheet.merge_range('Z4:Z7', 'ESI @ 3.25%', boldc)
        worksheet.merge_range('AA4:AA7', 'TOTAL ESI @ 4%', boldc)
        worksheet.merge_range('AB4:AB7', 'ADVANCE', boldc)
        worksheet.merge_range('AC4:AC7', 'OTHERS', boldc)
        worksheet.merge_range('AD4:AD7', 'TOTAL DEDUCTIONS', boldc)
        worksheet.merge_range('AE4:AE7', 'NET SALARY DUE', boldc)

        from_date = datetime.strptime(inv.start_date, "%Y-%m-%d")
        to_date = datetime.strptime(inv.end_date, "%Y-%m-%d")

        
        employee_payslips = self.env['hr.payslip'].search([('date_from','=',from_date),('date_to','=',to_date)])

        sl_no = 1
        total_epf1 = 0
        total_epf2 = 0
        total_esi1 = 0
        total_esi3 = 0
        total_esi4 = 0
        total_salary = 0
        for payslip in employee_payslips:
            new_row += 1
            sl_no += 1
            worksheet.write('A%s' % (new_row), sl_no)
            worksheet.write('B%s' % (new_row), payslip.employee_id.name)
            worksheet.write('C%s' % (new_row), payslip.employee_id.user_category, center)
            worksheet.write('D%s' % (new_row), payslip.staff_donation, center)
            pf_amt = 0
            if payslip.wages_due<15000:
                
                pf_amt = round((payslip.wages_due * .12))
            else:
                if payslip.employee_id.pf_required == True:
                    pf_amt = 1800
                else:
                    pf_amt = 0
            worksheet.write('E%s' % (new_row), pf_amt, center)
            esi_amt = 0
            if payslip.contract_id.wage <21000:
                esi_amt = round(payslip.wages_due * .0075)
            worksheet.write('F%s' % (new_row), esi_amt, center)
            worksheet.write('G%s' % (new_row), payslip.mobile_over, center)
            worksheet.write('H%s' % (new_row), payslip.society_kit, center)
            worksheet.write('I%s' % (new_row), payslip.canteen_food, center)
            worksheet.write('J%s' % (new_row), payslip.lic_amount, center)
            worksheet.write('K%s' % (new_row), payslip.mediclaim_amount, center)
            worksheet.write('L%s' % (new_row), payslip.loan_refund, center)
            worksheet.write('M%s' % (new_row), payslip.fine, center)
            worksheet.write('N%s' % (new_row), payslip.chitty, center)
            total = payslip.staff_donation + pf_amt + esi_amt + payslip.mobile_over + payslip.society_kit + payslip.canteen_food+ \
                    payslip.lic_amount + payslip.mediclaim_amount + payslip.loan_refund + payslip.fine + payslip.chitty
            
            worksheet.write('O%s' % (new_row), total or '', center)
            no_of_days = to_date - from_date
            worksheet.write('Q%s' % (new_row), no_of_days.days or '', center)

            worksheet.write('R%s' % (new_row), payslip.attendance or '', center)

            worksheet.write('S%s' % (new_row), payslip.wages_due or '', center)
            pf_wages = 0
            if payslip.employee_id.pf_required:
                if pf_amt == 0:
                    pf_wages = payslip.wages_due
                else:
                    pf_wages = payslip.contract_id.wage
                
            worksheet.write('T%s' % (new_row),  pf_wages or '', center)
            
            worksheet.write('U%s' % (new_row), payslip.employee_id.pf_required and round(payslip.wages_due * .0050) or 0, center)
            
            total_esi3 += payslip.employee_id.pf_required and round(payslip.wages_due * .0050) or 0
            
            worksheet.write('V%s' % (new_row), payslip.employee_id.pf_required and round(payslip.wages_due * .12) or 0, center)
            total_epf1 += payslip.employee_id.pf_required and round(payslip.wages_due * .12) or 0
            worksheet.write('W%s' % (new_row), payslip.employee_id.pf_required and round(payslip.wages_due * .0367) or 0, center)
            worksheet.write('X%s' % (new_row), payslip.employee_id.pf_required and round(payslip.wages_due * .0833) or 0, center)
            total_epf2 +=  payslip.employee_id.pf_required and round(payslip.wages_due * .0367) or 0
            esi1 = esi_amt != 0 and round(payslip.wages_due * .0075) or 0
            esi2 = esi_amt != 0 and round(payslip.wages_due * .0325) or 0
            total_esi1 += esi_amt != 0 and round(payslip.wages_due * .0833) or 0
            worksheet.write('Y%s' % (new_row), esi_amt != 0 and round(payslip.wages_due * .0075) or 0, center)
            worksheet.write('Z%s' % (new_row), esi_amt != 0 and round(payslip.wages_due * .0325) or 0, center)
            total_esi4 += (esi1 +  esi2 )
            worksheet.write('AA%s' % (new_row), (esi1 +  esi2 )or '', center)
            
            worksheet.write('AB%s' % (new_row), payslip.wages_due or '', center)
            advance = payslip.amount_advance
            worksheet.write('AC%s' % (new_row), payslip.amount_advance or '', center)
            total_dedu = total + advance
            worksheet.write('AD%s' % (new_row), total_dedu or '', center)
            worksheet.write('AE%s' % (new_row), payslip.wages_due - total_dedu or '', center)
            total_salary += payslip.wages_due - total_dedu
            
            
            new_row+=1
       
        worksheet.write('AE%s' % (new_row), total_salary or '', center)
        
        
        worksheet.write('T%s' % (new_row), "Employee's Contribution to EPF " or '', center)
        worksheet.write('U%s' % (new_row), total_epf1 or '', center)
        new_row +=1
        worksheet.write('T%s' % (new_row), "Employer's Contribution to EPF " or '', center)
        worksheet.write('U%s' % (new_row), total_epf2 or '', center)
        new_row += 1
        worksheet.write('T%s' % (new_row), "Employer's Contribution to EPS " or '', center)
        worksheet.write('U%s' % (new_row), total_esi1 or '', center)
        new_row += 1
        worksheet.write('T%s' % (new_row), "Employer's Contribution to EDLI " or '', center)
        worksheet.write('U%s' % (new_row), total_esi3 or '', center)
        new_row += 1
        worksheet.write('T%s' % (new_row), "Administrative Charges  " or '', center)
        worksheet.write('U%s' % (new_row), total_esi3 or '', center)
        new_row += 1

        worksheet.write('T%s' % (new_row), "Total Amount Payable  PF" or '', center)
        worksheet.write('U%s' % (new_row), total_epf1 + total_epf2+total_esi3 + total_esi1+ total_esi3 or '', center)
        
        new_row += 1

        worksheet.write('T%s' % (new_row), "ESI  " or '', center)
        worksheet.write('U%s' % (new_row), total_esi4 or '', center)

        new_row += 1

       
            
            
            
          
        #
        # extra_row = new_row
        # if inv.extra_line_ids:
        #     extra_row += 1
        #     worksheet.write('B%s' % (extra_row), 'Extra Items', bolde)
        #
        #     for line in inv.extra_line_ids:
        #         extra_row += 1
        #
        #         qty = "'{%." + str(line.uom_id.decimal_no) + "f}'"
        #         a = qty % line.already_executed_qty
        #         a = a.split('{')[1]
        #         already_executed_qty = a.split("}")[0]
        #
        #         b = qty % line.to_be_executed_qty
        #         b = b.split('{')[1]
        #         to_be_executed_qty = b.split("}")[0]
        #
        #         c = qty % line.total_quantity
        #         c = c.split('{')[1]
        #         total_quantity = c.split("}")[0]
        #
        #         worksheet.write('A%s' % (extra_row), line.sl_no)
        #         worksheet.write('B%s' % (extra_row), line.product_id.name)
        #         worksheet.write('C%s' % (extra_row), line.quantity, center)
        #         worksheet.write('D%s' % (extra_row), line.estimated_rate, center)
        #         worksheet.write('E%s' % (extra_row), line.untaxed_amt, center)
        #         worksheet.write('F%s' % (extra_row), line.already_executed_qty, center)
        #         worksheet.write('G%s' % (extra_row), line.to_be_executed_qty, center)
        #         worksheet.write('H%s' % (extra_row), line.total_quantity, center)
        #         worksheet.write('I%s' % (extra_row), line.revised_rate, center)
        #         worksheet.write('J%s' % (extra_row), "%.2f" % line.already_executed_revised, center)
        #         worksheet.write('K%s' % (extra_row), "%.2f" % line.to_be_executed_revised, center)
        #         worksheet.write('L%s' % (extra_row), "%.2f" % line.revised_total, center)
        #         worksheet.write('M%s' % (extra_row), line.savings, center)
        #         worksheet.write('N%s' % (extra_row), line.excess, center)
        #         worksheet.write('O%s' % (extra_row), line.explanation or '', center)
        #         worksheet.write('P%s' % (extra_row), line.remarks_ksrrda or '', center)
        #         worksheet.write('Q%s' % (extra_row), line.remarks_se or '', center)
                
                
PayRollReport('report.hiworth_attendance.report_payroll_report.xlsx', 'payroll.report')