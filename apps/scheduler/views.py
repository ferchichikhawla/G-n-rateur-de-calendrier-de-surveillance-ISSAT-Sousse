from django.shortcuts import render
from .services.excel_service import ExcelImportService
from django.http import FileResponse,JsonResponse
from .models import Session,Teacher
from .services.export_services import ExportService
from django.http import HttpResponse
from io import BytesIO
from django.http import JsonResponse
from .models import Teacher

# Create your views here.
'''def import_teachers_view(request):
    if request.method=='POST':
        try:
            teachers=ExcelImportService.import_teachers(request.FILES['file'])
            print("well done")
        except ValidationError as e:
            print("error")'''

def test_import(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            teachers = ExcelImportService.import_teachers(request.FILES['file'])
            return JsonResponse({
                'status': 'success',
                'count': len(teachers),
                'teachers': [t.name for t in teachers]
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'test_upload.html')

from django.views.generic import TemplateView

class AdminDashboardView(TemplateView):
    template_name = 'admin.html'

def test_session_import(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # Get optional teacher columns
            teacher_cols_input = request.POST.get('teacher_cols', '')
            teacher_cols = [c.strip() for c in teacher_cols_input.split(',') if c.strip()] or None
            
            print(f"Received file: {request.FILES['file'].name}")
            print(f"Teacher columns: {teacher_cols}")
            
            sessions = ExcelImportService.import_sessions(
                request.FILES['file'],
                teacher_columns=teacher_cols
            )
            print(f"Imported {len(sessions)} sessions successfully.")
            
            return JsonResponse({
                'success': True,
                'status': f"Successfully imported {len(sessions)} sessions",
                'created': len(sessions),
            })
        except Exception as e:
            print("Session import failed:", str(e))
            return JsonResponse({
                'success': False,
                'status': "Import failed",
                'errors': [str(e)]
            }, status=400)
    else:
        return JsonResponse({'success': False, 'status': 'Invalid request'}, status=400)

def test_export(request):
    sessions=Session.objects.all()
    teachers=Teacher.objects.all()
    file_path='CalendarS.xlsx'
    output = BytesIO()
    
    ExportService.export_to_excel(sessions,teachers,file_path)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="CalendarS.xlsx"'
    return response

def test_export_pdf(request):
    buffer=ExportService.export_to_pdf()

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=teacher_timetables.pdf'
    return response

def generate_and_export_excel(request):
    if request.method == 'POST':
        try:
            from .services.scheduling_service import AssignementEngine
            from .services.export_services import ExportService
            from io import BytesIO
            from django.http import HttpResponse
            # Run the scheduling algorithm
            AssignementEngine.assign_teachers_to_sessions()
            # Get all sessions and teachers
            sessions = Session.objects.all()
            teachers = Teacher.objects.all()
            # Generate Excel file with results
            output = BytesIO()
            ExportService.export_to_excel(sessions, teachers, output)
            output.seek(0)
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="assignments.xlsx"'
            return response
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def teachers_list_api(request):
    teachers = Teacher.objects.all()
    data = [{'id': t.id, 'name': t.name} for t in teachers]
    return JsonResponse(data, safe=False)

def export_teacher_schedule(request, teacher_id):
    from django.http import HttpResponse, JsonResponse
    from io import BytesIO
    try:
        from .services.scheduling_service import AssignementEngine
        AssignementEngine.assign_teachers_to_sessions()
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Teacher not found'}, status=404)

    buffer = BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch

    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(1*inch, 10.5*inch, f"Timetable for {teacher.name}")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(1*inch, 10.2*inch, f"Original Workload: {teacher.original_workload_hours} hours")
    pdf.drawString(1*inch, 10.0*inch, f"Assigned Hours: {teacher.assigned_hours} hours")
    pdf.drawString(1*inch, 9.8*inch, f"New Workload: {teacher.workload_hours} hours")

    pdf.setFont("Helvetica-Bold", 10)
    headers = ["Day", "Time", "Role"]
    for i, header in enumerate(headers):
        pdf.drawString(1*inch + i*2*inch, 9.5*inch, header)

    pdf.setFont("Helvetica", 10)
    y_position = 9.2*inch
    sorted_sessions = teacher.sort_assigned_sessions()

    for session in sorted_sessions:
        if teacher in session.responsibles.all() and teacher in session.supervisors.all():
            role = "R/S"
        elif teacher in session.responsibles.all():
            role = "R"
        elif teacher in session.supervisors.all():
            role = "S"
        else:
            continue

        row = [session.day, session.time_slot, role]
        for i, item in enumerate(row):
            pdf.drawString(1*inch + i*2*inch, y_position, str(item))

        y_position -= 0.3*inch
        if y_position < 0.5*inch:
            pdf.showPage()
            y_position = 10*inch

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={teacher.name}_schedule.pdf'
    return response

    from django.http import HttpResponse, JsonResponse
    from io import BytesIO
    try:
        from .services.scheduling_service import AssignementEngine
        # Run the scheduling algorithm to update assignments
        AssignementEngine.assign_teachers_to_sessions()
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Teacher not found'}, status=404)
    # Generate PDF or Excel for this teacher's schedule
    buffer = BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch

    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(1*inch, 10.5*inch, f"Timetable for {teacher.name}")

    # Workload information
    pdf.setFont("Helvetica", 10)
    pdf.drawString(1*inch, 10.2*inch, f"Original Workload: {teacher.original_workload_hours} hours")
    pdf.drawString(1*inch, 10.0*inch, f"Assigned Hours: {teacher.assigned_hours} hours")
    pdf.drawString(1*inch, 9.8*inch, f"New Workload: {teacher.workload_hours} hours")

    # Create table headers
    pdf.setFont("Helvetica-Bold", 10)
    headers = ["Day", "Time", "Role"]
    for i, header in enumerate(headers):
        pdf.drawString(1*inch + i*2*inch, 9.5*inch, header)

    # Add sessions
    pdf.setFont("Helvetica", 10)
    y_position = 9.2*inch
    sorted_sessions = teacher.sort_assigned_sessions()

    for session in sorted_sessions:
        if teacher in session.responsibles.all() and teacher in session.supervisors.all():
            role = "R/S"
        elif teacher in session.responsibles.all():
            role = "R"
        elif teacher in session.supervisors.all():
            role = "S"
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

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

from django.views.generic import TemplateView

class TeacherListView(TemplateView):
    template_name = 'teacher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For demonstration, we create a list of teacher files with dummy URLs
        # In real use, you might list actual files or teacher data
        context['teacher_files'] = [
            {'name': 'professeurs.xlsx', 'view_url': '#'},
            # Add more files or data as needed
        ]
        return context

def test_export_teacher_pdfs(request):
    buffer = ExportService.export_teacher_timetables_to_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=teacher_individual_timetables.pdf'
    return response
