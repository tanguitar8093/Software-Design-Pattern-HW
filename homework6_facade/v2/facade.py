from typing import List
from models.database import PatientDatabase
from models.prescriber import Prescriber
from models.enums import Symptom
from models.observers import CaseRecordObserver, JsonExportObserver, CsvExportObserver

class PrescriptionSystemFacade:
    def __init__(self, patients_json: str, diseases_txt: str):
        self.db = PatientDatabase()
        self.db.import_data(patients_json)
        
        self.prescriber = Prescriber(self.db)
        self.prescriber.import_supported_diseases(diseases_txt)
        
        # Default attach case record observer
        self.prescriber.attach_observer(CaseRecordObserver(self.db))

    def set_export_format(self, format_type: str, file_path: str):
        if format_type.upper() == "JSON":
            self.prescriber.attach_observer(JsonExportObserver(file_path))
        elif format_type.upper() == "CSV":
            self.prescriber.attach_observer(CsvExportObserver(file_path))

    def diagnose(self, patient_id: str, symptoms: List[Symptom]):
        self.prescriber.prescribe(patient_id, symptoms)

    def wait_for_completion(self):
        self.prescriber.demand_queue.join()
