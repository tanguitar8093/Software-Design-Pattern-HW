from enum import Enum

class Symptom(Enum):
    HEADACHE = "Headache"
    COUGH = "Cough"
    SNEEZE = "Sneeze"
    SNORE = "Snore"

class PotentialDisease(Enum):
    COVID_19 = "COVID-19"
    ATTRACTIVE = "Attractive"
    SLEEP_APNEA_SYNDROME = "SleepApneaSyndrome"
