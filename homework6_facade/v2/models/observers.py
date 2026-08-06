from abc import ABC, abstractmethod
import json
import csv
import os
from datetime import datetime, timezone
from .entities import Prescription
from .enums import Symptom
from .database import PatientDatabase
from .entities import PatientCase

class IPrescriberObserver(ABC):
    @abstractmethod
    def update(self, patient_id: str, symptoms: list[Symptom], prescription: Prescription):
        pass

class CaseRecordObserver(IPrescriberObserver):
    def __init__(self, db: PatientDatabase):
        self.db = db

    def update(self, patient_id: str, symptoms: list[Symptom], prescription: Prescription):
        case = PatientCase(case_time=datetime.now(tz=timezone.utc), symptoms=symptoms, prescription=prescription)
        self.db.add_patient_case(patient_id, case)

class JsonExportObserver(IPrescriberObserver):
    def __init__(self, target_path: str):
        self.target_path = target_path

    def update(self, patient_id: str, symptoms: list[Symptom], prescription: Prescription):
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
        existing_data = []
        if os.path.exists(self.target_path):
            with open(self.target_path, 'r', encoding='utf-8') as f:
                try:
                    content = json.load(f)
                    if isinstance(content, list):
                        existing_data = content
                    else:
                        existing_data = [content]
                except (json.JSONDecodeError, ValueError):
                    pass
                    
        existing_data.append(data)
        
        with open(self.target_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

class CsvExportObserver(IPrescriberObserver):
    def __init__(self, target_path: str):
        self.target_path = target_path

    def update(self, patient_id: str, symptoms: list[Symptom], prescription: Prescription):
        file_exists = os.path.isfile(self.target_path)
        with open(self.target_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["patient_id", "symptoms", "prescription_name", "disease", "medicines", "usage"])
            writer.writerow([
                patient_id,
                ",".join([s.value for s in symptoms]),
                prescription.name,
                prescription.potential_disease.value,
                ",".join(prescription.medicines),
                prescription.usage
            ])
