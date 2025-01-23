import zipfile
from datetime import datetime
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import subprocess
import shutil
import os
from datetime import datetime
from flask_cors import CORS
import uuid
import threading
# Initialize Flask app and Flask-Mail
app = Flask(__name__)
CORS(app)
# Configure email settings
app.config['MAIL_SERVER'] = 'email-smtp.ap-south-1.amazonaws.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'AKYFBS3RB'  # Your email address
app.config['MAIL_PASSWORD'] = 'BBUWzRD114OkTbhOrf25EHy'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'hello@scans.atlassoit.co'

mail = Mail(app)

# Directory for storing reports
OUTPUT_DIR = "sitespeed_reports"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

def process_request(url, email):
    """Background task to process the URL and send the report."""
    # Generate unique folder name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    output_folder = f"{OUTPUT_DIR}/{timestamp}_{unique_id}"
    zip_file = None  # Declare upfront to handle cleanup properly

    try:
        # Run sitespeed.io in Docker
        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(OUTPUT_DIR)}:/sitespeed.io/sitespeed-result",
            "sitespeedio/sitespeed.io",
            url,
            "--output", f"sitespeed-result/{timestamp}_{unique_id}"
        ]
        subprocess.run(docker_command, check=True)

        # Check if output folder exists
        if not os.path.exists(output_folder):
            raise FileNotFoundError(f"Output folder {output_folder} was not created.")

        # Create zip file for the report
        zip_file = f"{output_folder}.zip"
        shutil.make_archive(output_folder, 'zip', output_folder)

        # Send email with the report
        msg = Message("Your Sitespeed.io Report", recipients=[email])
        msg.body = f"Attached is the performance report for {url}."
        with app.open_resource(zip_file) as fp:
            msg.attach(f"report_{timestamp}.zip", "application/zip", fp.read())
        mail.send(msg)

        print(f"Email sent successfully to {email}.")

    except subprocess.CalledProcessError as e:
        print(f"Sitespeed.io failed to run: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Cleanup: Delete the output folder and zip file if they exist
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            print(f"Cleaned up folder: {output_folder}")
        if zip_file and os.path.exists(zip_file):
            os.remove(zip_file)
            print(f"Cleaned up zip file: {zip_file}")


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Parse input JSON
        data = request.get_json()
        url = data.get('url')
        email = data.get('email')

        if not url or not email:
            return jsonify({"error": "Both 'url' and 'email' fields are required."}), 400

        # Start background task
        thread = threading.Thread(target=process_request, args=(url, email))
        thread.start()

        # Return 200 immediately
        return jsonify({"message": "Request received. Report will be emailed shortly."}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
