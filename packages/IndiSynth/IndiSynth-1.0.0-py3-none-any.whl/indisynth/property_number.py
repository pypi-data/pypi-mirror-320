import random
import string

class PropertySynth:
    @staticmethod
    def generate_property_registration_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

    @staticmethod
    def generate_khata_number():
        return f"K-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_survey_number():
        return f"S-{''.join(random.choices(string.digits, k=6))}"

    @staticmethod
    def generate_property_tax_assessment_number():
        return f"PT-{''.join(random.choices(string.digits, k=10))}"
