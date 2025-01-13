import random
import string

class ProfessionalSynth:
    @staticmethod
    def generate_medical_registration_number():
        return f"MCI-{random.randint(100000, 999999)}"

    @staticmethod
    def generate_bar_council_registration():
        return f"BAR-{random.randint(10000, 99999)}"

    @staticmethod
    def generate_pharmacy_license_number():
        return f"PH-{random.randint(100000, 999999)}"

    @staticmethod
    def generate_chartered_accountant_registration():
        return f"CA-{random.randint(10000, 99999)}"

    @staticmethod
    def generate_company_secretary_membership_number():
        return f"CS-{random.randint(10000, 99999)}"

    @staticmethod
    def generate_insurance_agent_license():
        return f"IA-{random.randint(10000, 99999)}"
