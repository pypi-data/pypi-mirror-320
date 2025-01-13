import random
import string

class UtilitiesSynth:
    @staticmethod
    def generate_electricity_consumer_number():
        return "".join(random.choices(string.digits, k=10))

    @staticmethod
    def generate_gas_connection_number():
        return "".join(random.choices(string.digits, k=12))

    @staticmethod
    def generate_water_connection_id():
        return f"WC-{''.join(random.choices(string.digits, k=10))}"

    @staticmethod
    def generate_broadband_customer_id():
        return "".join(random.choices(string.digits, k=12))

    @staticmethod
    def generate_dth_subscription_number():
        return "".join(random.choices(string.digits, k=10))
