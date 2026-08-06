# 處方診斷系統 OOD（責任鏈＋觀察者＋Facade）

```mermaid
classDiagram
direction TB

class Client {
    +main() void
}

class PatientData {
    +str id
    +str name
    +str gender
    +int age
    +float height
    +float weight
    +List~PatientCase~ patient_cases
    +add_case(patient_case) void
    +to_dict() dict
}

class PatientCase {
    +Prescription prescription
    +List~str~ symptoms
    +datetime case_time
    +to_dict() dict
}

class Prescription {
    +str name
    +str potential_disease
    +List~str~ medicines
    +str usage
    +to_dict() dict
}

PatientData "1" *-- "0..*" PatientCase : patient_cases
PatientCase "1" *-- "1" Prescription : prescription

class PatientDatabase {
    -Dict~str, PatientData~ patients
    +load_from_json(file_path) void
    +get_patient(patient_id) PatientData
}

class PrescriptionDemand {
    +PatientData patient
    +List~str~ symptoms
}

class Prescriber {
    -DiagnosisHandler rule_chain_head
    -Queue~PrescriptionDemand~ demands_queue
    -List~Callable~ observers
    +set_rule_chain(handler) void
    +add_observer(callback) void
    +prescribe(patient, symptoms) void
    -_worker_loop() void
    -_notify_observers(patient, symptoms, prescription) void
    +stop() void
}

Prescriber *-- "1" PrescriptionDemand : FIFO queue
Prescriber o-- "0..*" "callback" ExportAndSaveObserver : on_diagnosed

class DiagnosisHandler {
    <<abstract>>
    -DiagnosisHandler _next_handler
    +set_next(handler) DiagnosisHandler
    +handle(patient, symptoms) Prescription
}

class Covid19Handler {
    +handle(patient, symptoms) Prescription
}
class AttractiveHandler {
    +handle(patient, symptoms) Prescription
}
class SleepApneaHandler {
    +handle(patient, symptoms) Prescription
}

DiagnosisHandler <|-- Covid19Handler
DiagnosisHandler <|-- AttractiveHandler
DiagnosisHandler <|-- SleepApneaHandler
DiagnosisHandler --> "0..1" DiagnosisHandler : next handler
Prescriber o-- "0..1" DiagnosisHandler : rule_chain_head
DiagnosisHandler ..> PatientData : evaluates
DiagnosisHandler ..> Prescription : creates

class ExportAndSaveObserver {
    -PatientDatabase db
    -str export_format
    -str export_file
    +on_diagnosed(patient, symptoms, prescription) void
    -_export_json() void
    -_export_csv(patient, patient_case) void
}

ExportAndSaveObserver --> PatientDatabase : stores case / exports
ExportAndSaveObserver ..> PatientCase : creates

class PrescriberSystemFacade {
    -PatientDatabase db
    -Prescriber prescriber
    +run_diagnosis(json_path, diseases_txt_path, patient_id, symptoms, export_format, export_file) void
    -_build_rule_chain(diseases_txt_path) DiagnosisHandler
}

PrescriberSystemFacade *-- PatientDatabase : owns
PrescriberSystemFacade *-- Prescriber : owns
PrescriberSystemFacade ..> DiagnosisHandler : builds from disease TXT
PrescriberSystemFacade ..> ExportAndSaveObserver : creates / registers callback
Client --> PrescriberSystemFacade : one-call diagnosis
```
