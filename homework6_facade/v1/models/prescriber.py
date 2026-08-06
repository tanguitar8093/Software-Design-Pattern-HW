import time
import threading
import queue
from typing import List, Callable, Optional
from models.entities import PatientData, Prescription
from models.rules import DiagnosisHandler

class PrescriptionDemand:
    def __init__(self, patient: PatientData, symptoms: List[str]):
        self.patient = patient
        self.symptoms = symptoms

class Prescriber:
    def __init__(self):
        self.rule_chain_head: Optional[DiagnosisHandler] = None
        self.demands_queue: queue.Queue = queue.Queue()
        self.observers: List[Callable[[PatientData, List[str], Prescription], None]] = []
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def set_rule_chain(self, handler: DiagnosisHandler):
        self.rule_chain_head = handler

    def add_observer(self, callback: Callable[[PatientData, List[str], Prescription], None]):
        self.observers.append(callback)

    def prescribe(self, patient: PatientData, symptoms: List[str]):
        demand = PrescriptionDemand(patient, symptoms)
        self.demands_queue.put(demand)

    def _worker_loop(self):
        while self._running:
            try:
                demand = self.demands_queue.get(timeout=1.0)
                
                # 模擬耗時 3 秒
                time.sleep(3)
                
                prescription = None
                if self.rule_chain_head:
                    prescription = self.rule_chain_head.handle(demand.patient, demand.symptoms)

                if prescription:
                    self._notify_observers(demand.patient, demand.symptoms, prescription)
                else:
                    print(f"[{demand.patient.name}] 找不到對應的診斷處方。")
                
                self.demands_queue.task_done()
            except queue.Empty:
                continue

    def _notify_observers(self, patient: PatientData, symptoms: List[str], prescription: Prescription):
        for observer in self.observers:
            observer(patient, symptoms, prescription)

    def stop(self):
        self._running = False
        self._worker_thread.join()
