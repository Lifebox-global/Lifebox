from flask import Flask, request, jsonify
from datetime import datetime
import os
import requests
import json

app = Flask(__name__)

sos_records = []

SOS_FILE = "sos_history.json"

if os.path.exists(SOS_FILE):
    try:
        with open(SOS_FILE, "r") as file:
            sos_records = json.load(file)
    except:
        pass
emergency_contacts = [
    {
        "name": "Ukeje Chiwando",
        "email": "ukejechinwendustanley5511@gmail.com",
        "phone": "07071797707"
    }
]

CONTACTS_FILE = "emergency_contacts.json"

if os.path.exists(CONTACTS_FILE):
    try:
        with open(CONTACTS_FILE, "r") as file:
            emergency_contacts = json.load(file)
    except:
        pass
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
SENDER_EMAIL = "ukejechinwendustanley5511@gmail.com"
SENDER_NAME = "LifeBox Emergency"

ROBASE_API_KEY = os.environ.get("ROBASE_API_KEY", "").strip()
ROBASE_API_URL = "https://api.robase.dev/v1/sms/send"


def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("0"):
        phone = "+234" + phone[1:]
    elif phone.startswith("234"):
        phone = "+" + phone

    return phone

def send_sms_alert(phone, message):
    try:
        api_key = os.environ.get("ROBASE_API_KEY", "").strip()

        if not api_key:
            return False, "Robase API key is not configured."

        phone = normalize_phone(phone)

        data = {
            "phone_number": phone,
            "message": message
        }

        response = requests.post(
            ROBASE_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=20
        )

        print(
            "ROBASE RESPONSE:",
            response.status_code,
            response.text
        )

        if response.ok:

            try:
                result = response.json()
            except:
                result = {}

            status = str(
                result.get("status", "")
            ).lower()

            if status == "pending":
                return True, (
                    "SMS accepted by Robase "
                    "and is pending delivery."
                )

            if status in ["sent", "delivered"]:
                return True, (
                    "SMS reported as delivered."
                )

            return True, (
                "SMS request accepted by Robase. "
                "Delivery status is being processed."
            )

        return False, (
            f"Robase SMS failed: "
            f"{response.text}"
        )

    except Exception as e:

        print(
            "ROBASE SMS ERROR:",
            e
        )

        return False, str(e)


@app.route("/")
def home():
    return """
<!DOCTYPE html>

<html>

<head>

    <title>LifeBox Emergency Network</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>

        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .header {
            background: #d32f2f;
            color: white;
            text-align: center;
            padding: 25px 15px;
        }

        .header h1 {
            margin: 0;
            font-size: 34px;
        }

        .header p {
            margin-top: 8px;
            font-size: 16px;
        }

        .container {
            max-width: 650px;
            margin: 20px auto;
            padding: 0 15px;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }

        .card h2 {
            margin-top: 0;
            color: #333;
        }

        .contact {
            background: #f8f8f8;
            padding: 15px;
            margin-top: 15px;
            border-radius: 8px;
            border-left: 4px solid #d32f2f;
        }

        input {
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 16px;
        }

        button {
            border: none;
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 16px;
            cursor: pointer;
        }

        .add-button {
            background: #1976d2;
            color: white;
        }

        .save-button {
            background: #388e3c;
            color: white;
        }

        .sos-button {
            display: block;
            width: 100%;
            background: #d32f2f;
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            border-radius: 12px;
        }

        .history-button {
            display: block;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
            background: #555;
            color: white;
            text-decoration: none;
            padding: 13px;
            border-radius: 8px;
            margin-top: 15px;
        }

        #status {
            margin-top: 20px;
            font-weight: bold;
            text-align: center;
        }

        #contactStatus {
            font-weight: bold;
            margin-top: 15px;
        }

        .warning {
            background: #fff3cd;
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            color: #664d03;
        }

    </style>

</head>

<body>

    <div class="header">

        <h1>🚨 LifeBox</h1>

        <p>
            Emergency Communication Network
        </p>

    </div>


    <div class="container">


        <div class="card">

            <h2>👥 Emergency Contacts</h2>

            <p>
                Add people who should receive your SOS alert.
            </p>

            <div id="contacts"></div>

            <button
                class="add-button"
                onclick="addContact()">
                ➕ Add Emergency Contact
            </button>

            <br><br>

            <button
                class="save-button"
                onclick="saveContacts()">
                💾 Save Emergency Contacts
            </button>

            <p id="contactStatus"></p>

        </div>


        <div class="card">

            <h2>🚨 Emergency SOS</h2>

            <p>
                Use this button only when you need emergency assistance.
            </p>

            <div class="warning">
                ⚠️ Your location will be requested when SOS is activated.
            </div>

            <br>

            <button
                class="sos-button"
                onclick="activateSOS()">
                🚨 SOS - I NEED HELP
            </button>

            <p id="status"></p>

        </div>


        <div class="card">

            <h2>📜 SOS History</h2>

            <p>
                View previous emergency alerts and their locations.
            </p>

            <a
                class="history-button"
                href="/history">
                📜 View SOS History
            </a>

        </div>


    </div>


<script>

let contactCount = 0;


function addContact() {

    if (contactCount >= 5) {

        alert(
            "You can add up to 5 emergency contacts."
        );

        return;
    }

    contactCount++;

    const div =
        document.createElement("div");

    div.className = "contact";

    div.innerHTML = `

        <h4>
            Contact ${contactCount}
        </h4>

        <input
            id="name${contactCount}"
            type="text"
            placeholder="Contact name">

        <br><br>

        <input
            id="phone${contactCount}"
            type="text"
            placeholder="Phone number">

        <br><br>

        <input
            id="email${contactCount}"
            type="email"
            placeholder="Email address">

    `;

    document
        .getElementById("contacts")
        .appendChild(div);
}


window.onload = function() {

    fetch("/contacts")

    .then(response =>
        response.json()
    )

    .then(data => {

        data.contacts.forEach(
            contact => {

                addContact();

                document.getElementById(
                    "name" + contactCount
                ).value =
                    contact.name;

                document.getElementById(
                    "phone" + contactCount
                ).value =
                    contact.phone;

                document.getElementById(
                    "email" + contactCount
                ).value =
                    contact.email;

            }
        );

    });

};


function saveContacts() {

    const contacts = [];

    for (
        let i = 1;
        i <= contactCount;
        i++
    ) {

        const name =
            document.getElementById(
                "name" + i
            ).value;

        const phone =
            document.getElementById(
                "phone" + i
            ).value;

        const email =
            document.getElementById(
                "email" + i
            ).value;

        if (
            name ||
            phone ||
            email
        ) {

            contacts.push({

                name: name,

                phone: phone,

                email: email

            });

        }

    }


    fetch("/contacts", {

        method: "POST",

        headers: {
            "Content-Type":
                "application/json"
        },

        body: JSON.stringify({

            contacts: contacts

        })

    })

    .then(response =>
        response.json()
    )

    .then(data => {

        document.getElementById(
            "contactStatus"
        ).innerText =
            "✅ " + data.message;

    });

}


function activateSOS() {

    let countdown = 5;
    let cancelled = false;

    document.getElementById("status").innerHTML =
        "🚨 <strong>SOS will activate in " +
        countdown +
        " seconds...</strong><br><br>" +
        "<button onclick='cancelSOS()' " +
        "style='background:#555;color:white;padding:14px 24px;border:none;border-radius:8px;font-size:16px;'>" +
        "🛑 CANCEL SOS" +
        "</button>";

    const timer = setInterval(function() {

        countdown--;

        if (countdown > 0) {

            document.getElementById("status").innerHTML =
                "🚨 <strong>SOS will activate in " +
                countdown +
                " seconds...</strong><br><br>" +
                "<button onclick='cancelSOS()' " +
                "style='background:#555;color:white;padding:14px 24px;border:none;border-radius:8px;font-size:16px;'>" +
                "🛑 CANCEL SOS" +
                "</button>";

            return;
        }

        clearInterval(timer);

        if (cancelled) {
            return;
        }

        document.getElementById("status").innerHTML =
            "📍 <strong>Getting your location...</strong>";

        if (!navigator.geolocation) {

            document.getElementById("status").innerText =
                "❌ Location is not supported on this device.";

            return;
        }

        navigator.geolocation.getCurrentPosition(

            function(position) {

                document.getElementById("status").innerHTML =
                    "⏳ <strong>Sending emergency alert...</strong>";

                fetch("/sos", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        latitude:
                            position.coords.latitude,

                        longitude:
                            position.coords.longitude

                    })

                })

                .then(response => response.json())

                .then(data => {

                    let callButton = "";

                    if (
                        data.call_contact &&
                        data.call_contact.phone
                    ) {

                        callButton = `

                            <br><br>

                            <a
                                href="tel:${data.call_contact.phone}"
                                onclick="return confirm('Are you sure you want to call ${data.call_contact.name}?')"
                                style="display:block;text-align:center;background:#1976d2;color:white;padding:16px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:16px;"
                            >

                                📞 CALL ${data.call_contact.name}

                            </a>

                        `;
                    }


                    let emergencyButton = `

                        <br><br>

                        <a
                            href="#"
                            onclick="return callGlobalEmergency()"
                            style="display:block;text-align:center;background:#b71c1c;color:white;padding:16px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:16px;"
                        >

                            🚨 CALL LOCAL EMERGENCY SERVICES

                        </a>

                    `;


                    document.getElementById("status").innerHTML =

                        "<div style='background:#fff3f3;padding:18px;border-radius:12px;border:2px solid #d32f2f;'>" +

                        "<h2 style='color:#d32f2f;margin-top:0;'>" +
                        "🚨 SOS ACTIVATED" +
                        "</h2>" +

                        "<p><strong>Help alert sent successfully.</strong></p>" +

                        "<p>" +
                        "🕐 <strong>Time:</strong><br>" +
                        data.time +
                        "</p>" +

                        "<p>" +
                        "📍 <strong>Your emergency location:</strong>" +
                        "</p>" +

                        "<a " +
                        "href='https://www.google.com/maps?q=" +
                        data.latitude +
                        "," +
                        data.longitude +
                        "' " +
                        "target='_blank' " +
                        "style='display:block;text-align:center;background:#388e3c;color:white;padding:16px;border-radius:10px;text-decoration:none;font-weight:bold;'>" +

                        "📍 OPEN LOCATION IN GOOGLE MAPS" +

                        "</a>" +

                        "<p style='margin-top:15px;'>" +
                        data.message +
                        "</p>" +

                        callButton +

                        emergencyButton +

                        "</div>";

                });

            },

            function() {

                document.getElementById("status").innerHTML =
                    "❌ <strong>Location permission was not granted.</strong><br><br>" +
                    "LifeBox could not send your location.";

            }

        );

    }, 1000);


    window.cancelSOS = function() {

        cancelled = true;

        clearInterval(timer);

        document.getElementById("status").innerHTML =
            "🛑 <strong>SOS cancelled.</strong>";

    };

}

</script>

</body>

</html>
"""


@app.route("/history", methods=["GET"])
def history():
    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>LifeBox SOS History</title>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                margin: 0;
                padding: 20px;
            }

            h1 {
                text-align: center;
                color: #d32f2f;
            }

            .record {
                background: white;
                padding: 20px;
                margin: 15px auto;
                max-width: 600px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }

            .record h3 {
                color: #d32f2f;
                margin-top: 0;
            }

            .map-button {
                display: inline-block;
                margin-top: 15px;
                padding: 10px 15px;
                background: #1976d2;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }

            .clear-button {
                display: block;
                margin: 20px auto;
                padding: 12px 20px;
                background: #d32f2f;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }

            .back-button {
                display: block;
                width: fit-content;
                margin: 20px auto;
                padding: 12px 20px;
                background: #555;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            }

        </style>
    </head>

    <body>

        <h1>🚨 LifeBox SOS History</h1>

        <div id="history">
            Loading SOS history...
        </div>

        <button class="clear-button"
                onclick="clearHistory()">
            🗑️ Clear SOS History
        </button>

        <a class="back-button" href="/">
            ← Back to LifeBox
        </a>

        <script>

            function clearHistory() {

                if (!confirm(
                    "Are you sure you want to clear all SOS history?"
                )) {
                    return;
                }

                fetch("/clear-history", {
                    method: "POST"
                })
                .then(response => response.json())
                .then(data => {

                    alert("✅ " + data.message);

                    location.reload();

                });

            }


            fetch("/history-data")
            .then(response => response.json())
            .then(data => {

                const historyDiv =
                    document.getElementById("history");

                if (!data.records ||
                    data.records.length === 0) {

                    historyDiv.innerHTML =
                        "<div class='record'>" +
                        "No SOS records found." +
                        "</div>";

                    return;
                }

                historyDiv.innerHTML = "";

                data.records.slice().reverse().forEach(record => {

                    const mapLink =
                        "https://maps.google.com/?q=" +
                        record.latitude +
                        "," +
                        record.longitude;

                    const div =
                        document.createElement("div");

                    div.className = "record";

                    div.innerHTML =
                        "<h3>🚨 SOS ACTIVATED</h3>" +

                        "<p><strong>Time:</strong> " +
                        record.time +
                        "</p>" +

                        "<p><strong>Latitude:</strong> " +
                        record.latitude +
                        "</p>" +

                        "<p><strong>Longitude:</strong> " +
                        record.longitude +
                        "</p>" +

                        "<p><strong>Emergency Contact(s):</strong></p>" +

                        "<ul>" +
                        record.contacts.map(function(contact) {

                            return "<li>" +
                                   contact.name +
                                   " — " +
                                   contact.phone +
                                   " — " +
                                   contact.email +
                                   "</li>";

                        }).join("") +
                        "</ul>" +

                        "<a class='map-button' " +
                        "href='" + mapLink +
                        "' target='_blank'>" +
                        "📍 View Location on Google Maps" +
                        "</a>";

                    historyDiv.appendChild(div);

                });

            });

        </script>

    </body>

    </html>
    """

    return jsonify({
        "records": sos_records
    })


@app.route("/clear-history", methods=["POST"])
def clear_history():

    global sos_records

    sos_records = []

    with open(SOS_FILE, "w") as file:
        json.dump(sos_records, file)

    return jsonify({
        "message": "SOS history cleared successfully."
    })


@app.route("/history-data", methods=["GET"])
def history_data():

    return jsonify({
        "records": sos_records
    })
def get_contacts():

    return jsonify({
        "contacts": emergency_contacts
    })


@app.route("/contacts", methods=["GET"])
def get_contacts():

    return jsonify({
        "contacts": emergency_contacts
    })


@app.route("/contacts", methods=["POST"])
def save_contacts():

    global emergency_contacts

    data = request.get_json()

    emergency_contacts = data.get("contacts", [])

    with open(CONTACTS_FILE, "w") as file:
        json.dump(emergency_contacts, file)

    return jsonify({
        "message":
        f"{len(emergency_contacts)} emergency contact(s) saved."
    })


@app.route("/sos", methods=["POST"])
def sos():

    data = request.get_json()

    time_now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    maps_link = (
        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    # BREVO EMAIL

    api_key = os.environ.get("BREVO_API_KEY")

    email_message = ""

    if not api_key:

        email_message = (
            "❌ Brevo API key is not configured."
        )

    else:

        recipients = [
            {
                "email": SENDER_EMAIL,
                "name": "LifeBox Owner"
            }
        ]

        for contact in emergency_contacts:

            email = contact.get(
                "email", ""
            ).strip()

            if email and email.lower() != SENDER_EMAIL.lower():

                recipients.append({
                    "email": email,
                    "name": contact.get(
                        "name",
                        "Emergency Contact"
                    )
                })

        email_data = {

            "sender": {
                "name": SENDER_NAME,
                "email": SENDER_EMAIL
            },

            "to": recipients,

            "subject":
                "🚨 LIFEBOX SOS ALERT - I NEED HELP",

            "htmlContent": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">

                <h2 style="color:#d32f2f;">
                    🚨 LIFEBOX SOS ALERT
                </h2>

                <h3>
                    I NEED HELP.
                </h3>

                <p>
                    An emergency SOS alert has been activated through LifeBox.
                </p>

                <hr>

                <p>
                    <strong>🕐 Time:</strong><br>
                    {time_now}
                </p>

                <p>
                    <strong>📍 Latitude:</strong><br>
                    {latitude}
                </p>

                <p>
                    <strong>📍 Longitude:</strong><br>
                    {longitude}
                </p>

                <p>
                    <a href="{maps_link}">
                        📍 OPEN EMERGENCY LOCATION IN GOOGLE MAPS
                    </a>
                </p>

                <hr>

                <p>
                    <strong>⚠️ Action required:</strong><br>
                    Please contact the person who activated this SOS
                    and seek appropriate emergency assistance.
                </p>

                <p style="color:#666;font-size:13px;">
                    This alert was sent automatically by LifeBox.
                </p>

            </div>
            """
        }

        try:

            response = requests.post(
                BREVO_API_URL,

                headers={
                    "accept": "application/json",
                    "api-key": api_key,
                    "content-type": "application/json"
                },

                json=email_data,

                timeout=20
            )

            if response.status_code in [200, 201, 202]:

                email_message = (
                    "✅ SOS email sent successfully "
                    "through Brevo."
                )

            else:

                email_message = (
                    f"❌ Brevo email failed. "
                    f"Status: {response.status_code}<br>"
                    f"Details: {response.text}"
                )

        except Exception as e:

            email_message = (
                f"❌ Email error: {str(e)}"
            )


    # ROBASE SMS

    sms_results = []

    sms_message = (
        "LIFEBOX SOS ALERT\n"
        "I NEED HELP.\n"
        f"Time: {time_now}\n"
        f"Location: {maps_link}"
    )

    for contact in emergency_contacts:

        phone = contact.get(
            "phone", ""
        ).strip()

        if phone:

            success, result = send_sms_alert(
                phone,
                sms_message
            )

            if success:

                sms_results.append(
                    f"✅ SMS request accepted by Robase for {phone}"
                )

            else:

                sms_results.append(
                    f"❌ SMS failed for {phone}: {result}"
                )


    # SAVE SOS RECORD

    record = {

        "time": time_now,

        "latitude": latitude,

        "longitude": longitude,

        "status": "SOS ACTIVATED",

        "contacts": emergency_contacts
    }

    sos_records.append(record)

    with open(SOS_FILE, "w") as file:
        json.dump(sos_records, file)


    # EMERGENCY CALL CONTACT

    call_contact = None

    for contact in emergency_contacts:

        phone = contact.get(
            "phone", ""
        ).strip()

        if phone:

            call_contact = {
                "name": contact.get(
                    "name",
                    "Emergency Contact"
                ),
                "phone": phone
            }

            break


    # FINAL RESPONSE

    final_message = email_message

    if sms_results:

        final_message += (
            "<br><br>"
            + "<br>".join(sms_results)
        )

    else:

        final_message += (
            "<br><br>"
            "ℹ️ No emergency phone numbers "
            "were available for SMS."
        )

    return jsonify({

        "time": time_now,

        "latitude": latitude,

        "longitude": longitude,

        "contact_count":
            len(emergency_contacts),

        "call_contact":
            call_contact,

        "message":
            final_message
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )