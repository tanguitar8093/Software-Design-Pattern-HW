from abc import ABC, abstractmethod
from typing import List, Optional
from models.entities import PatientData, Prescription

class DiagnosisHandler(ABC):
    def __init__(self):
        self._next_handler: Optional['DiagnosisHandler'] = None

    def set_next(self, handler: 'DiagnosisHandler') -> 'DiagnosisHandler':
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, patient: PatientData, symptoms: List[str]) -> Optional[Prescription]:
        if self._next_handler:
            return self._next_handler.handle(patient, symptoms)
        return None

class Covid19Handler(DiagnosisHandler):
    def handle(self, patient: PatientData, symptoms: List[str]) -> Optional[Prescription]:
        covid_symptoms = {"打噴嚏", "Headache", "Cough"}
        if covid_symptoms.issubset(set(symptoms)):
            return Prescription(
                name="清冠一號",
                potential_disease="COVID-19",
                medicines=["清冠一號"],
                usage="將相關藥材裝入茶包裡，使用500 mL 溫、熱水沖泡悶煮1~3 分鐘後即可飲用。"
            )
        return super().handle(patient, symptoms)

class AttractiveHandler(DiagnosisHandler):
    def handle(self, patient: PatientData, symptoms: List[str]) -> Optional[Prescription]:
        if patient.age == 18 and patient.gender == "female" and "sneeze" in symptoms:
            return Prescription(
                name="青春抑制劑",
                potential_disease="Attractive",
                medicines=["假鬢角", "臭味"],
                usage="把假鬢角黏在臉的兩側，讓自己異性緣差一點，自然就不會有人想妳了。"
            )
        return super().handle(patient, symptoms)

class SleepApneaHandler(DiagnosisHandler):
    def handle(self, patient: PatientData, symptoms: List[str]) -> Optional[Prescription]:
        bmi = patient.weight / ((patient.height / 100) ** 2)
        if bmi > 26 and "snore" in symptoms:
            return Prescription(
                name="打呼抑制劑",
                potential_disease="SleepApneaSyndrome",
                medicines=["一捲膠帶"],
                usage="睡覺時，撕下兩塊膠帶，將兩塊膠帶交錯黏在關閉的嘴巴上，就不會打呼了。"
            )
        return super().handle(patient, symptoms)
