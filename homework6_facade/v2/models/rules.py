from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import PatientData, Prescription
from .enums import Symptom, PotentialDisease

class PrescribeRule(ABC):
    def __init__(self):
        self.next_rule: Optional['PrescribeRule'] = None

    def set_next(self, rule: 'PrescribeRule') -> 'PrescribeRule':
        self.next_rule = rule
        return rule

    def handle(self, patient: PatientData, symptoms: List[Symptom]) -> Optional[Prescription]:
        result = self.diagnose(patient, symptoms)
        if result:
            return result
        if self.next_rule:
            return self.next_rule.handle(patient, symptoms)
        return None

    @abstractmethod
    def diagnose(self, patient: PatientData, symptoms: List[Symptom]) -> Optional[Prescription]:
        pass

class Covid19Rule(PrescribeRule):
    def diagnose(self, patient: PatientData, symptoms: List[Symptom]) -> Optional[Prescription]:
        # 打噴嚏、頭痛和咳嗽
        if Symptom.SNEEZE in symptoms and Symptom.HEADACHE in symptoms and Symptom.COUGH in symptoms:
            return Prescription(
                name="清冠一號",
                potential_disease=PotentialDisease.COVID_19,
                medicines=["清冠一號"],
                usage="將相關藥材裝入茶包裡，使用500 mL 溫、熱水沖泡悶煮1~3 分鐘後即可飲用。"
            )
        return None

class AttractiveRule(PrescribeRule):
    def diagnose(self, patient: PatientData, symptoms: List[Symptom]) -> Optional[Prescription]:
        if patient.age == 18 and patient.gender == "female" and Symptom.SNEEZE in symptoms:
            return Prescription(
                name="青春抑制劑",
                potential_disease=PotentialDisease.ATTRACTIVE,
                medicines=["假鬢角", "臭味"],
                usage="把假鬢角黏在臉的兩側，讓自己異性緣差一點，自然就不會有人想妳了。"
            )
        return None

class SleepApneaRule(PrescribeRule):
    def diagnose(self, patient: PatientData, symptoms: List[Symptom]) -> Optional[Prescription]:
        bmi = patient.weight / ((patient.height / 100) ** 2)
        if bmi > 26 and Symptom.SNORE in symptoms:
            return Prescription(
                name="打呼抑制劑",
                potential_disease=PotentialDisease.SLEEP_APNEA_SYNDROME,
                medicines=["一捲膠帶"],
                usage="睡覺時，撕下兩塊膠帶，將兩塊膠帶交錯黏在關閉的嘴巴上，就不會打呼了。"
            )
        return None
