import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class Prescription:
    def __init__(self, name: str, potential_disease: str, medicines: List[str], usage: str):
        self.name = name
        self.potential_disease = potential_disease
        self.medicines = medicines
        self.usage = usage

    def to_dict(self):
        return {
            "name": self.name,
            "potential_disease": self.potential_disease,
            "medicines": self.medicines,
            "usage": self.usage
        }

class PatientCase:
    def __init__(self, prescription: Prescription, symptoms: List[str]):
        self.prescription = prescription
        self.symptoms = symptoms
        self.case_time = datetime.now()

    def to_dict(self):
        return {
            "prescription": self.prescription.to_dict(),
            "symptoms": self.symptoms,
            "case_time": self.case_time.isoformat()
        }

class PatientData:
    def __init__(self, id: str, name: str, gender: str, age: int, height: float, weight: float):
        self.id = id
        self.name = name
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.patient_cases: List[PatientCase] = []

    def add_case(self, case: PatientCase):
        self.patient_cases.append(case)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "cases": [case.to_dict() for case in self.patient_cases]
        }

class PatientDatabase:
    def __init__(self):
        self.patients: Dict[str, PatientData] = {}

    def load_from_json(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for p_data in data:
                    patient = PatientData(
                        id=p_data['id'],
                        name=p_data['name'],
                        gender=p_data['gender'],
                        age=p_data['age'],
                        height=p_data['height'],
                        weight=p_data['weight']
                    )
                    self.patients[patient.id] = patient
        except FileNotFoundError:
            print(f"Error: Database file {file_path} not found.")

    def get_patient(self, patient_id: str) -> Optional[PatientData]:
        return self.patients.get(patient_id)
