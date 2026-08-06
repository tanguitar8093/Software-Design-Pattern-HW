import json
from typing import Dict
from .entities import PatientData, PatientCase

class PatientDatabase:
    def __init__(self):
        self.patients: Dict[str, PatientData] = {}

    def import_data(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                patient = PatientData(
                    id=p['id'],
                    name=p['name'],
                    gender=p['gender'],
                    age=p['age'],
                    height=p['height'],
                    weight=p['weight']
                )
                self.patients[patient.id] = patient

    def get_patient(self, id: str) -> PatientData:
        return self.patients.get(id) # 這個 .get(id), 是會依據 id 拿到整個 PatientData, 還是只有 id

    def add_patient_case(self, id: str, patient_case: PatientCase): # 這是私有方法, 應該用私有方式方式寫 code
        patient = self.get_patient(id)
        if patient:
            patient.add_case(patient_case)
