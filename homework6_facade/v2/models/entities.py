from datetime import datetime

from .enums import PotentialDisease, Symptom


class Prescription:
    def __init__(self, name: str, potential_disease: PotentialDisease, medicines: list[str], usage: str):
        self.name = name
        self.potential_disease = potential_disease
        self.medicines = medicines
        self.usage = usage

class PatientCase:
    def __init__(self, case_time: datetime, symptoms: list[Symptom], prescription: Prescription | None):
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
        self.cases: list[PatientCase] = []

    def add_case(self, case: PatientCase):
        self.cases.append(case)
