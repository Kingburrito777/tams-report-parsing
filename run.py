import os
import gzip
from report_parser import ReportParser
import json

all_reports_dir = 'reports/'

def decompress_file(file_path):
    decompressed_path = file_path.rstrip('.z')
    with gzip.open(file_path, 'rb') as f_in:
        with open(decompressed_path, 'wb') as f_out:
            f_out.write(f_in.read())
    return decompressed_path

report_dirs = sorted(os.listdir(all_reports_dir))
report_parser = ReportParser()

report_data = {}
char_count = {}

report_types = {
    "RPT001":"RPT001",
    "RPT002":"RPT002",
    "RPT003":"RPT003",
    "RPT004":"RPT004",
    "RPT083":"RPT083"
}

for dir in report_dirs:
    dir_path = os.path.join(all_reports_dir, dir)
    for file in os.listdir(dir_path):
        report_type = file.split('_')[0]
        report_type = report_types.get(report_type, None)
        if not file.startswith('RPT') or report_type is None:
            continue

        real_date = file.split('_')[1].split('.')[0][:8]
        if real_date not in report_data:
            report_data[real_date] = {}

        file_path = os.path.join(dir_path, file)
        if file.endswith('.PF') or file.endswith('.z'):
            if file.endswith('.z'):
                file_path = decompress_file(file_path)
            with open(file_path, 'rb') as f:
                strdata = f.read().decode('utf-8')
                report_parser.parse_report(report_type.strip('RPT'), strdata)
                report_data[real_date][report_type] = report_parser.report_data

with open('dump.json', 'w') as file:
    json.dump(report_data, file, indent=2)

"""
EXAMPLE STRUCTURE
├── 20140512
│   ├── COM050_20140514181303.pdf
│   ├── COM060_20140514183634.pdf
│   ├── COM070_20140514183641.PF.z
│   ├── COM150_20140515002052.PF.z
│   ├── COMLOG.PF
│   ├── EODLOG.PF
│   ├── ISLOG.PF
│   ├── ISLOG.PF.z
│   ├── JOEILOG.PF
│   ├── JOEILOG.PF.z
│   ├── PO_FINAL_20140514143716.PF.z
│   ├── PO_FINAL_20140514143741.PF.z
│   ├── PO_FINAL_20140514144500.PF.z
│   ├── PO_FINAL_20140514144536.PF.z
│   ├── PO_FINAL_20140514145155.PF.z
│   ├── PO_FINAL_20140514145220.PF.z
│   ├── PO_FINAL_20140514175208.PF.z
│   ├── PO_FINAL_20140514175232.PF.z
│   ├── RPT001_20140514181224.PF.z
│   ├── RPT002_20140514181224.PF.z
│   ├── RPT003_20140514181224.PF.z
│   ├── RPT004_20140514181225.PF.z
│   ├── RPT005_20140514181225.PF.z
│   ├── RPT006_20140514181258.PF.z
│   ├── RPT007_20140514182540.pdf
│   ├── RPT008_20140514182541.PF.z
│   ├── RPT009_20140514182542.PF.z
│   ├── RPT012_20140514182540.PF.z
│   ├── RPT013_20140515040000.PF.z
│   ├── RPT015_20140514182550.PF.z
│   ├── RPT017_20140514182540.PF.z
│   ├── RPT076_20140514182542.PF.z
│   ├── RPT077_20140514182540.PF.z
│   ├── RPT078_20140514182541.PF.z
│   ├── RPT079_20140514182541.PF.z
│   ├── RPT080_20140514182541.PF.z
│   ├── RPT082_20140514182541.PF.z
│   ├── RPT083_20140514182541.PF.z
│   ├── RPT087_20140514182542.PF.z
│   ├── RPT088_20140514182549.PF.z
│   ├── RPT113_20140514182541.PF.z
│   ├── RPT115_20140514182552.pdf
│   ├── RPT121_20140514182552.PF.z
│   ├── RPT130_20140514182550.PF.z
│   ├── RPT203_20140514182550.PF.z
│   ├── RPT205_20140514082747.PF.z
│   ├── RPT206_20140514082748.PF.z
│   ├── SCR053-OR_20140514104220.PF.z
│   ├── SCR053-OR_20140514123517.PF.z
│   ├── SCR053-OR_20140514123557.PF.z
│   ├── SCR053-OR_20140514123713.PF.z
│   ├── SCR053-OR_20140514123739.PF.z
│   ├── SCR053-OR_20140514123802.PF.z
│   ├── SCR054-OR_20140514104221.PF.z
│   ├── SCR054-OR_20140514123517.PF.z
│   ├── SCR054-OR_20140514123557.PF.z
│   ├── SCR054-OR_20140514123713.PF.z
│   ├── SCR054-OR_20140514123739.PF.z
│   ├── SCR054-OR_20140514123802.PF.z
│   └── TRANSIN_LOG.PF

RPT013: 3147 - INVENTORY STATUS (ON ORDER/BACKORDER, DATE LAST SALE/RECIEVED)
RPT203: 3163 - TRANSFERS INVOICED (INTERSTORE)
RPT006: 3167 - SALES BY DEPARTEMNT (AUTOMOTIVE, LAWN & GARDEN, ETC)
RPT121: 3167 - RETURN DEFECTIVE / LABOR CLAIM BY CUSTOMER
RPT079: 3167 - CHECKS
RPT005: 3167 - SALES POSTED (DAY SALES INFO)
RPT080: 3167 - PAYMENT CARDS (TRANSACTIONS)
RPT012: 3167 - SAVED INVOICE REPORT (SAVED INVOICES)
RPT113: 3167 - 
RPT130: 3167 - SPECIAL INVOICE REPORT (CORES, NO-CHARGE, WARRANTY, RETURNS) 
RPT077: 3167 - CASH REPORT (CASH, CARD, CHECK BY DRAWER + TOTAL)
RPT078: 3167 - INVENTORY ACTIVITY (ADJUSTMENTS)
RPT008: 3167 - RECIEVED ON ACCOUNT (CASH, CARD, CHECK)
RPT082: 3167 - PRICE OVERRIDES
RPT017: 3167 - DAILY REPORTABLE SALES (LINE: GROUP, CUSTOMER)
RPT015: 3181 - SPECIAL ORDER COMMUNICATION REPORT


################ DONE ##################

RPT083: 3167 - INVETORY EFFECTIVENESS (IN STORE VS WAREHOUSE)
    Store identification information and report metadata
    Counts of in-store and non-store inventory items tracked daily, monthly, and yearly
    Lost sales metrics
    Effectiveness ratings shown as percentages
    Comparative data between current periods and previous year

RPT004: 3167 - SALES JOURNAL
    Store identification and report metadata
    Sales performance metrics comparing current periods to last year (today, month-to-date, year-to-date)
    Main categories: Merchandise Sales, Labor Sales, Net Sales, Miscellaneous, Gross Sales
    Financial metrics within each category: revenue, cost, profit, profit percentage
    Sales tax breakdowns by different tax rates/categories
    Payment method analysis (cash vs charge)
    Taxable vs non-taxable sales breakdown
    Core sales and returns tracking
    Miscellaneous charges (freight, environmental, service)

RPT003: 3168 - TRANSACTION ACTIVITY BY QUARTER HOUR
    Store identification information (ID, name, date)
    Transaction metrics broken down by 15-minute intervals
    Comparison between today's figures and month-to-date totals
    Financial data including cash sales, charge sales, and percentages
    Transaction volume metrics (invoices and line items)
    Sales distribution analysis by time period

RPT002: 3168 - TRANSACTION REGISTER
    Metadata section with report date, store identification, and report type
    Financial performance categories including:
        Merchandise Sales (with subcategories for Cost, Rebates, Total Cost, Profit, and Profit Percent)
        Labor Sales
        Net Sales
        Miscellaneous income
    Each category tracks financial metrics comparing:
        Daily figures (current vs. last year)
        Month-to-date performance
        Year-to-date totals
        Percentage changes across these periods

RPT001: 3199 - EMPLOYEE SALES REPORT
    Report metadata: Date, store identification, report type and pagination
    Individual employee metrics: Performance data for multiple employees
    Sales metrics: Daily, monthly, and yearly sales figures with profit margins
    Invoice details: Transaction counts, returns, and voids across different time periods
    Comparative data: Current performance versus previous periods
    Store totals: Aggregated performance metrics for all employees and sales representatives
    Delivery sales: Separate tracking for delivery-based transactions

reports_dump.json
    20141125
        RPT001
        ...
        RPT083
    20141126
        RPT001
        ...
        RPT083

        .
        ..
        ...
"""
