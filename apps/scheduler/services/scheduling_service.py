from django.db import models,transaction
from ..models import Teacher,Session
from collections import defaultdict
from datetime import timedelta

class AssignementEngine:

    @classmethod
    @transaction.atomic
    def assign_teachers_to_sessions(cls):
        
        #clear previous assignements
        cls._clear_assignements()

        sessions=Session.objects.prefetch_related('responsibles')
        if not sessions.first():
                raise ValueError("No sessions exist in the database")
        session_duration=sessions.first().session_duration
        #check if it's possible with teachers' total wokload and adjust if not
        cls.verify_total_workload(session_duration)

        #assign all responsibles
        cls._assign_all_responsibles(sessions)

         #organize sessions by days and time
        sorted_sessions=cls._organize_sessions(sessions)

        #algo 
        cls.assign_teachers_globally(sorted_sessions)
        

    @classmethod
    def _safe_assign_teacher(cls,teacher,session):
        try:
            teacher.refresh_from_db()
            return teacher.assign_session(session)
        except Exception as e:
            print(f"error assigning teacher {teacher.id} to session {session.id}: {str(e)}")
            return False
    @classmethod
    def verify_total_workload(cls,session_duration):
        total_hours_needed=sum(
            s.session_duration *s.total_number_needed
            for s in Session.objects.all()
        )
        total_capacity=sum(
            t.original_workload_hours
            for t in Teacher.objects.all()
        )

        if total_capacity>=total_hours_needed:
            return True
        deficit=total_hours_needed-total_capacity
        num_teachers=Teacher.objects.count()

        #round to session duration

        base=deficit/num_teachers
        additional_hours=session_duration-(base%session_duration)
        if additional_hours==session_duration:
            additional_hours=0

        hours_per_teacher=base+additional_hours
        #apply
        Teacher.objects.update(
            workload_hours=models.F('original_workload_hours')+hours_per_teacher
            )
        return False
    @classmethod
    def _assign_all_responsibles(cls,sessions):
        for session in sessions:
            for teacher in session.responsibles.all():
                cls._safe_assign_teacher(teacher,session)
    
    @classmethod
    def _organize_sessions(cls,sessions):
        #sort sessions by day & time
        return sorted(
            sessions,
            key=lambda s: (s.extract_date(),s.time_slot)
        )
       
         
    

    @classmethod
    def _clear_assignements(cls):
        with transaction.atomic(): 
            for s in Session.objects.all():
                s.supervisors.clear()
            for t in Teacher.objects.all():
                t.assigned_sessions.clear()
        Teacher.objects.update(assigned_hours=0,workload_hours=models.F('original_workload_hours'))
        
    @classmethod
    def assign_teachers_globally(cls,sorted_sessions):
        for i,current_session in enumerate(sorted_sessions):
            if current_session.supervisors.count() >= current_session.number_sup_wanted:
                continue 
            #find available teachers same day & next day
            same_day_sessions=[
                s for s in sorted_sessions[i+1:]
                if s.day==current_session.day
            ]
            next_day=current_session.extract_date()+timedelta(days=1)
            next_day_sessions=[
                s for s in sorted_sessions[i+1:]
                if s.extract_date()==next_day
            ]

            if current_session.supervisors.count() <= current_session.number_sup_wanted:
                #cls._assign_from_future_sessions(current_session,next_day_sessions)
                cls._assign_consecutive_sessions(current_session,same_day_sessions)
            if current_session.supervisors.count() <= current_session.number_sup_wanted:

                #cls._assign_from_future_sessions(current_session,next_day_sessions)
                cls._assign_consecutive_sessions(current_session,next_day_sessions)

            if current_session.supervisors.count()<=current_session.number_sup_wanted:
                cls._assign_available_teachers(current_session)







    @classmethod
    def _process_day(cls,day,day_sessions):
        #assign teachers to supervise sessions in a day
        for i,current_session in enumerate(day_sessions):
            
            #skip next step if minimun is met
            if current_session.supervisors.count() >= current_session.number_sup_wanted:
                continue 

            #assign responsibles for following sessions
            if current_session.supervisors.count()<=current_session.number_sup_wanted:
                cls._assign_from_future_sessions(current_session,day_sessions[i+1:])
                #cls._assign_consecutive_sessions(current_session,day_sessions[i+1:])
                

            #assign any available teacher if needed
            if current_session.supervisors.count()<=current_session.number_sup_wanted:
                cls._assign_available_teachers(current_session)

    @classmethod
    def _assign_consecutive_sessions(cls,current_session,future_sessions,max_break_min=45):
        #timeline=sorted(sessions,key=lambda s: s.time_slot)

        for teacher in current_session.supervisors.all():
            for future_session in future_sessions:
                if teacher in future_session.responsibles.all():
                    time_slot = current_session.time_slot.strip("[]'\"")
                    _,current_end=time_slot.split('-')

                    next_slot=future_session.time_slot.strip("[]'\"")
                    next_start,_=next_slot.split('-')

                    #calculate break time
                    break_mins=cls._time_diff_minutes(current_end,next_start)
                    if(0<=break_mins<=max_break_min and teacher.is_available(future_session.day,future_session.time_slot,future_session.session_duration)):
                       
                       cls._safe_assign_teacher(future_session)
                    
                    break

    @classmethod
    def _time_diff_minutes(cls,end_time,start_time):
        def clean_time(time_str):
            return ''.join(c for c in time_str if c.isdigit() or c == ':')
    
        def parse_time(time_str):
            clean = clean_time(time_str)
            hh, mm = map(int, clean.split(':'))
            return hh * 60 + mm
    
        return parse_time(start_time) - parse_time(end_time)
        
    @classmethod
    def _assign_from_future_sessions(cls,current_session,future_sessions):
        needed=current_session.number_sup_wanted-current_session.supervisors.count()

        for future_session in future_sessions:
            for teacher in future_session.responsibles.all():
                if(current_session.supervisors.count()<current_session.number_sup_wanted and teacher.is_available(
                    current_session.day,current_session.time_slot,current_session.session_duration
                )):
                    cls._safe_assign_teacher(teacher,current_session)
                    needed-=1
                    if needed<=0:
                        return
    
    @classmethod
    def _assign_available_teachers(cls,session):
        #assigning random teachers(teachers who didn't reach their workload capacity)
        needed=session.number_sup_wanted-session.supervisors.count()
        same_day_teachers = Teacher.objects.filter( assigned_sessions__day=session.day,id=models.OuterRef('pk'))
       
        available_today=Teacher.objects.annotate(
            remaining_capacity=models.F('workload_hours')-models.F('assigned_hours')
            
        ).filter(
            models.Exists(same_day_teachers),
            remaining_capacity__gte=session.session_duration
            
        ).exclude(
            id__in=session.supervisors.values_list('id',flat=True)
        ).order_by('-remaining_capacity')

        available=Teacher.objects.annotate(
            remaining_capacity=models.F('workload_hours')-models.F('assigned_hours')      
        ).filter(
            remaining_capacity__gte=session.session_duration
            
        ).exclude(
            id__in=session.supervisors.values_list('id',flat=True)
        ).order_by('-remaining_capacity')


        for teacher in available_today:
            if needed<=0:
                break

            if teacher.is_available(session.day,session.time_slot,session.session_duration):
                if cls._safe_assign_teacher(teacher,session):
                    needed-=1
        
        if needed>0:
            for teacher in available:
                if needed<=0:
                    break

                if teacher.is_available(session.day,session.time_slot,session.session_duration):
                    if cls._safe_assign_teacher(teacher,session):
                        needed-=1


        
                     

            
