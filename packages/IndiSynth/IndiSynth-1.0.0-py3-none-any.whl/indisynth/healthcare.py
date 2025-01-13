import random
import string

class HealthcareSynth:
    @staticmethod
    def generate_abha_number():
        return "".join(random.choices(string.digits, k=14))

    @staticmethod
    def generate_health_insurance_policy_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

    @staticmethod
    def generate_hospital_registration_number():
        return f"HOSP-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_medical_record_number():
        return f"MRN-{''.join(random.choices(string.digits, k=12))}"

    @staticmethod
    def generate_vaccine_certificate_number():
        return f"VAC-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_blood_donor_card_number():
        return f"BD-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_cghs_beneficiary_id():
        return "".join(random.choices(string.digits, k=12))
