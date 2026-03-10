from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Movie, Payment, project
from datetime import datetime
import base64
import requests

# ACTIVITY LOGGER
from app.utils.activity_logger import log_activity

payment_bp = Blueprint("payment", __name__)

# Helper: normalize phone
def normalize_phone(phone):
    phone = phone.replace(" ", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if len(phone) != 12 or not phone.isdigit():
        return None
    return phone


# Helper: get MPESA access token
def get_mpesa_access_token():
    consumer_key = current_app.config["MPESA_CONSUMER_KEY"]
    consumer_secret = current_app.config["MPESA_CONSUMER_SECRET"]
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json().get("access_token")


@payment_bp.route("/pay", methods=["POST"])
def initiate_payment():

    data = request.get_json()
    phone_input = data.get("phone")
    item_id = data.get("item_id")

    phone = normalize_phone(phone_input)
    if not phone:
        return jsonify({"success": False, "error": "Invalid phone format"}), 400

    movie = Movie.query.get_or_404(item_id)
    amount = movie.price

    # ACTIVITY LOG (payment started)
    log_activity(
        action="start_payment",
        item_type="project",
        item_id=project.id,
        payment_type="mpesa"
    )

    access_token = get_mpesa_access_token()
    shortcode = current_app.config["MPESA_SHORTCODE"]
    passkey = current_app.config["MPESA_PASSKEY"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": current_app.config["MPESA_CALLBACK_URL"],
        "AccountReference": f"movie_{movie.id}",
        "TransactionDesc": f"Payment for {movie.title}"
    }

    response = requests.post(stk_url, json=payload, headers=headers)
    res_data = response.json()

    if "CheckoutRequestID" in res_data:

        payment = Payment(
            checkout_request_id=res_data["CheckoutRequestID"],
            merchant_request_id=res_data["MerchantRequestID"],
            phone_number=phone,
            amount=amount,
            item_type="movie",
            item_id=movie.id,
            status="pending"
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({"success": True, "checkout_request_id": res_data["CheckoutRequestID"]})

    return jsonify({"success": False, "error": res_data})


# -----------------------------
# MPESA Callback
# -----------------------------
@payment_bp.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    try:

        data = request.get_json()
        callback = data["Body"]["stkCallback"]

        checkout_request_id = callback["CheckoutRequestID"]
        result_code = callback["ResultCode"]

        payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()

        if not payment:
            return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

        payment.result_code = result_code

        if result_code == 0:

            metadata = callback["CallbackMetadata"]["Item"]

            amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
            phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")

            if float(amount) == float(payment.amount) and str(phone) == payment.phone_number:

                payment.status = "paid"

                # ACTIVITY LOG (successful payment)
                log_activity(
                    action="payment_success",
                    target_type="movie",
                    target_id=payment.item_id,
                    payment_type="mpesa",
                    page="/mpesa/callback"
                )

            else:

                payment.status = "failed"

                # ACTIVITY LOG (payment validation failed)
                log_activity(
                    action="payment_failed",
                    target_type="movie",
                    target_id=payment.item_id,
                    payment_type="mpesa"
                )

        else:

            payment.status = "failed"

            # ACTIVITY LOG (payment cancelled or failed)
            log_activity(
                action="payment_failed",
                target_type="movie",
                target_id=payment.item_id,
                payment_type="mpesa"
            )

        db.session.commit()

        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception as e:
        return jsonify({"ResultCode": 1, "ResultDesc": str(e)}), 500


# -----------------------------
# Check Payment Status
# -----------------------------
@payment_bp.route("/payment/status/<checkout_request_id>", methods=["GET"])
def payment_status(checkout_request_id):

    payment = Payment.query.filter_by(
        checkout_request_id=checkout_request_id
    ).first_or_404()

    return jsonify({"status": payment.status})