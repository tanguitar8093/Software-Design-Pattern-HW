import json
import csv
import os
from typing import List
from models.entities import PatientDatabase, PatientData, PatientCase, Prescription
from models.prescriber import Prescriber
from models.rules import DiagnosisHandler, Covid19Handler, AttractiveHandler, SleepApneaHandler

class ExportAndSaveObserver:
    def __init__(self, db: PatientDatabase, export_format: str, export_file: str):
        self.db = db
        self.export_format = export_format
        self.export_file = export_file

    def on_diagnosed(self, patient: PatientData, symptoms: List[str], prescription: Prescription):
        # 1. 將診斷結果存為該病患的病例
        case = PatientCase(prescription, symptoms)
        patient.add_case(case)
        print(f"診斷完成！病患：{patient.name}, 處方：{prescription.name}")

        # 2. 執行匯出
        if self.export_format.lower() == 'json':
            self._export_json()
        elif self.export_format.lower() == 'csv':
            self._export_csv(patient, case)
        else:
            print("不支援的匯出格式")

    def _export_json(self):
        data = [p.to_dict() for p in self.db.patients.values()]
        with open(self.export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"資料已匯出至 {self.export_file}")

    def _export_csv(self, patient: PatientData, case: PatientCase):
        file_exists = os.path.isfile(self.export_file)
        with open(self.export_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Patient ID', 'Name', 'Time', 'Symptoms', 'Disease', 'Prescription', 'Medicines', 'Usage'])
            
            writer.writerow([
                patient.id, patient.name, case.case_time.isoformat(),
                ','.join(case.symptoms), case.prescription.potential_disease,
                case.prescription.name, ','.join(case.prescription.medicines),
                case.prescription.usage
            ])
        print(f"資料已匯出至 {self.export_file}")

class PrescriberSystemFacade:
    def __init__(self):
        self.db = PatientDatabase()
        self.prescriber = Prescriber()

    def run_diagnosis(self, json_path: str, diseases_txt_path: str, patient_id: str, symptoms: List[str], export_format: str, export_file: str):
        # 1. 初始化資料庫
        self.db.load_from_json(json_path)

        # 2. 構建並設定責任鏈
        rule_chain = self._build_rule_chain(diseases_txt_path)
        if rule_chain:
            self.prescriber.set_rule_chain(rule_chain)
        else:
            print("警告：沒有啟用的診斷規則。")
            return

        # 3. 註冊收尾觀察者 (存入資料庫與匯出檔案)
        observer = ExportAndSaveObserver(self.db, export_format, export_file)
        self.prescriber.add_observer(observer.on_diagnosed)

        # 4. 開始診斷
        patient = self.db.get_patient(patient_id)
        if patient:
            print(f"開始排隊診斷：{patient.name}...")
            self.prescriber.prescribe(patient, symptoms)
        else:
            print(f"錯誤：找不到病患 {patient_id}。")

    def _build_rule_chain(self, txt_path: str) -> DiagnosisHandler:
        enabled_diseases = []
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                enabled_diseases = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"Error: Diseases file {txt_path} not found.")

        # 簡單的 Mapping 與串列邏輯來組裝責任鏈
        handlers_map = {
            "COVID-19": Covid19Handler(),
            "Attractive": AttractiveHandler(),
            "SleepApneaSyndrome": SleepApneaHandler()
        }

        head = None
        current = None

        for disease in enabled_diseases:
            handler = handlers_map.get(disease)
            if handler:
                if head is None:
                    head = handler
                    current = head
                else:
                    current.set_next(handler)
                    current = handler

        return head
