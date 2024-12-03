from django.views.decorators.csrf import csrf_exempt
import os
import threading
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .utils import run_tool, send_email_with_attachment
from fpdf import FPDF
from datetime import datetime

# Directory to store reports
REPORT_DIR = "scanner/reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

@csrf_exempt
def scan_view(request):
    """Endpoint to initiate a scan."""
    url = request.GET.get("url")
    email = request.GET.get("email")

    if not url or not email:
        return JsonResponse({"error": "Missing URL or email parameter."}, status=400)

    # Acknowledge the request immediately
    response = JsonResponse({"message": "Scan started. You will receive the report via email once completed."}, status=200)

    # Run the scan and email process in the background
    thread = threading.Thread(target=background_scan, args=(url, email))
    thread.start()

    return response

@csrf_exempt
def background_scan(url, email):
    """Run the scanning process and send the email in the background."""
    tools = {
        "nmap": ["nmap", "-Pn", "-A", url],
        "sslscan": ["sslscan", url],
        "dig": ["dig", url],
    }

    # Run all tools
    scan_results = {}
    for tool_name, command in tools.items():
        tool_result = run_tool(command, tool_name, url)
        scan_results[tool_name] = tool_result[1]  # Output of the tool

    # Generate a new PDF report
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    pdf_path = os.path.join(REPORT_DIR, f"{url.replace('.', '_')}_{timestamp}_report.pdf")
    generate_pdf_report(scan_results, pdf_path)

    # Send the report via email
    send_email_with_attachment(
        email,
        subject="Your Scan Report by SOIT Students",
        body="Please find the attached scan report, make sure to go though it and please check if email is from real source only, Thanks team Nerd",
        pdf_file_path=pdf_path,
    )

@csrf_exempt
def generate_pdf_report(scan_results, pdf_path):
    """Generate a PDF report from the scan results."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Scan Report", ln=True, align="C")
    pdf.ln(10)  # Line break

    for tool_name, output in scan_results.items():
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt=f"{tool_name.upper()} Results:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=output)
        pdf.ln(10)

    # Save the PDF to the specified path
    pdf.output(pdf_path)

@csrf_exempt
def get_report_view(request):
    """Endpoint to retrieve the latest report for a specific URL."""
    url = request.GET.get("url")

    if not url:
        return JsonResponse({"error": "Missing URL parameter."}, status=400)

    # Get the most recent report for the URL
    report_files = [
        f for f in os.listdir(REPORT_DIR)
        if f.startswith(url.replace('.', '_')) and f.endswith('_report.pdf')
    ]
    report_files.sort(reverse=True)  # Sort to get the latest report

    if report_files:
        latest_report = report_files[0]
        report_path = os.path.join(REPORT_DIR, latest_report)

        with open(report_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            response["Content-Disposition"] = f"inline; filename={latest_report}"
            return response
    else:
        return JsonResponse({"error": "Report not found for the given URL."}, status=404)

