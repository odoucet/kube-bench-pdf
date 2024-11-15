import json
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Kube-Bench Report", 0, 1, "C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_summary_table(self, summary_data):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Summary", 0, 1, "L")
        self.ln(10)
        
        for item in summary_data:
            status_color = (0, 255, 0) if item['status'] == 'PASS' else (255, 0, 0) if item['status'] == 'FAIL' else (255, 255, 0)
            self.set_fill_color(*status_color)
            self.cell(20, 10, item['status'], 1, 0, 'C', fill=True)
            self.cell(20, 10, item['test_number'], 1)
            self.multi_cell(0, 5, item['test_desc'], 1)
            self.ln()

    def add_test_result(self, test):
        # Set colors based on status
        status_color = (0, 255, 0) if test.get("status") == "PASS" else (255, 0, 0) if test.get("status") == "FAIL" else (255, 255, 0)
        
        # Header table for each test
        self.set_font("Arial", "B", 10)
        self.set_fill_color(*status_color)
        self.cell(20, 10, test.get("status", "UNKNOWN"), 0, 0, "C", fill=True)
        self.cell(10, 10, test.get("test_number", "N/A"), 0)
        txt = test.get("test_desc", "No description provided").replace("(Automated)", "").strip()
        if len(txt) > 95:
            cell_height = 5
        else:
            cell_height = 10
        self.multi_cell(0, cell_height, txt, 0)
        self.ln(5)
        
        # Details table below the header
        self.set_font("Arial", "", 9)
        self.set_fill_color(240, 240, 240)  # Fond grisé pour le cadre
        self.cell(30, 10, "Audit:", 0)
        self.set_font("Courier", "", 9)  # Police à largeur fixe
        self.multi_cell(0, 5, test.get("audit", "No audit provided"), 0, fill=True)
        self.set_font("Arial", "", 9)

        self.cell(30, 10, "Expected Result:", 0)
        self.multi_cell(0, 10, test.get("expected_result", "No expected result"), 0)


        if test.get("status") != "PASS":
            self.cell(30, 10, "Actual Value:", 0)
            self.set_font("Courier", "", 9)  # Police à largeur fixe
            self.multi_cell(0, 5, test.get("actual_value", "No actual value provided"), 0, fill=True)
            self.set_font("Arial", "", 9)

            self.cell(30, 10, "Remediation:", 0)
            self.multi_cell(0, 5, test.get("remediation", "No remediation provided"), 0)
        
        self.ln(5)

def convert_kube_bench_json_to_pdf(json_file, pdf_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    pdf = PDF()
    pdf.add_page()
    
    summary_data = []

    pages = []

    # Add Totals scores
    if "Totals" in data:
        pdf.chapter_title("Totals")

        passes = data['Totals'].get('total_pass')
        fail = data['Totals'].get('total_fail')
        warn = data['Totals'].get('total_warn')
        info = data['Totals'].get('total_info')

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Pass: {passes} - Fail: {fail} - Warn: {warn} - Info: {info}", 0, 1, "L")


        
        pdf.ln(5)
    
    # Gather summary data and add individual test details
    if "Controls" in data:
        for control in data["Controls"]:
            if "tests" in control:
                for test_group in control["tests"]:
                    for test in test_group["results"]:
                        # Collect data for summary
                        summary_data.append({
                            "status": test.get("status", "UNKNOWN"),
                            "test_number": test.get("test_number", "N/A"),
                            "test_desc": test.get("test_desc", "No description provided")
                        })
                        
                        # Add detailed test result
                        pages.append(test)
    
    # Add summary page
    pdf.add_summary_table(summary_data)
    pdf.add_page()
    # add all pages
    for page in pages:
        pdf.add_test_result(page)
    

    pdf.output(pdf_file)
    print(f"PDF report created successfully at {pdf_file}")

# check argv1 and argv2 are defined
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python kube-bench-pdf.py <kube-bench-json-file> <output-pdf-file>")
        sys.exit(1)

    # make sure source file exists
    try:
        with open(sys.argv[1], 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: File {sys.argv[1]} not found.")

    convert_kube_bench_json_to_pdf(sys.argv[1], sys.argv[2])