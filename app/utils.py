import re

def normalize_phone(phone):
    phone = phone.strip()

    # Accept only 07XXXXXXXX
    if re.match(r"^07\d{8}$", phone):
        return "254" + phone[1:]

    return None
