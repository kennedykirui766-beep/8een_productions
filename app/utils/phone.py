# app/utils/phone.py

def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("07"):
        phone = "+254" + phone[1:]
    return phone