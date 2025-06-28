from datetime import datetime

import re


def validate_earned_leave_letter(extracted_text: dict) -> bool:
    issues = []

    # Helper to validate date
    def is_valid_date(value: str) -> bool:
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    # 1. Rc No
    rc = data.get("rc_no", {}).get("extracted_text", "")
    if not rc or not re.match(r"^[A-Z0-9]+/\d{1,4}/\d{4}$", rc.split()[-1]):
        issues.append("Invalid or missing Rc No.")

    # 2. HOD No
    hod = data.get("hod_no", {}).get("extracted_text", "")
    if not hod or not re.match(r"^\d{1,4}/\d{4}$", hod.split()[-1]):
        issues.append("Invalid or missing HOD No.")

    # 3. PC/HC/ARSI No (conditional)
    if designation in {"PC", "HC", "ARSI"}:
        pc_no = data.get("pc_no", {}).get("extracted_text", "")
        if not re.match(r"^(PC-|HC|ARSI)[\s\-]?\d{1,4}$", pc_no):
            issues.append(f"Missing or invalid PC/HC/ARSI No for designation '{designation}'.")

    # 4. Name
    name = data.get("name", {}).get("extracted_text", "")
    if not name or not re.match(r"^[A-Za-z. ]+$", name):
        issues.append("Invalid or missing Name.")

    # 5. Date
    date = data.get("date", {}).get("extracted_text", "")
    if not date or not is_valid_date(date):
        issues.append("Invalid or missing Date.")

    # 6. Number of Days
    no_of_days = data.get("no_of_days", {}).get("extracted_text", "")
    if not no_of_days.isdigit() or int(no_of_days) <= 0:
        issues.append("Invalid or missing Number of Days.")

    # 7. Leave From Date
    from_date = data.get("leave_from_date", {}).get("extracted_text", "")
    if not is_valid_date(from_date):
        issues.append("Invalid Leave From Date.")

    # 8. Leave To Date
    to_date = data.get("leave_to_date", {}).get("extracted_text", "")
    if not is_valid_date(to_date):
        issues.append("Invalid Leave To Date.")

    # 9. Leave Reason
    reason = data.get("leave_reason", {}).get("extracted_text", "")
    if not reason.strip():
        issues.append("Missing Leave Reason.")

    # 10. Leave Date Logic
    try:
        if is_valid_date(from_date) and is_valid_date(to_date):
            from_dt = datetime.strptime(from_date, "%d-%m-%Y")
            to_dt = datetime.strptime(to_date, "%d-%m-%Y")
            if to_dt < from_dt:
                issues.append("Leave To Date is earlier than Leave From Date.")
    except Exception:
        pass

    # Final decision
    status = "Approved" if not issues else "Disapproved"

    return {
        "document_status": status,
        "issues": issues
    }


def validate_medical_leave(data: dict) -> dict:
    issues = []

    # 1. Name validation
    name = data.get("name", {}).get("extracted_text", "")
    if not name or not re.match(r"^[A-Za-z. ]+$", name):
        issues.append("Invalid or missing Name.")

    # 2. Date of Submission (format DD-MM-YYYY)
    date_str = data.get("date_of_submission", {}).get("extracted_text", "")
    def is_valid_date(d):
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"):
            try:
                return datetime.strptime(d, fmt)
            except:
                continue
        return None
    if not is_valid_date(date_str):
        issues.append("Invalid or missing Date of Submission.")

    # 3. Coy Belongs to
    coy = data.get("coy_belongs_to", {}).get("extracted_text", "")
    if not coy or not re.match(r"^[A-Za-z0-9 ]+Coy$", coy.strip(), re.IGNORECASE):
        issues.append("Invalid or missing Coy Belongs to.")

    # 4. Rank
    rank = data.get("rank", {}).get("extracted_text", "")
    if not rank or not re.match(r"^[A-Za-z. ]+$", rank):
        issues.append("Invalid or missing Rank.")

    # 5. Leave Reason
    reason = data.get("leave_reason", {}).get("extracted_text", "")
    if not reason or not reason.strip():
        issues.append("Missing Leave Reason.")

    # 6. Phone Number
    phone = data.get("phone_number", {}).get("extracted_text", "")
    if not re.match(r"^[6-9]\d{9}$", phone):
        issues.append("Invalid or missing Phone Number.")

    # 7. Unit and District
    unit_data = data.get("unit_and_district", {})
    unit = unit_data.get("unit", {}).get("extracted_text", "")
    district = unit_data.get("district", {}).get("extracted_text", "")
    if not unit or not district:
        issues.append("Missing Unit and/or District in Unit and District field.")

    # Final decision
    status = "Approved" if not issues else "Disapproved"

    return {
        "document_status": status,
        "issues": issues
    }


def validate_reward_letter(data: dict) -> dict:
    issues = []

    # Helper to check date format
    def is_valid_date(date_str: str):
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except:
            return False

    # Rc No validation
    rc_no = data.get("rc_no", {}).get("extracted_text", "")
    if not rc_no or not re.match(r"^[A-Z0-9]+/\d{1,4}/\d{4}$", rc_no.strip()):
        issues.append("Invalid or missing Rc No.")

    # HOO No validation
    hoo_no = data.get("hoo_no", {}).get("extracted_text", "")
    if not hoo_no or not re.match(r"^\d{1,5}/\d{4}$", hoo_no.strip()):
        issues.append("Invalid or missing HOO No.")

    # Date validation
    date = data.get("date", {}).get("extracted_text", "")
    if not date or not is_valid_date(date.strip()):
        issues.append("Invalid or missing Date.")

    # Issued By validation (basic: must include a designation and location)
    issued_by = data.get("issued_by", {}).get("extracted_text", "")
    if not issued_by or not re.search(r"\b(Commissioner|Inspector|Director|Superintendent|Constable|Officer|DGP|DIG|IGP)\b", issued_by, re.IGNORECASE):
        issues.append("Invalid or missing Issued By field.")

    # Subject
    subject = data.get("subject", {}).get("extracted_text", "")
    if not subject or not subject.strip():
        issues.append("Missing Subject.")

    # Reference Orders validation
    reference_orders = data.get("reference_orders", [])
    if not reference_orders or not all(order.get("extracted_text", "").strip() for order in reference_orders):
        issues.append("Invalid or missing Reference Orders.")

    # Reward Details
    reward_details = data.get("reward_details", [])
    if not reward_details or not all(
        r.get("rank", {}).get("extracted_text", "").strip() and
        r.get("name", {}).get("extracted_text", "").strip() and
        r.get("reward", {}).get("extracted_text", "").strip()
        for r in reward_details
    ):
        issues.append("Invalid or missing Reward Details.")

    # Reason for Reward
    reason = data.get("reason_for_reward", {}).get("extracted_text", "")
    if not reason or not reason.strip():
        issues.append("Missing Reason for Reward.")

    # Final result
    status = "Approved" if not issues else "Disapproved"
    return {
        "document_status": status,
        "issues": issues
    }


def validate_punishment_letter(data: dict) -> dict:
    issues = []

    # Helper to validate date format
    def is_valid_date(date_str):
        formats = ["%d/%m/%y", "%d-%m-%Y", "%d-%m-%y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                datetime.strptime(date_str.strip(), fmt)
                return True
            except:
                continue
        return False

    # 1. R.C. No.
    rc_no = data.get("rc_no", {}).get("extracted_text", "")
    if not rc_no or not re.search(r"\d+\/[A-Z0-9]+\/PR-\d+\/\d{2}-\d{2}", rc_no, re.IGNORECASE):
        issues.append("Invalid or missing R.C. No.")

    # 2. D.O. No.
    do_no = data.get("do_no", {}).get("extracted_text", "")
    if not do_no or not re.match(r"^\d+\/\d{4}$", do_no.strip()):
        issues.append("Invalid or missing D.O. No.")

    # 3. Order Date
    order_date = data.get("order_date", {}).get("extracted_text", "")
    if not is_valid_date(order_date):
        issues.append("Invalid or missing Order Date.")

    # 4. Punishment Awarded
    punishment = data.get("punishment_awarded", {}).get("extracted_text", "")
    if not punishment or not re.search(r"PP\s?(I|II)", punishment, re.IGNORECASE):
        issues.append("Missing or invalid Punishment Awarded field (PP I or PP II not found).")

    # 5. Delinquency Description
    delinquency = data.get("deliquency_description", {}).get("extracted_text", "")
    if not delinquency or "w.e.f." not in delinquency.lower():
        issues.append("Invalid or missing Delinquency Description (must contain w.e.f.).")

    # 6. Issued By
    issued_by = data.get("issued_by", {}).get("extracted_text", "")
    if not issued_by or not re.search(r"(Commandant|Inspector|Officer|Superintendent|Commissioner|Director|IGP|DIG)", issued_by, re.IGNORECASE):
        issues.append("Invalid or missing Issued By (designation expected).")

    # 7. Issued Date
    issued_date = data.get("issued_date", {}).get("extracted_text", "")
    if not is_valid_date(issued_date):
        issues.append("Invalid or missing Issued Date.")

    # Final status
    status = "Approved" if not issues else "Disapproved"

    return {
        "document_status": status,
        "issues": issues
    }


