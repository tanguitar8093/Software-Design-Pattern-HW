from facade import PrescriberSystemFacade
import time

def generate_test_data():
    import json
    # 建立測試病患資料
    patients = [
        {"id": "A123456789", "name": "John Doe", "gender": "male", "age": 30, "height": 175, "weight": 90},
        {"id": "B987654321", "name": "Jane Smith", "gender": "female", "age": 18, "height": 160, "weight": 50}
    ]
    with open("homework6_facade/patients.json", "w", encoding='utf-8') as f:
        json.dump(patients, f, indent=4)

    # 建立測試支援疾病清單
    with open("homework6_facade/diseases.txt", "w", encoding='utf-8') as f:
        f.write("COVID-19\nAttractive\nSleepApneaSyndrome\n")

if __name__ == "__main__":
    # 準備假資料供測試
    generate_test_data()

    # --- Client 操作區 ---
    # 僅需 1~3 行即可啟動，對應需求 C-3
    system = PrescriberSystemFacade()
    
    # 病患A (BMI > 26 (29.39) 且打呼)
    system.run_diagnosis("homework6_facade/patients.json", "homework6_facade/diseases.txt", "A123456789", ["snore", "fever"], "json", "homework6_facade/output.json")
    
    # 病患B (18歲女性 且打噴嚏)
    system.run_diagnosis("homework6_facade/patients.json", "homework6_facade/diseases.txt", "B987654321", ["sneeze", "cough"], "csv", "homework6_facade/output.csv")

    print("[Main] 已將診斷任務送入佇列，等待各 3 秒的診斷過程...")
    
    # 讓主程式等待以觀察背景執行緒的輸出
    system.prescriber.demands_queue.join()
    system.prescriber.stop()
    print("[Main] 所有診斷任務結束。")