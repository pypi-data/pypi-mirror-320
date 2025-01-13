import random
import string

class AgricultureSynth:
    @staticmethod
    def generate_kisan_credit_card_number():
        return "".join(random.choices(string.digits, k=16))

    @staticmethod
    def generate_farmer_registration_number():
        return f"FR-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_soil_health_card_number():
        return f"SH-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_pm_kisan_beneficiary_id():
        return "".join(random.choices(string.digits, k=12))

    @staticmethod
    def generate_agricultural_land_registration():
        return f"AL-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_pesticide_license_number():
        return f"PL-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_seed_license_number():
        return f"SL-{''.join(random.choices(string.digits, k=8))}"
