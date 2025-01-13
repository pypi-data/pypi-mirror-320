import random
import string
from datetime import date

class BankingFinanceSynth:
    @staticmethod
    def generate_bank_account_number():
        return "".join([str(random.randint(0, 9)) for _ in range(12)])
    

    @staticmethod
    def generate_ifsc_code():

        bank_codes = [
        "HDFC", "ICIC", "SBIN", "PNB", "AXIS", "BOI", "IOBA", "KARB",
        "IDFB", "YESB", "UTIB", "CNRB", "BARB", "VIJB", "UBIN", "PUNB"]
        
        # Randomly select a bank code
        bank_code = random.choice(bank_codes)
         # Generate branch code
        branch_code = ''.join(random.choices(string.digits, k=6))
        return f"{bank_code}0{branch_code}"

    @staticmethod
    def generate_micr_code():
        return "".join([str(random.randint(0, 9)) for _ in range(9)])

    @staticmethod
    def generate_upi_id():
        return f"{''.join(random.choices(string.ascii_lowercase, k=10))}@upi"

    @staticmethod
    def generate_credit_card_number():
        return "".join([str(random.randint(0, 9)) for _ in range(16)])

    @staticmethod
    def generate_debit_card_number():
        return "".join([str(random.randint(0, 9)) for _ in range(16)])

    @staticmethod
    def generate_lic_policy_number():
        return "".join([str(random.randint(0, 9)) for _ in range(10)])

    @staticmethod
    def generate_mutual_fund_folio_number():
        return "".join([str(random.randint(0, 9)) for _ in range(10)])

    @staticmethod
    def generate_demat_account_number():
        return "".join([str(random.randint(0, 9)) for _ in range(16)])
    
    @staticmethod
    def generate_card_expiry_date():
    
        # Current year and month
        current_year = date.today().year
        current_month = date.today().month

        # Randomly pick a year within the next 10 years
        expiry_year = random.randint(current_year, current_year + 10)

        # If the year is the current year, ensure the month is not earlier than the current month
        if expiry_year == current_year:
            expiry_month = random.randint(current_month, 12)
        else:
            expiry_month = random.randint(1, 12)

        # Format month and year as MM/YY
        return f"{expiry_month:02}/{str(expiry_year)[-2:]}"
