from django.db import models,transaction
from datetime import datetime

# Create your models here.



class Teacher(models.Model):
    name=models.CharField(max_length=100)
    workload_hours=models.FloatField()
    original_workload_hours=models.FloatField()
    assigned_hours=models.FloatField(default=0)

    assigned_sessions = models.ManyToManyField(
        'Session',
        related_name='assigned_teachers',
        blank=True
    )

    def get_remaining_capacity(self):
        remaining=self.workload_hours-self.assigned_hours
        return max(remaining,0)
    
    def has_constraint(self,day,time_slot):
        return self.constraints.filter(day=day,time_slot=time_slot).exists()
    
    def has_assignement(self,day,time_slot):
        return self.assigned_sessions.filter(day=day,time_slot=time_slot).exists()
    
    def assign_session(self,session,commit=True):
        new_assigned=self.assigned_hours +session.session_duration
        if self.is_available(session.day,session.time_slot,session.session_duration) and new_assigned <= self.workload_hours :
            self.assigned_hours=self.assigned_hours +session.session_duration
            if commit:
                with transaction.atomic():
                    
                    self.save()
                    self.assigned_sessions.add(session)
                    session.supervisors.add(self)
            return True
        return False
    
    def is_available(self,day,time_slot,duration):
        return(
            not self.has_constraint(day,time_slot) and
            not self.has_assignement(day,time_slot) and
            self.workload_hours-self.assigned_hours>= duration
        )
    def sort_assigned_sessions(self):
        return sorted(
            self.assigned_sessions.all(),
            key=lambda s:s.extract_date()
        )
    
    def __str__(self):
        return f"{self.name} ({self.assigned_hours}/{self.workload_hours}h)"
    
class Session(models.Model):
    day=models.CharField(max_length=30)
    time_slot=models.CharField(max_length=20)
    total_number_needed=models.IntegerField()
    number_sup_wanted=models.IntegerField()
    session_duration=models.FloatField()

    responsibles=models.ManyToManyField(Teacher,related_name="responsibles_per_session",blank=True)
    supervisors=models.ManyToManyField(Teacher,related_name="supervisers_per_session",blank=True)

    def __str__(self):
        return f"On {self.day} {self.time_slot} we need ({self.total_number_needed} session )"
    def extract_date(self):
        #from Mardi[14-01-2025] =>datetime(2025,1,14)
        date_str=self.day.split("[")[1].rstrip("]")
        return datetime.strptime(date_str,"%d-%m-%Y")
    @classmethod
    def sort_sessions_by_date(cls):
        #return sessions sorted by date
        return sorted(
            cls.objects.all(),
            key=lambda session: session.extract_date()
        )
    
    

class Constraint(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,related_name='constraints')
    day=models.CharField(max_length=20)
    time_slot=models.CharField(max_length=20)

    class Meta:
        unique_together=('teacher','day','time_slot')



#class Supervision(models.Model):
