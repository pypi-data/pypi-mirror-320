import random
import string

class EmploymentSynth:
    STATE_CODES = [
        "KA", "UP", "MH", "TN", "DL", "GJ", "WB", "RJ", "KL", "AP", "MP", 
        "HR", "OR", "PB", "CT", "AS", "BR", "CG", "GA", "HP", "JK", "JH", 
        "KL", "MN", "ML", "MZ", "NL", "PY", "SK", "TR", "UT"
    ]

    @staticmethod
    def generate_epf_number():
        # State code
        state_code = random.choice(EmploymentSynth.STATE_CODES)

        # Regional office code (3 letters)
        regional_office_code = ''.join(random.choices(string.ascii_uppercase, k=3))

        # Establishment ID (7 digits)
        establishment_id = ''.join(random.choices(string.digits, k=7))

        # Extension code (3 digits)
        extension_code = ''.join(random.choices(string.digits, k=3))

        # Employee unique EPF account number (7 digits)
        employee_number = ''.join(random.choices(string.digits, k=7))

        # Combine all parts to form the EPF number
        return f"{state_code}{regional_office_code}{establishment_id}{extension_code}{employee_number}"

    @staticmethod
    def generate_esi_number():
        return "".join([str(random.randint(0, 9)) for _ in range(10)])

    @staticmethod
    def generate_uan_number():
        return "".join([str(random.randint(0, 9)) for _ in range(12)])

    @staticmethod
    def generate_government_employee_id():
        return f"GOV{''.join(random.choices(string.digits, k=7))}"
