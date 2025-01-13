import random
import string

class TravelTourismSynth:
    @staticmethod
    def generate_air_india_frequent_flyer_number():
        return f"AI-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

    @staticmethod
    def generate_railway_pnr():
        return "".join(random.choices(string.digits, k=10))

    @staticmethod
    def generate_tourist_guide_license():
        return f"TGL-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_hotel_registration_number():
        return f"HR-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_travel_agency_license():
        return f"TA-{''.join(random.choices(string.digits, k=8))}"

    @staticmethod
    def generate_tourist_visa_number():
        return f"VISA-{''.join(random.choices(string.digits, k=12))}"

    @staticmethod
    def generate_international_driving_permit():
        return f"IDP-{''.join(random.choices(string.digits, k=10))}"
