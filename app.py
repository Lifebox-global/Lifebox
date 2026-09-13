from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

sos_records = []

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LifeBox</title>
    </head>
    <body>
        <h1>🚨 LifeBox</h1>
        <h2>Emergency Network</h2>
        <p>Your emergency communication system.</p>

        <button onclick="activateSOS()">SOS - I NEED HELP</button>

        <p id="status"></p>

        <script>
        function activateSOS() {
            document.getElementById("status").innerText =
                "Getting your location...";

            if (!navigator.geolocation) {
                document.getElementById("status").innerText =
                    "Location is not supported.";
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    fetch("/sos", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById("status").innerHTML =
                            "🚨 SOS ACTIVATED<br>" +
                            "Your emergency information has been saved.<br>" +
                            "Time: " + data.time + "<br>" +
                            "Latitude: " + data.latitude + "<br>" +
                            "Longitude: " + data.longitude;
                    });
                },
                function() {
                    document.getElementById("status").innerText =
                        "Location permission was not granted.";
                }
            );
        }
        </script>
    </body>
    </html>
    """

@app.route("/sos", methods=["POST"])
def sos():
    data = request.get_json()

    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "status": "SOS ACTIVATED"
    }

    sos_records.append(record)

    return jsonify(record)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)