import random
import string

class PersonalIdentitySynth:
    @staticmethod
    def generate_aadhaar():
        return "".join([str(random.randint(0, 9)) for _ in range(12)])

    @staticmethod
    def generate_pan(last_name_initial: str = 'A') -> str:
        # Ensure the last name initial is a single uppercase letter
        if not (last_name_initial.isalpha() and len(last_name_initial) == 1):
            raise ValueError("Last name initial must be a single alphabet character.")

        # First three characters: Random alphabets
        first_three = ''.join(random.choices(string.ascii_uppercase, k=3))
        
        # Fourth character: PAN holder's status
        # Example categories: 'P' (Individual), 'C' (Company), 'H' (Hindu Undivided Family), 'F' (Firm), 'A' (Association of Persons), etc.
        pan_status = random.choice(['P', 'C', 'T', 'H', 'F', 'A'])
        
        # Fifth character: First letter of last name
        fifth_char = last_name_initial.upper()
        
        # Next four characters: Random numeric sequence
        numeric_sequence = f"{random.randint(1, 9999):04d}"
        
        # Last character: Check digit (random alphabet)
        check_digit = random.choice(string.ascii_uppercase)
        
        # Combine all parts to form the PAN
        pan = f"{first_three}{pan_status}{fifth_char}{numeric_sequence}{check_digit}"
        return pan

    @staticmethod
    def generate_voter_id():
        return random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase) + \
               "".join(random.choices(string.digits, k=7))

    @staticmethod
    def generate_passport_number():
        letter = random.choice(string.ascii_uppercase)  # Random alphabet
        digits = f"{random.randint(1000000, 9999999)}"  # 7 random digits
        return f"{letter}{digits}"
    
    # List of Indian state and union territory codes
    STATE_CODES = [
        "AN", "AP", "AR", "AS", "BR", "CH", "CT", "DN", "DD", "DL", "GA", "GJ", "HR", "HP", "JK",
        "JH", "KA", "KL", "LA", "LD", "MP", "MH", "MN", "ML", "MZ", "NL", "OR", "PY", "PB", "RJ",
        "SK", "TN", "TG", "TR", "UP", "UT", "WB"
    ]

    @staticmethod
    def generate_driving_license():
        state_code = random.choice(PersonalIdentitySynth.STATE_CODES)  # Random state code
        two_digits = f"{random.randint(10, 99)}"  # Two random digits
        year = random.randint(1980, 2024)  # Random year between 1980 and 2023
        unique_number = f"{random.randint(1000000, 9999999)}"  # 7 random digits
        return f"{state_code}{two_digits}{year}{unique_number}"

