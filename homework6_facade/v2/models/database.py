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
        return self.patients.get(id)

    def add_patient_case(self, id: str, patient_case: PatientCase):
        patient = self.get_patient(id)
        if patient:
            patient.add_case(patient_case)
