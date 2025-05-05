import io
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from ..models import Session,Teacher
import pandas as pd

class ExportService:
    @staticmethod
    def export_to_excel(sessions,teachers,file_path):
        teacher_names = list(teachers.values_list('name', flat=True))
        data = []

        for session in sessions:
            row = {
                'Day': session.day,
                'Time Slot': session.time_slot,
            }
            for name in teacher_names:
                row[name] = ""

            for teacher in session.responsibles.all():
                if teacher in session.supervisors.all():
                      row[teacher.name] = "R/S"
                else:
                      row[teacher.name] = "R"
            
            for teacher in session.supervisors.all():
                if teacher not in session.responsibles.all():
                      row[teacher.name] = "S"
            
            data.append(row)

            

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')    
    @staticmethod
    def export_to_pdf():
        
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        for teacher in Teacher.objects.all():
            # Start new page for each teacher
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(1*inch, 10.5*inch, f"Timetable for {teacher.name}")
            
            #workload information
            pdf.setFont("Helvetica", 10)
            pdf.drawString(1*inch, 10.2*inch, f"Original Workload: {teacher.original_workload_hours} hours")
            pdf.drawString(1*inch, 10.0*inch, f"Assigned Hours: {teacher.assigned_hours} hours")
            pdf.drawString(1*inch, 9.8*inch, f"New Workload: {teacher.workload_hours} hours")



            # Create table headers
            pdf.setFont("Helvetica-Bold", 10)
            headers = ["Day", "Time",  "Role"]
            for i, header in enumerate(headers):
                pdf.drawString(1*inch + i*2*inch, 9.5*inch, header)
            
            # Add sessions
            pdf.setFont("Helvetica", 10)
            y_position = 9.2*inch
            #get sessions
            sorted_sessions = teacher.sort_assigned_sessions()
            
            for session in sorted_sessions:
                if teacher in session.responsibles.all() and teacher in session.supervisors.all():
                    role = "R/S"  
                elif teacher in session.responsibles.all() :
                    role="R"
                elif teacher in session.supervisors.all() :
                    role="S"
                else:
                    continue
                    
                row = [
                    session.day,
                    session.time_slot,
                    
                    role
                ]
                
                for i, item in enumerate(row):
                    pdf.drawString(1*inch + i*2*inch, y_position, str(item))
                
                y_position -= 0.3*inch
                if y_position < 0.5*inch:  # New page if running out of space
                    pdf.showPage()
                    y_position = 10*inch
            
            pdf.showPage()  # New teacher on new page

        pdf.save()
        buffer.seek(0)
        return buffer
        
         


















'''@staticmethod
    def export_calendar_to_excel():
        """Export full supervision calendar to Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Supervision Calendar"

        # Create headers
        headers = ["Day", "Time Slot", "Session"] + \
                 [f"Teacher {i+1}" for i in range(10)]  # Adjust based on max teachers per session
        ws.append(headers)

        # Populate data
        for session in Session.objects.order_by('day', 'time_slot'):
            teachers = []
            for teacher in session.responsibles.all():
                if teacher in session.supervisors.all():
                    teachers.append(f"{teacher.name} (R/S)")
                else:
                    teachers.append(f"{teacher.name} (R)")
            
            for teacher in session.supervisors.all():
                if teacher not in session.responsibles.all():
                    teachers.append(f"{teacher.name} (S)")

            row = [
                session.day,
                session.time_slot,
            ] + teachers
            ws.append(row)

        # Create response
        output = io.BytesIO()
        wb.save(output)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename=supervision_calendar.xlsx'
        return response

   @staticmethod
    def export_teacher_timetables_to_pdf():
        """Export individual teacher timetables to PDF"""
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        for teacher in Teacher.objects.all():
            # Start new page for each teacher
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(1*inch, 10.5*inch, f"Timetable for {teacher.name}")
            
            # Create table headers
            pdf.setFont("Helvetica-Bold", 10)
            headers = ["Day", "Time", "Session", "Role"]
            for i, header in enumerate(headers):
                pdf.drawString(1*inch + i*2*inch, 10*inch, header)
            
            # Add sessions
            pdf.setFont("Helvetica", 10)
            y_position = 9.5*inch
            sessions = teacher.assigned_sessions.order_by('day', 'time_slot')
            
            for session in sessions:
                role = "R/S" if session in teacher.responsibles.all() else "S"
                row = [
                    session.day,
                    session.time_slot,
                    session.name,
                    role
                ]
                
                for i, item in enumerate(row):
                    pdf.drawString(1*inch + i*2*inch, y_position, str(item))
                
                y_position -= 0.3*inch
                if y_position < 0.5*inch:  # New page if running out of space
                    pdf.showPage()
                    y_position = 10*inch
            
            pdf.showPage()  # New teacher on new page

        pdf.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=teacher_timetables.pdf'
        return response'''