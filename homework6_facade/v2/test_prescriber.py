import pytest
from unittest.mock import patch, MagicMock
import json
import os

from models.enums import Symptom, PotentialDisease
from models.entities import PatientData
from models.rules import Covid19Rule, AttractiveRule, SleepApneaRule
from facade import PrescriptionSystemFacade

# ================= 1. 規則邏輯單元測試 (Unit Tests for Rules) =================

def test_covid19_rule_success():
    rule = Covid19Rule()
    # 測試正確條件：Headache, Cough, Sneeze
    patient = PatientData("A1", "Test", "male", 30, 175.0, 70.0)
    result = rule.diagnose(patient, [Symptom.HEADACHE, Symptom.COUGH, Symptom.SNEEZE])
    
    assert result is not None
    assert result.potential_disease == PotentialDisease.COVID_19
    assert result.name == "清冠一號"

def test_covid19_rule_failure():
    rule = Covid19Rule()
    # 測試缺少條件 (少咳嗽)
    patient = PatientData("A1", "Test", "male", 30, 175.0, 70.0)
    result = rule.diagnose(patient, [Symptom.HEADACHE, Symptom.SNEEZE])
    assert result is None

def test_attractive_rule_success():
    rule = AttractiveRule()
    # 測試正確條件：18歲, female, Sneeze
    patient = PatientData("C1", "Alice", "female", 18, 160.0, 50.0)
    result = rule.diagnose(patient, [Symptom.SNEEZE])
    
    assert result is not None
    assert result.potential_disease == PotentialDisease.ATTRACTIVE
    assert "假鬢角" in result.medicines

def test_attractive_rule_failure_age():
    rule = AttractiveRule()
    # 測試錯誤年齡 (19歲)
    patient = PatientData("C2", "Alice", "female", 19, 160.0, 50.0)
    result = rule.diagnose(patient, [Symptom.SNEEZE])
    assert result is None

def test_sleep_apnea_rule_success():
    rule = SleepApneaRule()
    # 測試正確條件：BMI > 26 (100 / 1.7^2 = 34.6), Snore
    patient = PatientData("B1", "Bob", "male", 40, 170.0, 100.0)
    result = rule.diagnose(patient, [Symptom.SNORE])
    
    assert result is not None
    assert result.potential_disease == PotentialDisease.SLEEP_APNEA_SYNDROME
    assert "一捲膠帶" in result.medicines

def test_sleep_apnea_rule_failure_bmi():
    rule = SleepApneaRule()
    # 測試 BMI 過低 (70 / 1.75^2 = 22.8)
    patient = PatientData("B2", "Tom", "male", 25, 175.0, 70.0)
    result = rule.diagnose(patient, [Symptom.SNORE])
    assert result is None

# ================= 2. 系統整合測試 (Integration Tests with Mock) =================

@pytest.fixture
def setup_test_files(tmp_path):
    """準備測試用的假 JSON 和純文字檔案，避免動到真實資料"""
    patients_file = tmp_path / "test_patients.json"
    patients_data = [
        {"id": "P_COVID", "name": "Tom", "gender": "male", "age": 25, "height": 175.0, "weight": 70.0},
        {"id": "P_APNEA", "name": "Jerry", "gender": "male", "age": 40, "height": 170.0, "weight": 100.0},
        {"id": "P_ATTRACTIVE", "name": "Alice", "gender": "female", "age": 18, "height": 160.0, "weight": 50.0}
    ]
    patients_file.write_text(json.dumps(patients_data), encoding="utf-8")
    
    diseases_file = tmp_path / "test_diseases.txt"
    diseases_file.write_text("COVID-19\nAttractive\nSleepApneaSyndrome", encoding="utf-8")
    
    return str(patients_file), str(diseases_file)

@patch("models.prescriber.time.sleep")
def test_facade_diagnose_integration(mock_sleep, setup_test_files):
    """測試整個 Facade 從呼叫、流過規則鏈到觀察者被通知的流程"""
    json_path, txt_path = setup_test_files
    
    facade = PrescriptionSystemFacade(json_path, txt_path)
    
    # 這裡我們掛載一個 Mock Observer 攔截結果，而不真的寫入檔案
    mock_observer = MagicMock()
    facade.prescriber.attach_observer(mock_observer)
    
    # 發起測試
    facade.diagnose("P_COVID", [Symptom.HEADACHE, Symptom.COUGH, Symptom.SNEEZE])
    facade.diagnose("P_ATTRACTIVE", [Symptom.SNEEZE])
    
    # 等待執行緒結束
    facade.wait_for_completion()
    
    # 驗證 1: Prescriber 的 3 秒等待機制有被呼叫兩次（因為兩筆診斷）
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(3)
    
    # 驗證 2: 觀察者有收到兩次診斷處方的結果
    assert mock_observer.update.call_count == 2
    
    # 驗證第一次發送的資料是預期的 COVID-19
    call_args_1 = mock_observer.update.call_args_list[0][0]
    assert call_args_1[0] == "P_COVID"
    assert call_args_1[2].potential_disease == PotentialDisease.COVID_19
    
    # 驗證第二次發送的資料是預期的 Attractive
    call_args_2 = mock_observer.update.call_args_list[1][0]
    assert call_args_2[0] == "P_ATTRACTIVE"
    assert call_args_2[2].potential_disease == PotentialDisease.ATTRACTIVE
