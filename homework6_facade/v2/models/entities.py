from typing import List, Optional
from datetime import datetime
from .enums import Symptom, PotentialDisease

class Prescription:
    def __init__(self, name: str, potential_disease: PotentialDisease, medicines: List[str], usage: str):
        self.name = name
        self.potential_disease = potential_disease
        self.medicines = medicines
        self.usage = usage

class PatientCase:
    def __init__(self, case_time: datetime, symptoms: List[Symptom], prescription: Optional[Prescription] = None):
        self.case_time = case_time
        self.symptoms = symptoms
        self.prescription = prescription

class PatientData:
    def __init__(self, id: str, name: str, gender: str, age: int, height: float, weight: float):
        self.id = id
        self.name = name
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.cases: List[PatientCase] = []

    def add_case(self, case: PatientCase):
        self.cases.append(case)
