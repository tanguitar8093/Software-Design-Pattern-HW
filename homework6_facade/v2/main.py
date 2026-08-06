import os
import sys

# Ensure python can import from the current directory
sys.path.append(os.path.dirname(__file__))

from facade import PrescriptionSystemFacade
from models.enums import Symptom


def main():
    # Setup paths
    base_dir = os.path.dirname(__file__)
    patients_json = os.path.join(base_dir, "patients.json")
    diseases_txt = os.path.join(base_dir, "diseases.txt")
    output_json = os.path.join(base_dir, "output.json")
    
    # Client 1~3 行使用
    # 1. 裝著病患資料的 JSON 檔案名稱 & 裝著支援潛在疾病診斷的純文字檔案名稱
    facade = PrescriptionSystemFacade(patients_json, diseases_txt)
    
    # 2. 要求匯出 JSON 格式
    facade.set_export_format("JSON", output_json)
    
    # 3. 呼叫診斷
    print("發起 A123456789 (新冠患者) 的診斷...")
    facade.diagnose("A123456789", [Symptom.HEADACHE, Symptom.COUGH, Symptom.SNEEZE])
    
    # 測試多位病患同時要求診斷
    print("同時發起 B987654321 (睡眠呼吸中止症) 的診斷...")
    facade.diagnose("B987654321", [Symptom.SNORE])
    
    print("同時發起 C111111111 (Attractive) 的診斷...")
    facade.diagnose("C111111111", [Symptom.SNEEZE])

    print("診斷器正在背景排隊處理，每次耗時 3 秒...")
    facade.wait_for_completion()
    print("所有診斷結束，請查看 output.json！")

if __name__ == "__main__":
    main()
