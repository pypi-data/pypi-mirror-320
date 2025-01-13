import random
import string

class LegalDocumentationSynth:
    @staticmethod
    def generate_court_case_number():
        return f"CASE-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_fir_number():
        return f"FIR-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_advocate_registration():
        return f"ADV-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_notary_license_number():
        return f"NOT-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_marriage_registration():
        return f"MAR-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_will_registration_number():
        return f"WILL-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_power_of_attorney_number():
        return f"POA-{''.join(random.choices(string.digits, k=10))}"
