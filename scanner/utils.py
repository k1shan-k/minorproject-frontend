import subprocess
from django.core.mail import EmailMessage
import os

def run_tool(command, tool_name, target_url):
    """
    Executes a command-line tool and captures its output.

    Args:
        command (list): The command to run as a list of arguments.
        tool_name (str): The name of the tool being run.
        target_url (str): The URL being scanned.

    Returns:
        tuple: (exit_code, output) - Exit code and the output of the tool.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        save_tool_output(tool_name, target_url, output)
        return 0, output
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stderr

def save_tool_output(tool_name, target_url, output):
    """
    Save the output of a tool into a text file.

    Args:
        tool_name (str): The name of the tool.
        target_url (str): The URL being scanned.
        output (str): The output of the tool.
    """
    output_dir = "scanner/tool_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, f"{tool_name}_{target_url.replace('.', '_')}.txt")
    with open(file_path, "w") as f:
        f.write(output)

def send_email_with_attachment(to_email, subject, body, pdf_file_path):
    """
    Sends an email with a PDF attachment.

    Args:
        to_email (str): The recipient's email address.
        subject (str): Subject of the email.
        body (str): Body of the email.
        pdf_file_path (str): Path to the PDF attachment.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        # Create the email
        email = EmailMessage(
            subject=subject,
            body=body,
            to=[to_email],
        )

        # Attach the PDF report
        with open(pdf_file_path, "rb") as f:
            email.attach(os.path.basename(pdf_file_path), f.read(), "application/pdf")

        # Send the email
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

