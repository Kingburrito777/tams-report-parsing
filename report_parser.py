from typing import List, Optional

class ReportParser:
    def __init__(self):
        # Map report numbers to their parser functions
        self.parser_map = {
            "001": parse_RPT001,  # EMPLOYEE SALES REPORT
            "002": parse_RPT002,  # TRANSACTION REGISTER
            "003": parse_RPT003,  # TRANSACTION ACTIVITY BY QUARTER HOUR
            "004": parse_RPT004,  # SALES JOURNAL
            "005": parse_RPT005,  # SALES POSTED (DAY SALES INFO)
            "006": parse_RPT006,  # SALES BY DEPARTMENT
            "008": parse_RPT008,  # RECEIVED ON ACCOUNT
            "012": parse_RPT012,  # SAVED INVOICE REPORT
            "013": parse_RPT013,  # INVENTORY STATUS
            "015": parse_RPT015,  # SPECIAL ORDER COMMUNICATION REPORT
            "017": parse_RPT017,  # DAILY REPORTABLE SALES
            "077": parse_RPT077,  # CASH REPORT
            "078": parse_RPT078,  # INVENTORY ACTIVITY
            "079": parse_RPT079,  # CHECKS
            "080": parse_RPT080,  # PAYMENT CARDS
            "082": parse_RPT082,  # PRICE OVERRIDES
            "083": parse_RPT083,  # INVENTORY EFFECTIVENESS
            "113": parse_RPT113,  # (No description)
            "121": parse_RPT121,  # RETURN DEFECTIVE / LABOR CLAIM
            "130": parse_RPT130,  # SPECIAL INVOICE REPORT
            "203": parse_RPT203,  # TRANSFERS INVOICED
        }
        self.report_data = None

    def parse_report_if_else(self, report_number, raw_data):
        if report_number == "001":
            self.report_data = parse_RPT001(raw_data)  # EMPLOYEE SALES REPORT
        elif report_number == "002":
            self.report_data = parse_RPT002(raw_data)  # TRANSACTION REGISTER
        elif report_number == "003":
            self.report_data = parse_RPT003(raw_data)  # TRANSACTION ACTIVITY BY QUARTER HOUR
        elif report_number == "004":
            self.report_data = parse_RPT004(raw_data)  # SALES JOURNAL
        elif report_number == "005":
            self.report_data = parse_RPT005(raw_data)  # SALES POSTED (DAY SALES INFO)
        elif report_number == "006":
            self.report_data = parse_RPT006(raw_data)  # SALES BY DEPARTMENT
        elif report_number == "008":
            self.report_data = parse_RPT008(raw_data)  # RECEIVED ON ACCOUNT
        elif report_number == "012":
            self.report_data = parse_RPT012(raw_data)  # SAVED INVOICE REPORT
        elif report_number == "013":
            self.report_data = parse_RPT013(raw_data)  # INVENTORY STATUS
        elif report_number == "015":
            self.report_data = parse_RPT015(raw_data)  # SPECIAL ORDER COMMUNICATION REPORT
        elif report_number == "017":
            self.report_data = parse_RPT017(raw_data)  # DAILY REPORTABLE SALES
        elif report_number == "077":
            self.report_data = parse_RPT077(raw_data)  # CASH REPORT
        elif report_number == "078":
            self.report_data = parse_RPT078(raw_data)  # INVENTORY ACTIVITY
        elif report_number == "079":
            self.report_data = parse_RPT079(raw_data)  # CHECKS
        elif report_number == "080":
            self.report_data = parse_RPT080(raw_data)  # PAYMENT CARDS
        elif report_number == "082":
            self.report_data = parse_RPT082(raw_data)  # PRICE OVERRIDES
        elif report_number == "083":
            self.report_data = parse_RPT083(raw_data)  # INVENTORY EFFECTIVENESS
        elif report_number == "113":
            self.report_data = parse_RPT113(raw_data)  # (No description)
        elif report_number == "121":
            self.report_data = parse_RPT121(raw_data)  # RETURN DEFECTIVE / LABOR CLAIM
        elif report_number == "130":
            self.report_data = parse_RPT130(raw_data)  # SPECIAL INVOICE REPORT
        elif report_number == "203":
            self.report_data = parse_RPT203(raw_data)  # TRANSFERS INVOICED
        else:
            raise ValueError(f"Unknown report number: {report_number}")

    def parse_report(self, report_number: str, raw_data: str) -> dict:
        """Parse the raw data for the given report number return JSON valid dict"""
        try:
            # Strip 'RPT' prefix if present
            if report_number.upper().startswith('RPT'):
                report_number = report_number[3:]
            
            self.parse_report_if_else(report_number, raw_data)
        except Exception as e:
            print(f"Error parsing report {report_number}: {str(e)}")
            raise
            

# may need to switch to fixed width parsing if unreliable
def parse_RPT001(raw_data):
    """
    Parse the employee sales report (RPT001) with proper pagination handling
    
    Args:
        raw_data (str): Raw ASCII report data
    
    Returns:
        dict: Parsed data containing report metadata, sales data, and invoice data
    """
    parsed_data = {
        'metadata': {},
        'employees': {},
        'salesreps': {},
        'totals': {
            'employee': {
                'sales': {},
                'invoice': {}
            },
            'salesrep': {
                'sales': {},
                'invoice': {}
            }
        },
        'memo_delivery_sales': {}
    }
    
    # Parse employee sales report
    pages = raw_data.split("\f")
    
    # Track the current section and data type across pages
    current_section = None
    current_data_type = 'sales'  # Start with sales data, will switch to 'invoice' when detected
    
    for page_index, page_data in enumerate(pages):
        current_section = None
        lines = page_data.strip().split('\n')
        
        # Parse metadata from each page header
        if len(lines) > 5:
            # Extract report metadata from first page only
            if page_index == 0 or not parsed_data['metadata']:
                header_date_line = lines[0].split()
                if len(header_date_line) >= 2:
                    parsed_data['metadata']['report_date'] = f"{header_date_line[0]} {header_date_line[1]}"
                
                store_info_line = lines[1].split(' - ')
                if len(store_info_line) >= 2:
                    parsed_data['metadata']['store_id'] = store_info_line[0].strip()
                    parsed_data['metadata']['store_name'] = store_info_line[1].replace('Accounting Day', '').rstrip()
                
                # Extract accounting day
                accounting_info = lines[1].split('Accounting Day - ')
                if len(accounting_info) > 1:
                    parsed_data['metadata']['accounting_day'] = accounting_info[1].split()[0].strip()
                
                parsed_data['metadata']['report_type'] = 'Employee Sales'
                
                # Get month for "Last Month" reference
                last_month_info = None
                for line in lines[0:5]:
                    if 'Last' in line and '-' in line:
                        parts = line.split('Last')
                        if len(parts) > 1:
                            month_parts = parts[1].split('-')
                            if len(month_parts) > 0:
                                last_month_info = month_parts[0].strip()
                
                if last_month_info:
                    parsed_data['metadata']['last_month'] = last_month_info
            
            # Extract page number
            page_info = lines[1].split('Page')
            if len(page_info) > 1:
                current_page = int(page_info[1].strip())
                parsed_data['metadata']['current_page'] = current_page
        
        # Detect if this page contains invoice data or sales data
        for i, line in enumerate(lines):
            if i < 10 and 'InvLinesVdRet' in line.replace(' ', ''):
                current_data_type = 'invoice'
                break
            elif i < 10 and 'NetGrossNet' in line.replace(' ', ''):
                current_data_type = 'sales'
                break
        
        # Scan for section headers on each page
        line_index = 0
        while line_index < len(lines):
            line = lines[line_index]
            
            # Identify section headers - these can appear on any page
            if '*Employee' in line:
                current_section = 'employee'
                line_index += 1
                continue
            elif '*Salesrep' in line:
                current_section = 'salesrep'
                line_index += 1
                continue
            elif 'Memo of Delivery Sales' in line:
                current_section = 'memo_delivery'
                line_index += 1
                continue
            
            # Skip header and separator lines
            if ('-----' in line or 
                line.strip() == '' or 
                'EMPLOYEE SALES REPORT' in line.upper() or
                'End of Report' in line or
                'Page' in line and len(line.strip()) < 10 or
                '***' in line or
                '# Inv' in line):
                line_index += 1
                continue
                
            # Skip column headers based on data type
            if current_data_type == 'sales' and ('Emp' in line and 'Sales' in line or
                                             'Net' in line and 'Gross' in line):
                line_index += 1
                continue
            elif current_data_type == 'invoice' and ('Emp' in line and 'Inv' in line or
                                                 'Lines' in line and 'Vd' in line and 'Ret' in line):
                line_index += 1
                continue
            
            # Process data lines if we're in a valid section
            if current_section and line.strip():
                
                # Process Total lines
                if line.strip().startswith('Total'):
                    parts = line.split()
                    
                    if current_data_type == 'sales' and len(parts) >= 14:
                        # Replace '!!!!!' with None
                        parts = [None if p == '!!!!!!' else p for p in parts]
                        
                        total_data = {
                            'today_net_sales': safe_float(parts[1]),
                            'today_gross_profit': safe_float(parts[2]),
                            'today_gp_percent': safe_float(parts[3]),
                            'mtd_net_sales': safe_float(parts[4]),
                            'mtd_gross_profit': safe_float(parts[5]),
                            'mtd_gp_percent': safe_float(parts[6]),
                            'mtd_percent_change': safe_float(parts[7]),
                            'ytd_net_sales': safe_float(parts[8]),
                            'ytd_gross_profit': safe_float(parts[9]),
                            'ytd_gp_percent': safe_float(parts[10]),
                            'last_year_net_sales': safe_float(parts[11]) if len(parts) > 11 else None,
                            'last_year_gross_profit': safe_float(parts[12]) if len(parts) > 12 else None,
                            'last_year_gp_percent': safe_float(parts[13]) if len(parts) > 13 else None
                        }
                        
                        parsed_data['totals'][current_section]['sales'] = total_data
                    
                    # Handle invoice data totals
                    elif current_data_type == 'invoice' and len(parts) >= 20:
                        total_data = {
                            'today_invoices': safe_int(parts[1]),
                            'today_lines': safe_int(parts[2]),
                            'today_voided': safe_int(parts[3]),
                            'today_returns': safe_int(parts[4]),
                            'today_returns_value': safe_float(parts[5]),
                            'mtd_invoices': safe_int(parts[6]),
                            'mtd_lines': safe_int(parts[7]),
                            'mtd_voided': safe_int(parts[8]),
                            'mtd_returns': safe_int(parts[9]),
                            'mtd_returns_value': safe_float(parts[10]),
                            'ytd_invoices': safe_int(parts[11]),
                            'ytd_lines': safe_int(parts[12]),
                            'ytd_voided': safe_int(parts[13]),
                            'ytd_returns': safe_int(parts[14]),
                            'ytd_returns_value': safe_float(parts[15]),
                            'last_year_invoices': safe_int(parts[16]) if len(parts) > 16 else None,
                            'last_year_lines': safe_int(parts[17]) if len(parts) > 17 else None,
                            'last_year_voided': safe_int(parts[18]) if len(parts) > 18 else None,
                            'last_year_returns': safe_int(parts[19]) if len(parts) > 19 else None,
                            'last_year_returns_value': safe_float(parts[20]) if len(parts) > 20 else None
                        }
                        
                        parsed_data['totals'][current_section]['invoice'] = total_data
                
                # Process memo delivery sales data
                elif current_section == 'memo_delivery':
                    parts = line.split()

                    if len(parts) >= 4:
                        try:
                            # Handle invoice counts for memo delivery
                            if 'Inv Lines' in line:
                                line_index += 1
                                continue
                                
                            memo_data = {}
                            
                            # Handle memo delivery data layout
                            if current_data_type == 'invoice' and len(parts) >= 4:
                                memo_data = {
                                    'today_invoices': safe_int(parts[0]),
                                    'today_lines': safe_int(parts[1]),
                                    'mtd_invoices': safe_int(parts[2]),
                                    'mtd_lines': safe_int(parts[3])
                                }
                            
                            # Handle memo delivery data for sales data (if present)
                            elif current_data_type == 'sales' and len(parts) >= 6:
                                memo_data = {
                                    'today_net_sales': safe_float(parts[0]),
                                    'today_gross_profit': safe_float(parts[1]),
                                    'today_gp_percent': safe_float(parts[2]),
                                    'mtd_net_sales': safe_float(parts[3]),
                                    'mtd_gross_profit': safe_float(parts[4]),
                                    'mtd_gp_percent': safe_float(parts[5])
                                }
                            
                            if memo_data:
                                parsed_data['memo_delivery_sales'].update(memo_data)
                                
                        except (ValueError, IndexError):
                            # Skip malformed memo lines
                            pass
                
                # Process regular data lines (employee or salesrep)
                elif current_section in ['employee', 'salesrep'] and not line.strip().startswith('Total'):
                    try:
                        parts = line.split()
                        id_value = parts[0].strip()
                        
                        # Skip if this doesn't start with a valid ID
                        if not (id_value.isdigit() or id_value.isalnum() and len(id_value) <= 6):
                            line_index += 1
                            continue
                        
                        # Initialize structure if this ID is seen for the first time
                        collection_name = f"{current_section}s"  # 'employees' or 'salesreps'
                        if id_value not in parsed_data[collection_name]:
                            parsed_data[collection_name][id_value] = {
                                'sales': {},
                                'invoice': {}
                            }
                            
                        # Process sales data
                        if current_data_type == 'sales' and len(parts) >= 11:
                            # Replace '!!!!!' with None
                            parts = [None if p == '!!!!!!' else p for p in parts]
                            
                            entry = {
                                'today_net_sales': safe_float(parts[1]),
                                'today_gross_profit': safe_float(parts[2]),
                                'today_gp_percent': safe_float(parts[3]),
                                'mtd_net_sales': safe_float(parts[4]),
                                'mtd_gross_profit': safe_float(parts[5]),
                                'mtd_gp_percent': safe_float(parts[6]),
                                'mtd_percent_change': safe_float(parts[7]),
                                'ytd_net_sales': safe_float(parts[8]),
                                'ytd_gross_profit': safe_float(parts[9]),
                                'ytd_gp_percent': safe_float(parts[10])
                            }
                            
                            # Add last year data if available
                            if len(parts) >= 14:
                                entry.update({
                                    'last_year_net_sales': safe_float(parts[11]),
                                    'last_year_gross_profit': safe_float(parts[12]),
                                    'last_year_gp_percent': safe_float(parts[13])
                                })
                            
                            # Store in the appropriate section
                            parsed_data[collection_name][id_value]['sales'] = entry
                        
                        # Process invoice data
                        elif current_data_type == 'invoice' and len(parts) >= 16:
                            entry = {
                                'today_invoices': safe_int(parts[1]),
                                'today_lines': safe_int(parts[2]),
                                'today_voided': safe_int(parts[3]),
                                'today_returns': safe_int(parts[4]),
                                'today_returns_value': safe_float(parts[5]),
                                'mtd_invoices': safe_int(parts[6]),
                                'mtd_lines': safe_int(parts[7]),
                                'mtd_voided': safe_int(parts[8]),
                                'mtd_returns': safe_int(parts[9]),
                                'mtd_returns_value': safe_float(parts[10]),
                                'ytd_invoices': safe_int(parts[11]),
                                'ytd_lines': safe_int(parts[12]),
                                'ytd_voided': safe_int(parts[13]),
                                'ytd_returns': safe_int(parts[14]),
                                'ytd_returns_value': safe_float(parts[15])
                            }
                            
                            # Add last year data if available
                            if len(parts) >= 21:
                                entry.update({
                                    'last_year_invoices': safe_int(parts[16]),
                                    'last_year_lines': safe_int(parts[17]),
                                    'last_year_voided': safe_int(parts[18]),
                                    'last_year_returns': safe_int(parts[19]),
                                    'last_year_returns_value': safe_float(parts[20])
                                })
                            
                            # Store in the appropriate section
                            parsed_data[collection_name][id_value]['invoice'] = entry
                            
                    except (ValueError, IndexError) as e:
                        # Skip any malformed lines but continue processing
                        pass
                        
            line_index += 1
    
    return parsed_data


def safe_float(value):
    """Safely convert a value to float, handling None and exceptions"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value):
    """Safely convert a value to int, handling None and exceptions"""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def detect_data_type(line):
    """
    Detects whether a line is from sales or invoice data
    
    Args:
        line (str): A line from the report
    
    Returns:
        str: 'sales' or 'invoice' or None if can't determine
    """
    # Check for invoice data headers
    if ('Inv' in line and 'Lines' in line and 'Vd' in line and 'Ret' in line and 'Returns' in line):
        return 'invoice'
    
    # Check for sales data headers
    elif ('Net' in line and 'Gross' in line and 'GP%' in line):
        return 'sales'
    
    # Check data content patterns
    elif line.strip() and line[0].isdigit():
        parts = line.split()
        # Invoice data typically has more columns and specific numeric patterns
        if len(parts) >= 16:
            # Check if columns 1-4 look like integers (invoice counts)
            try:
                all(isinstance(int(parts[i]), int) for i in range(1, 5))
                return 'invoice'
            except ValueError:
                pass
                
        # Sales data typically has percentage values
        if len(parts) >= 10:
            try:
                # Check for percentage patterns
                if any(float(part) <= 100.0 for part in [parts[3], parts[6], parts[10]]):
                    return 'sales'
            except ValueError:
                pass
    
    return None

# @ReportParser.register_parser("002")
def parse_RPT002(raw_data):
    """
    Parse the Transaction Register report (RPT002)
    
    Args:
        raw_data (str): Raw ASCII report data
    
    Returns:
        dict: Parsed data containing report metadata and transaction details
    """
    parsed_data = {
        'metadata': {},
        'transactions': [],
        'summary': {
            'sales_totals': {},
            'rebates': {},
            'codes_legend': {},
            'transaction_counts': {}
        }
    }
    
    # Parse transaction register report
    pages = raw_data.split("\f")

    # page delimiter at EOF
    if pages[-1] == '':
        pages.remove(pages[-1])
    
    for page_index, page_data in enumerate(pages):
        lines = page_data.strip().split('\n')
        
        # Parse metadata (from first page)
        if page_index == 0 and len(lines) > 3:
            # Extract report date/time
            header_parts = lines[0].split()
            if len(header_parts) >= 2:
                parsed_data['metadata']['report_date'] = f"{header_parts[0]} {header_parts[1]}"
            
            # Extract store information
            store_info = lines[1].split(' - ')
            if len(store_info) >= 2:
                parsed_data['metadata']['store_id'] = store_info[0].strip()
                parsed_data['metadata']['store_name'] = store_info[1].replace('Accounting Day', '').rstrip()
            
            # Extract accounting day
            accounting_info = lines[1].split('Accounting Day - ')
            if len(accounting_info) > 1:
                parsed_data['metadata']['accounting_day'] = accounting_info[1].split()[0].strip()
                
            parsed_data['metadata']['report_type'] = 'Transaction Register'
        
        # Process transaction data lines
        for line in lines:
            if '-----MEMO-----' in line:
                break
            # Skip header, footer and separator lines
            if (not line.strip() or 
                '-----' in line or 
                'Page' in line or 
                'TRANSACTION REGISTER' in line.upper() or
                'End of Report' in line or
                'Inv #' in line):
                continue
                
            # Identify transaction data lines - typically start with transaction type
            transaction_types = ['CASH', 'CHG', 'CR MEM', 'ROA', 'REFUND']
            if any(line.strip().startswith(t) for t in transaction_types):
                try:
                    # Parse the line based on fixed column positions
                    # The data appears to be in a fixed-width format
                    transaction = parse_transaction_line(line)
                    if transaction:
                        parsed_data['transactions'].append(transaction)
                except Exception as e:
                    # Skip malformed lines but continue processing
                    continue

    # Parse memo section from the last page
    last_page = pages[-1] if pages else ""
    parse_memo_section(last_page, parsed_data)
    
    return parsed_data


def parse_transaction_line(line):
    """
    Parse a single transaction line from the RPT002 report using fixed-width positions
    
    Args:
        line (str): A transaction line from the report
        
    Returns:
        dict: Parsed transaction data
    """
    # Ensure line has minimum length
    if len(line) < 75:  # At least up to transaction_total position
        return None
    
    # Pad the line if it's shorter than we need to avoid index errors
    if len(line) < 130:
        line = line.ljust(130)
    
    # Extract fields using fixed positions
    try:
        # Fixed-width field extraction based on provided indexes
        transaction_type = line[0:8].strip()
        inv_number = line[8:15].strip()
        customer = line[15:24].strip()
        employee = line[24:31].strip()
        salesrep = line[31:39].strip()
        cashier = line[39:47].strip()
        purchase_order = line[47:75].strip()
        
        # Financial fields - need careful handling for potential empties
        transaction_total_str = line[75:87].strip()
        net_sales_str = line[87:97].strip()
        cose_str = line[97:107].strip()
        gross_profit_amount_str = line[107:117].strip()
        gross_profit_percent_str = line[117:125].strip()
        
        # Get codes from the remainder of the line
        codes = line[125:].strip() if len(line) > 125 else None
        
        # Convert financial data to appropriate types
        transaction_total = safe_float(transaction_total_str)
        net_sales = safe_float(net_sales_str)
        cost = safe_float(cose_str)
        gross_profit_amount = safe_float(gross_profit_amount_str)
        gross_profit_percent = safe_float(gross_profit_percent_str)
        
        # Special handling for CR MEM (credit memo) - ensure negative values
        if transaction_type == 'CR MEM':
            if transaction_total and not str(transaction_total).startswith('-'):
                transaction_total = -abs(transaction_total)
            if net_sales and not str(net_sales).startswith('-'):
                net_sales = -abs(net_sales)
            if cost and not str(cost).startswith('-'):
                cost = -abs(cost)
            if gross_profit_amount and not str(gross_profit_amount_str).startswith('-'):
                # Don't force negative if it was intentionally positive
                # (sometimes CR MEMs can have positive profit amounts)
                if gross_profit_amount_str:
                    gross_profit_amount = -abs(gross_profit_amount)
        
        # Create the transaction dictionary
        transaction = {
            'transaction_type': transaction_type,
            'inv_number': inv_number,
            'customer': customer,
            'employee': employee,
            'salesrep': salesrep,
            'cashier': cashier,
            'purchase_order': purchase_order,
            'transaction_total': transaction_total,
            'net_sales': net_sales,
            'cost': cost,
            'gross_profit_amount': gross_profit_amount,
            'gross_profit_percent': gross_profit_percent,
            'codes': codes
        }

        for entry in transaction:
            if transaction[entry] == '':
                transaction[entry] = None
        
        return transaction
        
    except Exception as e:
        # Return None for any parsing issues
        return None
    
def parse_memo_section(page_data, parsed_data):
    """
    Parse the memo section that appears on the last page of RPT002 reports
    
    Args:
        page_data (str): The last page content
        parsed_data (dict): The data structure to update with memo information
    """
    lines = page_data.strip().split('\n')
    
    # Find the memo section marker
    memo_index = -1
    for i, line in enumerate(lines):
        if '-----MEMO-----' in line:
            memo_index = i
            break
    
    if memo_index == -1:
        return  # No memo section found
    
    # Process the lines after the memo marker
    current_section = None
    
    for i in range(memo_index + 1, len(lines)):
        line = lines[i].strip()

        # Skip empty lines and separator lines
        if not line or '------' in line or '***' in line:
            continue
        
        # Process content
        if not ('#' in line and 'Transactions' in line):
            line = lines[i]
            # sales_total_section
            sales_parts = line[:45].split()
            if len(sales_parts) == 2:
                type = sales_parts[0]
                amount = safe_float(sales_parts[1])
                parsed_data['summary']['sales_totals'][type] = amount
            elif len(sales_parts) == 3:
                type = sales_parts[0] + ' ' + sales_parts[1]
                amount = safe_float(sales_parts[2])
                parsed_data['summary']['sales_totals'][type] = amount

            # rebates_section
            rebates_parts = line[48:82].split()
            if len(rebates_parts) == 2:
                type = rebates_parts[0]
                amount = safe_float(rebates_parts[1])
                parsed_data['summary']['rebates'][type] = amount
            elif len(rebates_parts) == 3:
                type = rebates_parts[0] + ' ' + rebates_parts[1]
                amount = safe_float(rebates_parts[2])
                parsed_data['summary']['rebates'][type] = amount
            elif len(rebates_parts) == 4:
                type = rebates_parts[0] + ' ' + rebates_parts[1] + ' ' + rebates_parts[2]
                amount = safe_float(rebates_parts[3])
                parsed_data['summary']['rebates'][type] = amount

            # codes_legend_section
            parts = line[85:].split(' = ')
            if len(parts) == 2:
                    code = parts[0].strip()
                    description = parts[1].strip()
                    parsed_data['summary']['codes_legend'][code] = description

        # Handle transaction counts section (part of sales totals)
        if 'of ' in line and 'Transaction' in line:
            try:
                parts = line.split('of')
                if len(parts) == 2 and 'Transaction' in parts[1]:
                    count_type = parts[1].split('Transaction')[0].strip().lower() + '_transactions'
                    count_value = int(line.split()[-1]) if line.split()[-1].isdigit() else 0
                    parsed_data['summary']['transaction_counts'][count_type] = count_value
            except (ValueError, IndexError):
                pass
        
        # Handle total transaction count
        elif 'Total Transaction Count' in line:
            try:
                total_count = int(line.split()[-1]) if line.split()[-1].isdigit() else 0
                parsed_data['summary']['transaction_counts']['total'] = total_count
            except (ValueError, IndexError):
                pass
        
        # elif current_section == 'codes_legend':
        #     if ' = ' in line:
        #         parts = line.split(' = ', 1)
        #         if len(parts) == 2:
        #             code = parts[0].strip()
        #             description = parts[1].strip()
        #             parsed_data['summary']['codes_legend'][code] = description

# @ReportParser.register_parser("003")
def parse_RPT003(raw_data):
    """
    Parse the Transaction Activity by Quarter Hour report (RPT003)
    
    Args:
        raw_data (str): Raw ASCII report data
    
    Returns:
        dict: Parsed data containing report metadata and transaction activity by time
    """
    parsed_data = {
        'metadata': {},
        'time_periods': {},
        'totals': {
            'today': {},
            'mtd': {}
        }
    }
    
    # Parse report pages
    pages = raw_data.split("\f")
    
    for page_index, page_data in enumerate(pages):
        lines = page_data.strip().split('\n')
        
        # Parse metadata (from first page)
        if page_index == 0 and len(lines) > 3:
            # Extract report date/time
            header_parts = lines[0].split()
            if len(header_parts) >= 2:
                parsed_data['metadata']['report_date'] = f"{header_parts[0]} {header_parts[1]}"
            
            # Extract store information
            store_info = lines[1].split(' - ')
            if len(store_info) >= 2:
                parsed_data['metadata']['store_id'] = store_info[0].strip()
                parsed_data['metadata']['store_name'] = store_info[1].replace('Accounting Day', '').rstrip()
            
            # Extract accounting day
            accounting_info = lines[1].split('Accounting Day - ')
            if len(accounting_info) > 1:
                parsed_data['metadata']['accounting_day'] = accounting_info[1].split()[0].strip()
                
            parsed_data['metadata']['report_type'] = 'Transaction by Quarter Hour'
        
        # Find the data section
        data_start_line = None
        for i, line in enumerate(lines):
            if '---------' in line and 'Time' in lines[i-1]:
                data_start_line = i + 1
                break
        
        if data_start_line is None:
            continue  # No data section found on this page
        
        # Process data lines until we hit the totals or end of data
        line_index = data_start_line
        while line_index < len(lines):
            line = lines[line_index]
            
            # Ensure line is padded to required length to avoid index errors
            if len(line) < 120:
                line = line.ljust(120)
            
            # Check if we've reached the totals line
            if 'Total' in line and line.strip().startswith('Total'):
                # Use fixed indexes for total line
                parsed_data['totals']['today'] = {
                    'cash_sales': safe_float(line[10:20].strip()),
                    'charge_sales': safe_float(line[20:30].strip()),
                    'number_of_invoices': safe_int(line[37:44].strip()),
                    'number_of_lines': safe_int(line[44:54].strip())
                }
                
                parsed_data['totals']['mtd'] = {
                    'cash_sales': safe_float(line[67:77].strip()),
                    'charge_sales': safe_float(line[77:87].strip()),
                    'number_of_invoices': safe_int(line[95:102].strip()),
                    'number_of_lines': safe_int(line[102:].strip())
                }
                break
            
            # Skip empty lines or separator lines
            if not line.strip() or '---' in line or '*' in line or 'End of Report' in line:
                line_index += 1
                continue
            
            # Extract time using fixed index
            time_period = line[0:9].strip()
            
            # Validate this is a time entry (contains ":" and AM/PM)
            if ':' in time_period and ('AM' in time_period or 'PM' in time_period):
                # Initialize time period entry if not exists
                if time_period not in parsed_data['time_periods']:
                    parsed_data['time_periods'][time_period] = {
                        'today': {},
                        'mtd': {}
                    }
                
                # Extract today's data using fixed column indices
                today_data = {
                    'cash_sales': safe_float(line[10:20].strip()),
                    'charge_sales': safe_float(line[20:30].strip()),
                    'perc_of_sales': safe_float(line[30:37].strip()),
                    'number_of_invoices': safe_int(line[37:44].strip()),
                    'number_of_lines': safe_int(line[44:54].strip()),
                    'perc_of_lines': safe_float(line[54:67].strip())
                }
                
                # Extract MTD data using fixed column indices
                mtd_data = {
                    'cash_sales': safe_float(line[67:77].strip()),
                    'charge_sales': safe_float(line[77:87].strip()),
                    'perc_of_sales': safe_float(line[87:94].strip()),
                    'number_of_invoices': safe_int(line[94:101].strip()),
                    'number_of_lines': safe_int(line[101:111].strip()),
                    'perc_of_lines': safe_float(line[111:].strip())
                }
                
                # Update the data structure
                parsed_data['time_periods'][time_period]['today'] = today_data
                parsed_data['time_periods'][time_period]['mtd'] = mtd_data
            
            line_index += 1
    
    return parsed_data

# @ReportParser.register_parser("004")
def parse_RPT004(raw_data):
    """
    Parse the Sales Journal report (RPT004) using fixed-width columns
    
    Args:
        raw_data (str): Raw ASCII report data
    
    Returns:
        dict: Parsed data containing metadata and sales data by category
    """
    parsed_data = {
        'metadata': {},
        'categories': {},
    }
    
    # Define column indices for data extraction
    columns = {
        'description': (0, 33),
        'today_current': 33,
        'today_last_year': 44,
        'percent_change': 56,
        'mtd_current': 64,
        'mtd_last_year': 75,
        'mtd_percent_change': 87,
        'ytd_current': 95,
        'ytd_last_year': 107,
        'ytd_percent_change': 120
    }
    
    # Split into pages and lines
    pages = raw_data.split("\f")
    
    # Track the current category for hierarchical data organization
    current_category = None
    current_subcategory = None
    
    for page_index, page_data in enumerate(pages):
        lines = page_data.split('\n')
        
        # Extract metadata from the header (first page only)
        if page_index == 0 and len(lines) > 2:
            header_date_line = lines[0].split()
            if len(header_date_line) >= 2:
                parsed_data['metadata']['report_date'] = f"{header_date_line[0]} {header_date_line[1]}"
            
            store_info_line = lines[1].split(' - ')
            if len(store_info_line) >= 2:
                parsed_data['metadata']['store_id'] = store_info_line[0].strip()
                parsed_data['metadata']['store_name'] = store_info_line[1].replace("Accounting Day", "").rstrip()
            
            # Extract accounting day
            accounting_info = lines[1].split('Accounting Day - ')
            if len(accounting_info) > 1:
                parsed_data['metadata']['accounting_day'] = accounting_info[1].split()[0].strip()
            
            parsed_data['metadata']['report_type'] = 'Sales Journal'
        
        # Skip header lines and find where data begins
        data_start = 0
        for i, line in enumerate(lines):
            if 'Today' in line and 'MTD' in line and 'YTD' in line:
                data_start = i + 2  # Skip the header and separator line
                break
        
        # Process data lines
        for line_index in range(data_start, len(lines)):
            current_subcategory = None
            line = lines[line_index]
            
            # Exit when we reach the ending section
            if line.startswith("**"):
                return parsed_data
            
            if '----------- Memo -------------' in line: # memo section header
                continue
            
            # Skip empty lines and separator lines
            if not line.strip() or all(c == '-' for c in line.strip()):
                continue
            
            # Extract the description and determine if it's a category or subcategory
            desc = line[columns['description'][0]:columns['description'][1]].strip()
            if not desc:
                continue
                
            # Determine if this is a main category, subcategory, or data line
            if line.startswith('  ') and not line.startswith('    '):
                # This is a main category (like "Merchandise Sales")
                current_category = desc.strip()
                current_subcategory = None
                
                # Initialize the category in our data structure
                if current_category not in parsed_data['categories']:
                    parsed_data['categories'][current_category] = {
                        'data': {},
                        'subcategories': {}
                    }
            
            elif line.startswith('    '):
                # This is a subcategory (like "Cost" under "Merchandise Sales")
                current_subcategory = desc.strip()
                
                # Initialize the subcategory if needed
                if current_category and current_subcategory:
                    if current_subcategory not in parsed_data['categories'][current_category]['subcategories']:
                        parsed_data['categories'][current_category]['subcategories'][current_subcategory] = {}
            
            # Extract values using fixed column positions
            if current_category:
                data = {}
                
                # Helper function to safely extract and convert values
                def safe_extract_value(index, width=10, convert_func=float):
                    """
                    Safely extract a value from a fixed-width position
                    
                    Args:
                        index (int): Starting column index
                        width (int): Width of the column to extract
                        convert_func (callable): Function to convert the extracted string
                        
                    Returns:
                        The converted value or None if extraction/conversion fails
                    """
                    if index >= len(line):
                        return None
                        
                    # Extract the substring at the specified position with the given width
                    # This is more reliable than splitting for fixed-width formats
                    value_str = line[index:index+width].strip() if index < len(line) else ""
                    
                    # Handle special cases and empty values
                    if not value_str or value_str == '******' or value_str == '!!!!!!' or value_str == '-':
                        return None
                        
                    clean_value = value_str.replace(',', '')
                    
                    try:
                        return convert_func(clean_value)
                    except (ValueError, TypeError):
                        return None
                
                # Define column widths based on the report format
                col_widths = {
                    'today_current': 11,
                    'today_last_year': 11, 
                    'percent_change': 7,
                    'mtd_current': 10,
                    'mtd_last_year': 11,
                    'mtd_percent_change': 7,
                    'ytd_current': 12,
                    'ytd_last_year': 12,
                    'ytd_percent_change': 8
                }
                
                # Extract all values from their fixed positions using appropriate widths
                data = {}
                has_data = False
                
                for field, index in [
                    ('today_current', columns['today_current']),
                    ('today_last_year', columns['today_last_year']),
                    ('percent_change', columns['percent_change']),
                    ('mtd_current', columns['mtd_current']),
                    ('mtd_last_year', columns['mtd_last_year']),
                    ('mtd_percent_change', columns['mtd_percent_change']),
                    ('ytd_current', columns['ytd_current']),
                    ('ytd_last_year', columns['ytd_last_year']),
                    ('ytd_percent_change', columns['ytd_percent_change'])
                ]:
                    value = safe_extract_value(index, col_widths.get(field, 10))
                    data[field] = value
                    if value is not None:
                        has_data = True
                
                # Only store if we actually parsed some data
                if has_data:
                    # Store the data in the appropriate place
                    if current_subcategory:
                        # This is subcategory data
                        parsed_data['categories'][current_category]['subcategories'][current_subcategory] = data
                    else:
                        # This is main category data
                        parsed_data['categories'][current_category]['data'] = data
    
    return parsed_data


# @ReportParser.register_parser("005")
def parse_RPT005(raw_data):
    parsed_data = {}
    # Parse sales posted (day sales info)
    # ...
    return parsed_data

# @ReportParser.register_parser("006")
def parse_RPT006(raw_data):
    parsed_data = {}
    # Parse sales by department
    # ...
    return parsed_data

# @ReportParser.register_parser("008")
def parse_RPT008(raw_data):
    parsed_data = {}
    # Parse received on account
    # ...
    return parsed_data

# @ReportParser.register_parser("012")
def parse_RPT012(raw_data):
    parsed_data = {}
    # Parse saved invoice report
    # ...
    return parsed_data

# @ReportParser.register_parser("013")
def parse_RPT013(raw_data):
    parsed_data = {}
    # Parse inventory status
    # ...
    return parsed_data

# @ReportParser.register_parser("015")
def parse_RPT015(raw_data):
    parsed_data = {}
    # Parse special order communication report
    # ...
    return parsed_data

# @ReportParser.register_parser("017")
def parse_RPT017(raw_data):
    parsed_data = {}
    # Parse daily reportable sales
    # ...
    return parsed_data

# @ReportParser.register_parser("077")
def parse_RPT077(raw_data):
    parsed_data = {}
    # Parse cash report
    # ...
    return parsed_data

# @ReportParser.register_parser("078")
def parse_RPT078(raw_data):
    parsed_data = {}
    # Parse inventory activity
    # ...
    return parsed_data

# @ReportParser.register_parser("079")
def parse_RPT079(raw_data):
    parsed_data = {}
    # Parse checks
    # ...
    return parsed_data

# @ReportParser.register_parser("080")
def parse_RPT080(raw_data):
    parsed_data = {}
    # Parse payment cards
    # ...
    return parsed_data

# @ReportParser.register_parser("082")
def parse_RPT082(raw_data):
    parsed_data = {}
    # Parse price overrides
    # ...
    return parsed_data

# @ReportParser.register_parser("083")
def parse_RPT083(raw_data):
    """
    Parse the Inventory Effectiveness report (RPT083) using precise fixed-width columns
    
    Args:
        raw_data (str): Raw ASCII report data
    
    Returns:
        dict: Parsed data containing report metadata and inventory metrics
    """
    parsed_data = {
        'metadata': {},
        'inventory': {
            'instore_items': {},
            'non_instore_items': {},
            'merchandise_total': {},
            'lost_sales': {},
            'total_merchandise_and_lost': {}
        },
        'ratings': {}
    }
    
    # Parse the report
    lines = raw_data.split('\n')
    
    # Extract metadata from header
    if len(lines) > 1:
        # Get report date and time from first line
        if len(lines[0]) >= 20:
            date_time = lines[0][:20].strip()
            if date_time:
                parsed_data['metadata']['report_date'] = date_time
        
        parsed_data['metadata']['report_type'] = 'Inventory Effectiveness'
        
        # Get store information from second line
        if " - " in lines[1]:
            store_parts = lines[1].split(' - ', 1)
            if len(store_parts) >= 2:
                store_id = store_parts[0].strip()
                # Extract accounting day if present
                if "Accounting Day" in store_parts[1]:
                    store_name_parts = store_parts[1].split("Accounting Day", 1)
                    parsed_data['metadata']['store_name'] = store_name_parts[0].strip()
                    
                    # Extract accounting day number
                    if "-" in store_name_parts[1]:
                        acct_day = store_name_parts[1].split("-")[1].strip()
                        # Get just the number part
                        import re
                        day_match = re.search(r'\d+', acct_day)
                        if day_match:
                            parsed_data['metadata']['accounting_day'] = day_match.group()
                else:
                    parsed_data['metadata']['store_name'] = store_parts[1].strip()
                
                parsed_data['metadata']['store_id'] = store_id
    
    # Find the data section (skip header)
    data_start_idx = 0
    for i, line in enumerate(lines):
        if "Merchandise Inventory" in line and "Today" in line and "MTD" in line:
            data_start_idx = i + 2  # Skip the header row and separator
            break
    
    # Process data lines using precise fixed width columns
    for i in range(data_start_idx, len(lines)):
        line = lines[i]
        
        # Skip empty lines and separators
        if not line.strip() or all(c == '-' or c.isspace() for c in line):
            continue
            
        # Check if we've reached the end of data section
        if "* * Rating * *" in line:
            # Extract ratings with proper column handling
            parsed_data['ratings'] = {
                'today_percent': extract_percentage(line, 56),
                'mtd_percent': extract_percentage(line, 66),
                'ytd_percent': extract_percentage(line, 79),
                'last_year_percent': extract_percentage(line, 92)
            }
            break  # Exit after capturing ratings as specified
            
        # Skip explanatory text
        if any(x in line for x in ["An item is", "The initial", "Any other part"]):
            continue
            
        # Process data lines by identifying the section
        section = None
        
        # Identify which section we're looking at
        if len(line) >= 56:
            section_text = line[:56].strip()
            if "Non-Instore Items" in section_text:
                section = 'non_instore_items'
            elif "Instore Items" in section_text:
                section = 'instore_items'
            elif "Merchandise Total" in section_text:
                section = 'merchandise_total'
            elif "Lost Sales" in section_text:
                section = 'lost_sales'
            elif "Total Merchandise & Lost" in section_text or "Total Merchandise and Lost" in section_text:
                section = 'total_merchandise_and_lost'
                
        if section:
            # Create a properly structured entry
            entry = {}
                
            # Extract all values using precise column positions
            entry['total_today'] = extract_value(line, 56)
            entry['total_mtd'] = extract_value(line, 66)
            entry['total_ytd'] = extract_value(line, 79)
            entry['total_last_year'] = extract_value(line, 92)
            
            parsed_data['inventory'][section] = entry
        
    return parsed_data


def extract_value(line, index):
    """
    Extract a numeric value from a fixed position in a line based on column width,
    handling various formats including commas
    
    Args:
        line (str): The line of text
        index (int): The starting index position
        
    Returns:
        int or None: The extracted value as an integer, or None if not found
    """
    try:
        # Define column widths based on the report structure
        # The columns in RPT083 have these widths:
        # - Today: 9 characters (indexes ~56-64)
        # - MTD: 12 characters (indexes ~66-77)
        # - YTD: 12 characters (indexes ~79-90)
        # - Last Year: 14 characters (indexes ~92-105)
        
        # Determine which column we're extracting and set width accordingly
        if index == 25:  # Merchandise Inventory (variable width)
            # For Merchandise Inventory, extract up to the next column
            end_idx = 56  # Next column starts at 56
            substring = line[index:end_idx].strip()
        elif index == 56:  # Today column
            end_idx = 66  # Next column starts at 66
            substring = line[index:end_idx].strip()
        elif index == 66:  # MTD column
            end_idx = 79  # Next column starts at 79
            substring = line[index:end_idx].strip()
        elif index == 79:  # YTD column
            end_idx = 92  # Next column starts at 92
            substring = line[index:end_idx].strip()
        elif index == 92:  # Last Year column
            # For the last column, read to the end of meaningful content
            substring = line[index:].strip()
            # Trim any trailing content (some reports might have extra spaces/chars)
            for i, char in enumerate(substring):
                if not (char.isdigit() or char == ',' or char == '-'):
                    substring = substring[:i]
                    break
        else:
            return None
        
        # If empty or just whitespace, return None
        if not substring:
            return None
            
        # Remove commas and convert to integer
        clean_value = substring.replace(',', '')
        
        # Handle empty or non-numeric values
        if not clean_value or clean_value.isspace():
            return None
            
        return int(clean_value)
    except (IndexError, ValueError):
        return None


def extract_percentage(line, index):
    """
    Extract a percentage value from a fixed position in a line based on proper column width
    
    Args:
        line (str): The line of text
        index (int): The starting index position
        
    Returns:
        float or None: The extracted percentage as a float, or None if not found
    """
    try:
        # Use same column widths as in extract_value
        if index == 56:  # Today percentage
            end_idx = 66
            substring = line[index:end_idx].strip()
        elif index == 66:  # MTD percentage
            end_idx = 79
            substring = line[index:end_idx].strip()
        elif index == 79:  # YTD percentage
            end_idx = 92
            substring = line[index:end_idx].strip()
        elif index == 92:  # Last Year percentage
            # For the last column, extract carefully
            substring = line[index:].strip()
            # Find the end of the percentage
            for i, char in enumerate(substring):
                if not (char.isdigit() or char == '.' or char == '%' or char == ' '):
                    substring = substring[:i]
                    break
        else:
            return None
            
        # If empty, return None
        if not substring:
            return None
            
        # Find the percentage value - look for digits followed by %
        import re
        match = re.search(r'(\d+\.\d+|\d+)\s*%', substring)
        if match:
            return float(match.group(1))
            
        # If no explicit % symbol, try to convert the whole string if it looks like a number
        clean_value = substring.replace('%', '').strip()
        if clean_value and any(c.isdigit() for c in clean_value):
            return float(clean_value)
            
        return None
    except (IndexError, ValueError):
        return None

# @ReportParser.register_parser("113")
def parse_RPT113(raw_data):
    parsed_data = {}
    # Parse (No description)
    # ...
    return parsed_data

# @ReportParser.register_parser("121")
def parse_RPT121(raw_data):
    parsed_data = {}
    # Parse return defective / labor claim
    # ...
    return parsed_data

# @ReportParser.register_parser("130")
def parse_RPT130(raw_data):
    parsed_data = {}
    # Parse special invoice report
    # ...
    return parsed_data

# @ReportParser.register_parser("203")
def parse_RPT203(raw_data):
    parsed_data = {}
    # Parse transfers invoiced
    # ...
    return parsed_data



# Then use the parser
# parser = ReportParser()
# data = parser.parse_report("001", raw_data)

"""
RPT013: 3147 - INVENTORY STATUS (ON ORDER/BACKORDER, DATE LAST SALE/RECIEVED)
RPT203: 3163 - TRANSFERS INVOICED (INTERSTORE)
RPT006: 3167 - SALES BY DEPARTEMNT (AUTOMOTIVE, LAWN & GARDEN, ETC)
RPT121: 3167 - RETURN DEFECTIVE / LABOR CLAIM BY CUSTOMER
RPT079: 3167 - CHECKS
RPT004: 3167 - SALES JOURNAL
RPT005: 3167 - SALES POSTED (DAY SALES INFO)
RPT080: 3167 - PAYMENT CARDS (TRANSACTIONS)
RPT012: 3167 - SAVED INVOICE REPORT (SAVED INVOICES)
RPT113: 3167 - 
RPT130: 3167 - SPECIAL INVOICE REPORT (CORES, NO-CHARGE, WARRANTY, RETURNS) 
RPT077: 3167 - CASH REPORT (CASH, CARD, CHECK BY DRAWER + TOTAL)
RPT078: 3167 - INVENTORY ACTIVITY (ADJUSTMENTS)
RPT083: 3167 - INVETORY EFFECTIVENESS (IN STORE VS WAREHOUSE)
RPT008: 3167 - RECIEVED ON ACCOUNT (CASH, CARD, CHECK)
RPT082: 3167 - PRICE OVERRIDES
RPT017: 3167 - DAILY REPORTABLE SALES (LINE: GROUP, CUSTOMER)
RPT002: 3168 - TRANSACTION REGISTER
RPT003: 3168 - TRANSACTION ACTIVITY BY QUARTER HOUR
RPT015: 3181 - SPECIAL ORDER COMMUNICATION REPORT
RPT001: 3199 - EMPLOYEE SALES REPORT

"""
