import random
import string

class BusinessOperationsSynth:
    @staticmethod
    def generate_factory_license_number():
        return f"FL-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_trademark_registration():
        return f"TM-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_patent_number():
        return f"PT-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_copyright_registration():
        return f"CR-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_esic_establishment_code():
        return "".join(random.choices(string.digits, k=17))

    @staticmethod
    def generate_pf_establishment_code():
        return f"PF-{''.join(random.choices(string.digits, k=12))}"

    @staticmethod
    def generate_labour_license_number():
        return f"LL-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_industrial_license_number():
        return f"IL-{''.join(random.choices(string.digits, k=10))}"
