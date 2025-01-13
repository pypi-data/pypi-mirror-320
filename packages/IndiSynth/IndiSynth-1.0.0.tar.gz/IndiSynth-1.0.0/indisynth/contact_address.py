import random

class ContactAddressSynth:
    @staticmethod
    def generate_mobile_number():
        return random.choice(['6', '7', '8', '9']) + \
               "".join([str(random.randint(0, 9)) for _ in range(9)])

    @staticmethod
    def generate_pincode():
        return "".join([str(random.randint(1, 9))] + [str(random.randint(0, 9)) for _ in range(5)])

    STREET_NAMES = [
        "M.G. Road", "Church Street", "Brigade Road", "J.P. Nagar Main Road", "Bannerghatta Road",
        "Indiranagar 100 Feet Road", "Connaught Place", "Marine Drive", "Lodhi Road", 
        "Park Street", "Salt Lake Sector 5", "Gariahat Road", "C.G. Road", "Ashram Road",
        "Anna Salai", "Nungambakkam High Road", "Perambur Main Road", "Banjara Hills Road",
        "Gachibowli Main Road", "Begumpet Road", "S.G. Highway", "Kaloor Road", "Vyttila Road",
        "Palarivattom Junction", "Jayanagar 4th Block", "Koramangala 80 Feet Road",
        "Mysore Road", "Rajaji Salai", "Trichy Road", "Coimbatore Avinashi Road",
        "MG Marg", "Rajpur Road", "Civil Lines", "Ambedkar Road", "Lal Bahadur Shastri Marg",
        "Race Course Road", "Chandni Chowk", "Hauz Khas Village", "Defence Colony", 
        "Vasant Vihar Main Road", "Kamla Nagar Main Road", "Sector 18 Market Road"
    ]

    # Mapping of cities to states
    CITIES_TO_STATES = {
        "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
        "Bengaluru": "Karnataka", "Mysuru": "Karnataka", "Hubli": "Karnataka",
        "Hyderabad": "Telangana", "Warangal": "Telangana", "Nizamabad": "Telangana",
        "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra",
        "Kolkata": "West Bengal", "Darjeeling": "West Bengal", "Siliguri": "West Bengal",
        "Delhi": "Delhi", "New Delhi": "Delhi", "Noida": "Uttar Pradesh",
        "Lucknow": "Uttar Pradesh", "Kanpur": "Uttar Pradesh", "Varanasi": "Uttar Pradesh",
        "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat",
        "Jaipur": "Rajasthan", "Jodhpur": "Rajasthan", "Udaipur": "Rajasthan",
        "Patna": "Bihar", "Gaya": "Bihar", "Bhagalpur": "Bihar",
        "Bhopal": "Madhya Pradesh", "Indore": "Madhya Pradesh", "Gwalior": "Madhya Pradesh",
        "Thiruvananthapuram": "Kerala", "Kochi": "Kerala", "Kozhikode": "Kerala",
        "Ranchi": "Jharkhand", "Jamshedpur": "Jharkhand", "Dhanbad": "Jharkhand",
        "Shimla": "Himachal Pradesh", "Dharamshala": "Himachal Pradesh", "Kullu": "Himachal Pradesh",
        "Dehradun": "Uttarakhand", "Haridwar": "Uttarakhand", "Rishikesh": "Uttarakhand",
        "Guwahati": "Assam", "Dibrugarh": "Assam", "Silchar": "Assam"
    }
    @staticmethod
    def generate_address():
        # Generate a random door number (1-4 digits)
        door_number = f"{random.randint(1, 9999)}"

        # Select a random city and its corresponding state
        city, state = random.choice(list(ContactAddressSynth.CITIES_TO_STATES.items()))
        
        # Randomly select a street name
        street = random.choice(ContactAddressSynth.STREET_NAMES)
        
        # Generate a random 6-digit pin code
        pin_code = f"{random.randint(100000, 999999)}"
        
        # Construct the address
        address = f"{door_number}, {street}, {city}, {state} - {pin_code}, India"
        return address
