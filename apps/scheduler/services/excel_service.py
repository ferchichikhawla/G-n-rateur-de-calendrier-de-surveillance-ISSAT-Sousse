import pandas as pd 
from django.db import transaction
from io import BytesIO
import numpy as np
from django.core.exceptions import ValidationError
from apps.scheduler.models import Teacher,Session
from datetime import datetime

class ExcelImportService:
    #this service handles import operations from excel
    @staticmethod
    def _clean_data(df):
        #removes empty rows
        df=df.dropna(how='all')

        if not df.empty and df.iloc[-1].isna().all():
            df=df.iloc[:-1]
        

        return df
    
    
    @staticmethod
    @transaction.atomic
    def import_teachers(file):
        #file: InMemoryUploadedFile from Django form =>returns List of all teachers
        try:
            df = pd.read_excel(BytesIO(file.read()), na_values=['', None, 'NA', 'N/A', 'NaN'])
            #df=pd.read_excel(BytesIO(file.read()))
            df=ExcelImportService._clean_data(df)

            required_columns={'Nom Et Prénom Enseignant','Nombre de Séances de surveillance'}
            if not required_columns.issubset(df.columns):
                raise ValidationError("Excel missing required columns")
            
            #delete all existing teachers
            deleted_count,_ =Teacher.objects.all().delete()

            '''teachers=[]
            for _, row in df.iterrows():
                if pd.isna(row['Nom Et Prénom Enseignant']) or row['Nom Et Prénom Enseignant'] == '':
                    continue

                teacher,created=Teacher.objects.update_or_create(
                    name=row['Nom Et Prénom Enseignant'],
                    defaults={'workload_hours':float(row['Nombre de Séances de surveillance']),
                              'original_workload_hours':float(row['Nombre de Séances de surveillance'])
                              }
                )
                teachers.append(teacher)'''
            
            #create in bulk
            teachers=[
                Teacher(
                    name=row['Nom Et Prénom Enseignant'],
                    workload_hours=float(row['Nombre de Séances de surveillance']),
                    original_workload_hours=float(row['Nombre de Séances de surveillance'])
                )
                for _, row in df.iterrows()
                if pd.notna(row['Nom Et Prénom Enseignant'])
                    
            ]

            created_teachers=Teacher.objects.bulk_create(teachers)

            
            return created_teachers
        except Exception as e:
            raise ValidationError(f"Excel import failed: {str(e)}")
    @staticmethod
    @transaction.atomic
    def import_sessions(file,teacher_columns=None):
        #loads sessions from excel sheet
        #assigns teachers their R sessions
        #time_slot validation + day continuation
        try:
            df=pd.read_excel(BytesIO(file.read()))
            df=ExcelImportService._clean_session_data(df)

            #delete existing sessions
            deleted_count,_=Session.objects.all().delete()

            if teacher_columns is None:
                teacher_columns=ExcelImportService._detect_teacher_columns(df)

            #get teachers
            teachers={t.name: t for t in Teacher.objects.all()}

            sessions=[]
            current_day=None
            for _,row in df.iterrows():
                if not ExcelImportService._valid_session_row(row):
                    continue

                #update day if needed else use current
                if pd.notna(row['Day']):
                    current_day=str(row['Day']).strip()

                session= Session.objects.create(
                    day=current_day,
                    time_slot=str(row['time_slot']).split(),
                    total_number_needed=int(float(row['Total number'])) if pd.notna(row['Total number']) else 0,
                    number_sup_wanted=int(float(row['Besoin sup'])) if pd.notna(row['Besoin sup']) else 0,
                    session_duration=ExcelImportService._calculate_duration(row['time_slot'])
                )

                #assign responsibles
                for col in teacher_columns:
                    if str(row[col]).strip().upper()=='R':
                        if teacher :=teachers.get(col):
                            session.responsibles.add(teacher)
                sessions.append(session)
                
            return sessions
        except Exception as e:
            raise ValidationError(f"Session import error: {str(e)}")
    @staticmethod
    def _clean_session_data(df):
        df['Day']=df['Day'].ffill()
        df=df.dropna(subset=['time_slot'], how='all') #drop invalid rows

        str_cols= df.select_dtypes(include=['object']).columns
        df[str_cols]=df[str_cols].apply(lambda x: x.str.strip())

        return df
    
    @staticmethod
    def _valid_session_row(row):
        #validate req session fields
        return(
            pd.notna(row.get('time_slot')) and
            pd.notna(row.get('Day')) and
            str(row.get('time_slot')).strip() !=''
        
        )
    @staticmethod
    def _calculate_duration(time_slot):
        #convert time slot to duration hours (string->period)
        try:
            start,end =map(str.split, time_slot.split('-'))
            fmt= "%H:%M"
            delta=datetime.strptime(end,fmt)-datetime.strptime(start,fmt)

            return delta.total_seconds()/3600
        
        except:
            return 1.5
    
    @staticmethod
    def _detect_teacher_columns(df):
        teacher_cols=[
            col for col in df.columns
            if any(str(row[col]).strip().upper()=='R' for _, row in df.iterrows())
        ]
        if not teacher_cols:
            teacher_cols=[
                col for col in df.columns
                if any(t.name in col for t in Teacher.objects.all())
            ]

        return teacher_cols or []

        
    





        

        
