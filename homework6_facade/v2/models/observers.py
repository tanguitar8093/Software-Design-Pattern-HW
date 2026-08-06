from abc import ABC, abstractmethod
from typing import List
import json
import csv
from .entities import Prescription
from .enums import Symptom
from .database import PatientDatabase
from .entities import PatientCase
from datetime import datetime

class IPrescriberObserver(ABC):
    @abstractmethod
    def update(self, patient_id: str, symptoms: List[Symptom], prescription: Prescription):
        pass

class CaseRecordObserver(IPrescriberObserver):
    def __init__(self, db: PatientDatabase):
        self.db = db

    def update(self, patient_id: str, symptoms: List[Symptom], prescription: Prescription):
        case = PatientCase(case_time=datetime.now(), symptoms=symptoms, prescription=prescription)
        self.db.add_patient_case(patient_id, case)

class JsonExportObserver(IPrescriberObserver):
    def __init__(self, target_path: str):
        self.target_path = target_path

    def update(self, patient_id: str, symptoms: List[Symptom], prescription: Prescription):
        data = {
            "patient_id": patient_id,
            "symptoms": [s.value for s in symptoms],
            "prescription": {
                "name": prescription.name,
                "potential_disease": prescription.potential_disease.value,
                "medicines": prescription.medicines,
                "usage": prescription.usage
            }
        }
        with open(self.target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class CsvExportObserver(IPrescriberObserver):
    def __init__(self, target_path: str):
        self.target_path = target_path

    def update(self, patient_id: str, symptoms: List[Symptom], prescription: Prescription):
        with open(self.target_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["patient_id", "symptoms", "prescription_name", "disease", "medicines", "usage"])
            writer.writerow([
                patient_id,
                ",".join([s.value for s in symptoms]),
                prescription.name,
                prescription.potential_disease.value,
                ",".join(prescription.medicines),
                prescription.usage
            ])
