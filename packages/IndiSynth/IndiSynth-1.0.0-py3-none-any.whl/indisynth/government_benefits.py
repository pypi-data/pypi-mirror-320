import random
import string

class GovernmentBenefitsSynth:
    @staticmethod
    def generate_bpl_card_number():
        return "".join(random.choices(string.digits, k=12))

    @staticmethod
    def generate_pension_payment_order():
        return f"PPO-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_scholarship_id():
        return f"SC-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_social_security_number():
        return "".join(random.choices(string.digits, k=9))

    @staticmethod
    def generate_disability_id_card():
        return f"DID-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_senior_citizen_card_number():
        return f"SC-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_freedom_fighter_pass_number():
        return f"FF-{''.join(random.choices(string.digits, k=10))}"
