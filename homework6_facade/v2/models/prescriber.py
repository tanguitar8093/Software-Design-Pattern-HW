import time
from typing import List
import queue
import threading
from .enums import PotentialDisease, Symptom
from .database import PatientDatabase
from .rules import Covid19Rule, AttractiveRule, SleepApneaRule
from .entities import Prescription
from .observers import IPrescriberObserver

class Prescriber:
    def __init__(self, db: PatientDatabase):
        self.db = db
        self.supported_diseases: List[PotentialDisease] = []
        self.observers: List[IPrescriberObserver] = []
        
        # Build rule chain
        self.rule_chain = Covid19Rule()
        self.rule_chain.set_next(AttractiveRule()).set_next(SleepApneaRule())
        
        # Queue for prescription demands
        self.demand_queue = queue.Queue()
        self.is_diagnosing = False
        self.lock = threading.Lock()

    def import_supported_diseases(self, txt_path: str):
        self.supported_diseases = []
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name:
                    try:
                        self.supported_diseases.append(PotentialDisease(name))
                    except ValueError:
                        pass # Ignore unknown diseases

    def attach_observer(self, observer: IPrescriberObserver):
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_observers(self, patient_id: str, symptoms: List[Symptom], prescription: Prescription):
        for obs in self.observers:
            obs.update(patient_id, symptoms, prescription)

    def _process_queue(self):
        while not self.demand_queue.empty():
            patient_id, symptoms = self.demand_queue.get()
            
            # Simulate 3 seconds diagnostics
            time.sleep(3)
            
            patient = self.db.get_patient(patient_id)
            if patient:
                prescription = self.rule_chain.handle(patient, symptoms)
                if prescription and prescription.potential_disease in self.supported_diseases:
                    self.notify_observers(patient_id, symptoms, prescription)
            
            self.demand_queue.task_done()
            
        with self.lock:
            self.is_diagnosing = False

    def prescribe(self, patient_id: str, symptoms: List[Symptom]):
        self.demand_queue.put((patient_id, symptoms))
        with self.lock:
            if not self.is_diagnosing:
                self.is_diagnosing = True
                # Run the diagnostic process in a separate thread to allow concurrent prescribe requests
                threading.Thread(target=self._process_queue, daemon=True).start()
