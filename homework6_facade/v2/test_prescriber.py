import pytest
from unittest.mock import Mock, patch
import json
from models.enums import Symptom, PotentialDisease
from models.entities import PatientData, Prescription
from models.rules import Covid19Rule, AttractiveRule, SleepApneaRule
from models.observers import IPrescriberObserver, JsonExportObserver, CsvExportObserver
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
    # BMI = 70 / (1.7^2) = 24.2 < 26
    patient = PatientData(id="Thin", name="ThinBoy", gender="male", age=30, height=170.0, weight=70.0)
    symptoms = [Symptom.SNORE]
    prescription = rule.handle(patient, symptoms)
    assert prescription is None

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
    mock_observer = Mock()
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

# ==================== 整合測試：Facade 與 排隊機制 ====================

@patch('time.sleep') # 攔截 sleep, 不要真的等 3 秒
def test_facade_integration_and_observer(mock_sleep, tmp_path):
    # 建立虛擬檔案
    patients_json = tmp_path / "patients.json"
    patients_data = [
        {"id": "TEST1", "name": "Tester", "gender": "male", "age": 25, "height": 175.0, "weight": 70.0}
    ]
    patients_json.write_text(json.dumps(patients_data, ensure_ascii=False), encoding='utf-8')
    
    diseases_txt = tmp_path / "diseases.txt"
    diseases_txt.write_text("COVID-19\n", encoding='utf-8')
    
    # 初始化系統
    facade = PrescriptionSystemFacade(str(patients_json), str(diseases_txt))
    
    # 建立一個 Mock Observer 塞進系統
    mock_obs = Mock(spec=IPrescriberObserver)
    facade.prescriber.attach_observer(mock_obs)
    
    # 發起診斷
    facade.diagnose("TEST1", [Symptom.SNEEZE, Symptom.HEADACHE, Symptom.COUGH])
    
    # 確保隊列跑完
    facade.wait_for_completion()
    
    # 斷言：Sleep 是否被正確呼叫 (等同於進入了診斷流程，耗時 3 秒)
    mock_sleep.assert_called_once_with(3)
    
    # 斷言：Observer 是否成功收到結果 (成功被通知)
    mock_obs.update.assert_called_once()
    args, _kwargs = mock_obs.update.call_args
    assert args[0] == "TEST1"
    assert args[2].potential_disease == PotentialDisease.COVID_19

def test_json_observer_multiple_records(tmp_path):
    target_json = tmp_path / "test_output.json"
    observer = JsonExportObserver(str(target_json))
    
    # 第一筆
    p1 = Prescription(name="清冠一號", potential_disease=PotentialDisease.COVID_19, medicines=["清冠一號"], usage="...")
    observer.update("A123", [Symptom.COUGH], p1)
    
    # 第二筆
    p2 = Prescription(name="青春抑制劑", potential_disease=PotentialDisease.ATTRACTIVE, medicines=["假鬢角"], usage="...")
    observer.update("C111", [Symptom.SNEEZE], p2)
    
    # 讀取結果驗證
    results = json.loads(target_json.read_text(encoding='utf-8'))
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["patient_id"] == "A123"
    assert results[1]["patient_id"] == "C111"

def test_csv_observer_multiple_records(tmp_path):
    target_csv = tmp_path / "test_output.csv"
    observer = CsvExportObserver(str(target_csv))
    
    # 第一筆
    p1 = Prescription(name="清冠一號", potential_disease=PotentialDisease.COVID_19, medicines=["清冠一號"], usage="...")
    observer.update("A123", [Symptom.COUGH], p1)
    
    # 第二筆
    p2 = Prescription(name="青春抑制劑", potential_disease=PotentialDisease.ATTRACTIVE, medicines=["假鬢角"], usage="...")
    observer.update("C111", [Symptom.SNEEZE], p2)
    
    # 讀取結果驗證
    lines = target_csv.read_text(encoding='utf-8').strip().split("\n")
    assert len(lines) == 3 # 標題1行 + 資料2行
    assert lines[0] == "patient_id,symptoms,prescription_name,disease,medicines,usage"
    assert lines[1].startswith("A123")
    assert lines[2].startswith("C111")
