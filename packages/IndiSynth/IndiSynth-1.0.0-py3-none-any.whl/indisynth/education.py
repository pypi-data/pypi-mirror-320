import random
import string

class EducationSynth:
    @staticmethod
    def generate_student_id():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    @staticmethod
    def generate_board_roll_number():
        return "".join([str(random.randint(0, 9)) for _ in range(10)])

    @staticmethod
    def generate_university_registration_number():
        return "".join([str(random.randint(0, 9)) for _ in range(12)])

    @staticmethod
    def generate_school_udise_code():
        return "".join([str(random.randint(0, 9)) for _ in range(11)])

    @staticmethod
    def generate_college_aishe_code():
        return "".join([str(random.randint(0, 9)) for _ in range(12)])
