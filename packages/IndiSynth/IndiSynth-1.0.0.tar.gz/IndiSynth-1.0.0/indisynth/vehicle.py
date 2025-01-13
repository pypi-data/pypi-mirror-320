import random
import string

import random
import string

class VehicleSynth:
    STATE_CODES = [
        "AN", "AP", "AR", "AS", "BR", "CH", "CT", "DN", "DD", "DL", "GA", "GJ", "HR", "HP", "JK",
        "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OR", "PY", "PB", "RJ",
        "SK", "TN", "TG", "TR", "UP", "UT", "WB"
    ]

    @staticmethod
    def generate_vehicle_registration_number():
        # State code
        state_code = random.choice(VehicleSynth.STATE_CODES)

        # District code (2 digits)
        district_code = random.randint(10, 99)

        # Alphabets after district code
        post_district_letters = ''.join(random.choices(string.ascii_uppercase, k=2))

        # Unique number (4 digits)
        unique_number = random.randint(1000, 9999)

        # Combine to form vehicle registration number
        return f"{state_code}{district_code}{post_district_letters}{unique_number}"


    @staticmethod
    def generate_rc_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=15))

    @staticmethod
    def generate_chassis_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=17))

    @staticmethod
    def generate_engine_number():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=15))

    @staticmethod
    def generate_driving_school_license_number():
        return f"DS-{''.join(random.choices(string.digits, k=6))}"

    @staticmethod
    def generate_pollution_certificate_number():
        return f"PC-{''.join(random.choices(string.digits, k=10))}"
