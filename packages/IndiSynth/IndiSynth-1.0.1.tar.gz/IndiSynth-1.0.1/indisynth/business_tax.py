import random
import string

class BusinessTaxSynth:

    STATE_CODES = [f"{i:02}" for i in range(1, 36)]  # State codes 01 to 35

    STATE_TEXT = [
        "AN", "AP", "AR", "AS", "BR", "CH", "CT", "DN", "DD", "DL", "GA", "GJ", "HR", "HP", "JK",
        "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OR", "PY", "PB", "RJ",
        "SK", "TN", "TG", "TR", "UP", "UT", "WB"
    ]

    @staticmethod
    def generate_gst():
        state_code = random.choice(BusinessTaxSynth.STATE_CODES)
        pan = ''.join(random.choices(string.ascii_uppercase, k=5)) + \
                ''.join(random.choices(string.digits, k=4)) + \
                    random.choice(string.ascii_uppercase)
        entity_number = str(random.randint(1, 9))
        default_z = "Z"
        check_code = random.choice(string.ascii_uppercase + string.digits)
        return f"{state_code}{pan}{entity_number}{default_z}{check_code}"

    @staticmethod
    def generate_cin():
        listing_status = "L"  # Single letter for listing status
        industry_code = ''.join(random.choices(string.digits, k=5))  # Five digits for industry
        roc_code = random.choice(BusinessTaxSynth.STATE_TEXT)  # Two-letter state/ROC code
        incorporation_year = str(random.randint(1900, 2025))  # Four-digit year of incorporation
        company_type = random.choice(["PTC", "PLC", "FTC", "OPC"])  # Company type
        unique_identifier = ''.join(random.choices(string.digits, k=6))  # Six-digit unique identifier
        return f"{listing_status}{industry_code}{roc_code}{incorporation_year}{company_type}{unique_identifier}"


    @staticmethod
    def generate_tan():
        prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
        state_code = random.choice(string.ascii_uppercase)  # State code letter
        numeric_part = ''.join(random.choices(string.digits, k=5))  # Numeric part
        checksum = random.choice(string.ascii_uppercase)
        return f"{prefix}{state_code}{numeric_part}{checksum}"

    @staticmethod
    def generate_udyam_aadhaar():
        return ''.join(random.choices(string.digits, k=12))
