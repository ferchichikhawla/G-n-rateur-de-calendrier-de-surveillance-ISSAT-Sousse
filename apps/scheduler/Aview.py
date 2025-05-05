from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .services.scheduling_service import AssignementEngine
from .models import Teacher,Session

class AssignementView(View):
    def get(self,request):
        return render(request,'assignements.html')
    def post(self,request):
        try:
            AssignementEngine.assign_teachers_to_sessions()
            #collect results
            results={
                'sessions':[],
                'teachers':[],
                'verification':{
                    'sessions':[],
                    'teachers':[],
                    'all_valid': True 
                }
            }
            #session assignements
            for session in Session.objects.order_by('day','time_slot'):
                assigned_teachers=list(session.supervisors.values_list('name',flat=True))
                results['sessions'].append({
                    'day': session.day,
                    'time': str(session.time_slot),
                    'duration': session.session_duration,
                    'needed': session.total_number_needed,
                    'min_needed': session.total_number_needed,
                    'max_wanted': session.number_sup_wanted,
                    
                    'assigned_count': len(assigned_teachers),
                    'assigned_teachers': assigned_teachers
                })
                #teachers
            for teacher in Teacher.objects.all():
                assigned_sessions=teacher.assigned_sessions.all()
                total_hours=sum(s.session_duration for s in assigned_sessions)
                sessions_info=[{
                        'day': s.day,
                        'time': str(s.time_slot),
                        'duration': s.session_duration
                        
                 }  for s in assigned_sessions.order_by('day', 'time_slot')]

                results['teachers'].append({
                        'name': teacher.name,
                        'capacity': teacher.workload_hours,
                        'assigned_hours': total_hours,
                        'sessions': sessions_info
                    })
                    #verification
            for session in Session.objects.all():
                assigned_count=session.supervisors.count()
                valid=session.total_number_needed<=assigned_count<=session.number_sup_wanted
                if not valid:
                            results['verification']['all_valid']=False
                results['verification']['sessions'].append({
                            'assigned': assigned_count,
                            'min_needed': session.total_number_needed,
                            'max_wanted': session.number_sup_wanted,
                            'valid': valid })
                    
            for teacher in Teacher.objects.all():
                assigned_hours = sum(s.session_duration for s in teacher.assigned_sessions.all())
                valid = assigned_hours <= teacher.workload_hours
                if not valid:
                        results['verification']['all_valid'] = False
                
                results['verification']['teachers'].append({
                            'name': teacher.name,
                            'capacity': teacher.workload_hours,
                            'assigned': assigned_hours,
                            'valid': valid
                         })
            return JsonResponse({
                        'status':'success',
                        'results':results
                    })
        except Exception as e:
            return JsonResponse({
                'status':'error',
                'message':str(e)
            },status=500)

                        
                        

