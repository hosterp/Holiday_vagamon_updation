from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime,timedelta
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class AttendanceReport(ReportXlsx):
    
    def generate_xlsx_report(self, workbook, data, lines):
        # We can recieve the data entered in the wizard here as data
        worksheet = workbook.add_worksheet("attendance_report.xlsx")
        
        boldc = workbook.add_format({'bold': True, 'align': 'center'})
        heading_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 10})
        bold = workbook.add_format({'bold': True})
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        regular = workbook.add_format({'align':'center','bold':False})
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
        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",inv
        worksheet.set_column('B:B', 20)
        worksheet.set_row('2', boldc)
        
        worksheet.merge_range('A1:Q1', "Attendance Report", boldc)
        
        month = datetime.strptime(inv[0].from_date,"%Y-%m-%d").month
        if month == 1:
            month = "January" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month== 2:
            month = "Febuary"+ str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 3:
            month = "March"+ str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 4:
            month="April"+ str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 5:
            month = "May"+ str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 6:
            month = "June" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month ==7:
            month = "July"  + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 8:
            month = "August" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 9:
            month = "Septemper" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 10:
            month = "October" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        elif month == 11:
            month = "November" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        else:
            month = "December" + str(datetime.strptime(inv[0].from_date,"%Y-%m-%d").year)
        worksheet.merge_range('A2:Q2',month , boldc)
        worksheet.write('A3','SL NO:',regular)
        worksheet.write('B3','Employee Name',regular)
        worksheet.write('C3','Employee Code',regular)
        day_first = datetime.strptime(inv[0].from_date,"%Y-%m-%d").day
        day_last = datetime.strptime(inv[0].to_date,"%Y-%m-%d").day
        col = 68
        new_col = 65
        next_col = 65
        for i in range(day_last):
            if day_first <24:
                worksheet.write('%s3' %(chr(col)),day_first,regular)
                day_first = day_first + 1
                col +=1
            else:
                worksheet.write('%s%s3' % (chr(new_col),chr(next_col)), day_first, regular)
                day_first = day_first + 1
                next_col +=1
        worksheet.write('%s%s3' % (chr(new_col),chr(next_col)), "Day Present", regular)
        next_col +=1
        worksheet.write('%s%s3' % (chr(new_col), chr(next_col)), "Day Absent", regular)
        
        row_no = 4
        sl_no = 1
        
        active_ids = inv[0].get_selected_users(inv[0].active_ids)
        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", inv[0].active_ids
        for emp in active_ids:
            total_att = 0
            worksheet.write('A%s' %(row_no), sl_no, regular)
            sl_no +=1
            worksheet.write('B%s' % (row_no), emp.name, regular)
            worksheet.write('C%s' % (row_no), emp.emp_code, regular)
            day_first = datetime.strptime(inv[0].from_date, "%Y-%m-%d")
            day_first_day = datetime.strptime(inv[0].from_date, "%Y-%m-%d").day
            day_last = datetime.strptime(inv[0].to_date, "%Y-%m-%d")
            day_last_day = datetime.strptime(inv[0].to_date, "%Y-%m-%d").day
            no_of_days= day_last - day_first
            col = 68
            new_col = 65
            next_col = 65
            for i in range(day_last_day):
                if day_first_day < 24:
                    attendance = self.env['hiworth.hr.attendance'].search([('name','=',emp.id),('date','=',day_first)])
                    att = 0
                    if attendance.attendance == 'full':
                        att = 1
                    if attendance.attendance == 'half':
                        att = .5
                    worksheet.write('%s%s' % (chr(col),row_no),att , regular)
                    total_att +=att
                    day_first = day_first + timedelta(days=1)
                    day_first_day = day_first_day + 1
                    col += 1
                else:
                    attendance = self.env['hiworth.hr.attendance'].search(
                        [('name', '=', emp.id), ('date', '=', day_first)])

                    att = 0
                    if attendance.attendance == 'full':
                        att = 1
                    if attendance.attendance == 'half':
                        att = .5
                    worksheet.write('%s%s%s' % (chr(new_col), chr(next_col),row_no), att, regular)
                    total_att += att
                    day_first = day_first + timedelta(days=1)
                    day_first_day = day_first_day + 1
                    next_col += 1
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col),row_no), total_att, regular)
            next_col += 1
            
            worksheet.write('%s%s%s' % (chr(new_col), chr(next_col),row_no), (no_of_days.days) - total_att , regular)
            row_no+=1
        
            
            
AttendanceReport('report.hiworth_attendance.report_attendance_report.xlsx', 'hiworth.hr.leave')