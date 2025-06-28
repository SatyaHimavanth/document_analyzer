from constants import *

from datetime import datetime

import re


def validate_earned_leave_letter(data: dict) -> dict:
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
    pc_no = data.get("pc_no", {}).get("extracted_text", "")
    if not re.match(r"^(PC-|HC|ARSI)[\s\-]?\d{1,4}$", pc_no):
        issues.append(f"Missing or invalid PC/HC/ARSI No.")

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
    status = "Valid" if not issues else "InValid"

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
    if not do_no or not re.match(r"^\d+\/\d{4}$", do_no):
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
    issued_by_text = issued_by

    rank_pattern = r'\b(?:' + '|'.join(re.escape(rank) for rank in LIST_OF_RANKS.keys()) + r')\b'
    unit_pattern = r'\b(?:' + '|'.join(re.escape(unit) for unit in LIST_OF_UNITS_DISTRICTS.keys()) + r')\b'
    district_pattern = r'\b(?:' + '|'.join(re.escape(dist) for dist in LIST_OF_UNITS_DISTRICTS.values()) + r')\b'

    has_rank = re.search(rank_pattern, issued_by_text, re.IGNORECASE)
    has_unit_or_district = re.search(unit_pattern, issued_by_text, re.IGNORECASE) or \
                           re.search(district_pattern, issued_by_text, re.IGNORECASE)
    if not has_rank or not has_unit_or_district:
        issues.append("Invalid or missing Issued By (designation expected).")

    # 7. Issued Date
    issued_date = data.get("issued_date", {}).get("extracted_text", "")
    if not is_valid_date(issued_date):
        issues.append("Invalid or missing Issued Date.")

    # Final status
    status = "Valid" if not issues else "InValid"

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
    if not rc_no or not re.match(r"^[A-Z0-9]+/\d{1,4}/\d{4}$", rc_no):
        issues.append("Invalid or missing Rc No.")

    # HOO No validation
    hoo_no = data.get("hoo_no", {}).get("extracted_text", "")
    if not hoo_no or not re.match(r"^\d{1,5}/\d{4}$", hoo_no):
        issues.append("Invalid or missing HOO No.")

    # Date validation
    date = data.get("date", {}).get("extracted_text", "")
    if not date or not is_valid_date(date):
        issues.append("Invalid or missing Date.")

    # Issued By validation (basic: must include a designation and location)
    issued_by = data.get("issued_by", {}).get("extracted_text", "")
    
    rank_pattern = r'\b(?:' + '|'.join(re.escape(rank) for rank in LIST_OF_RANKS.keys()) + r')\b'
    has_rank = re.search(rank_pattern, issued_by, re.IGNORECASE)
    office_pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in OFFICE_KEYWORDS) + r')\b'
    has_office = re.search(office_pattern, issued_by, re.IGNORECASE)

    if not has_rank or not has_office:
        issues.append("Invalid or missing Issued By field.")

    # Subject
    subject = data.get("subject", {}).get("extracted_text", "")
    if not subject or not subject:
        issues.append("Missing Subject.")

    # Reference Orders validation
    reference_orders = data.get("reference_orders", [])
    if not reference_orders or not all(order.get("extracted_text", "") for order in reference_orders):
        issues.append("Invalid or missing Reference Orders.")

    # Reward Details
    reward_details = data.get("reward_details", [])
    if not reward_details or not all(
        r.get("rank", {}).get("extracted_text", "") and
        r.get("name", {}).get("extracted_text", "") and
        r.get("reward", {}).get("extracted_text", "")
        for r in reward_details
    ):
        issues.append("Invalid or missing Reward Details.")

    # Reason for Reward
    reason = data.get("reason_for_reward", {}).get("extracted_text", "")
    if not reason or not reason.strip():
        issues.append("Missing Reason for Reward.") 

    # Final result
    status = "Valid" if not issues else "InValid"
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
        for fmt in ("%d-%m-%Y"):
            try:
                return datetime.strptime(d, fmt)
            except:
                continue
        return None
    if not is_valid_date(date_str):
        issues.append("Invalid or missing Date of Submission.")

    # 3. Coy Belongs to
    coy = data.get("coy_belongs_to", {}).get("extracted_text", "")
    if not coy or not coy not in LIST_OF_COYS:
        issues.append("Invalid or missing Coy Belongs to.")

    # 4. Rank
    rank = data.get("rank", {}).get("extracted_text", "")
    if not rank or rank not in LIST_OF_RANKS.keys() or rank not in LIST_OF_RANKS.values():
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
    
    if not unit or unit not in LIST_OF_UNITS_DISTRICTS.keys() or not district or district not in LIST_OF_UNITS_DISTRICTS.values():
        issues.append("Missing Unit and/or District in Unit and District field.")

    # Final decision
    status = "Valid" if not issues else "InValid"

    return {
        "document_status": status,
        "issues": issues
    }


def validate_probation_letter(data: dict) -> dict:

    issues=[]

    # Helper to validate date
    def is_valid_date(value: str) -> bool:
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    def is_valid_alpha_name(name: str) -> bool:
        return bool(re.match(r"^[A-Za-z. ]+$", name.strip()))

    def is_nil_or_date_range(text: str) -> bool:
        if text.strip().upper() == "NIL":
            return True
        return bool(re.search(r"From:\s*\d{2}-\d{2}-\d{4}\s*To:\s*\d{2}-\d{2}-\d{4}", text, re.IGNORECASE))

    def is_yes_or_no(text: str) -> bool:
        return text in {"YES", "NO"}

    #1 . service_class_category
    service_class_category = data.get("service_class_category", {}).get("extracted_text", "")
    if not service_class_category or service_class_category not in LIST_OF_RANKS.keys() or service_class_category not in LIST_OF_RANKS.values() :
        issues.append("Missing service class category Reason.")

    # 2. Name of Probationer
    name = data.get("name_of_probationer", {}).get("extracted_text")
    if not name:
        issues.append("Missing required field")
    elif not re.match(r'^[A-Z][a-zA-Z]*\.?[ ]?[A-Z][a-zA-Z]+$', name):
        issues.append("Invalid name format (only alphabets and initials allowed)") 

    # 3. Date of Regularization
    date_of_regularization = data.get("date_of_regularization", {}).get("extracted_text")
    if not is_valid_date(date_of_regularization):
        issues.append("Invalid or missing Date of Regularization.")

    # 4. Period of Probation Prescribed
    probation_period = data.get("period_of_probation_prescribed", {}).get("extracted_text", "")
    if not probation_period:
        issues.append("Missing Period of Probation Prescribed.")
        
    # 5. Leave Taken During Probation
    leave_taken = data.get("leave_taken_during_probation", {}).get("extracted_text", "")
    if not leave_taken or not is_nil_or_date_range(leave_taken):
        issues.append("Invalid Leave Taken During Probation.")

    # 6. Date of Completion of Probation
    completion_date = data.get("date_of_completion_of_probation", {}).get("extracted_text", "")
    if not is_valid_date(completion_date):
        issues.append("Invalid or missing Date of Completion of Probation.")

    # 7. Tests to be Passed
    tests = data.get("tests_to_passed_during_probation", {}).get("extracted_text", "")
    if not tests :
        issues.append("Invalid or missing Tests to be Passed During Probation.")

    # 8. Punishments During Probation
    punishment = data.get("punishment_during_probation", {}).get("extracted_text", "")
    if not punishment:
        issues.append("Invalid or missing Punishments During Probation.")

    # 9. Pending PR/OE
    pending = data.get("pending_pr_oe", {}).get("extracted_text", "")
    if not pending :
        issues.append("Invalid or missing Pending PR/OE.")

    # 10. Character and Conduct
    character = data.get("character_and_conduct", {}).get("extracted_text", "")
    if not character:
        issues.append("Invalid or missing Character and Conduct.")

    
    # 11. Firing Practice Completed
    firing = data.get("firing_practice_completed", {}).get("extracted_text", "")
    if not is_yes_or_no(firing):
        issues.append("Invalid or missing Firing Practice Completed.")

    # 12. remarks
    remarks_ic = data.get("remarks_of_ic_officer", {}).get("extracted_text", "")
    if not remarks_ic:
        issues.append("Missing Remarks of I/C Officer.")

    #13
    remarks_cmdt = data.get("remarks_of_commandant", {}).get("extracted_text", "")
    if not remarks_cmdt:
        issues.append("Missing Remarks of Commandant.")

    #14
    remarks_dig = data.get("remarks_of_dig", {}).get("extracted_text", "")
    if not remarks_dig:
        issues.append("Missing Remarks of DIG.")

    # 15. ADGP Orders
    adgp = data.get("adgp_orders", {}).get("extracted_text", "")
    if not adgp:
        issues.append("Missing ADGP Orders.")

    # 16. Date of Birth
    dob = data.get("dob", {}).get("extracted_text", "")
    if not is_valid_date(dob):
        issues.append("Invalid or missing Date of Birth.")

    # 17. Salary
    salary = data.get("salary", {}).get("extracted_text", "")
    if not salary or not re.match(r"^\d+(\.\d+)?$", salary):
        issues.append("Invalid or missing Salary.")

    # 18. Qualification
    qualification = data.get("qualification", {}).get("extracted_text", "")
    if not qualification:
        issues.append("Missing Qualification.")

    # 19. Acceptance of Self Appraisal Report
    appraisal = data.get("acceptance_of_self_appraisal_report_part1", {}).get("extracted_text", "")
    if appraisal not in {"Accepted", "Not Accepted"}:
        issues.append("Invalid Acceptance of Self Appraisal Report – Part-I.")

    # 20. Officer Performance Assessment
    performance = data.get("assessment_of_officers_permormance_during_the_year", {}).get("extracted_text", "")
    if not performance in {"Satisfactory", "Good", "Excellent"}:
        issues.append("Invalid or missing Officer’s Performance Assessment.")

    # Reporting Officer validation (with Date field handled)
    ro = data.get("reporting_officer", {})
    ro_date = ro.get("date", {}).get("extracted_text", "")
    ro_name = ro.get("name", {}).get("extracted_text", "")
    ro_designation = ro.get("designation", {}).get("extracted_text", "")

    if ro_date and not is_valid_date(ro_date):
        issues.append("Reporting Officer Date is invalid (must be DD-MM-YYYY).")

    if not ro_name or not is_valid_alpha_name(ro_name):
        issues.append("Invalid or missing Reporting Officer Name.")

    if not ro_designation or not ro_designation.strip():
        issues.append("Missing Reporting Officer Designation.")


    # 22. Countersigning Officer
    co = data.get("counter_singing_officer", {})
    co_name = co.get("name", {}).get("extracted_text", "")
    co_designation = co.get("designation", {}).get("extracted_text", "")
    co_remarks = co.get("remarks", {}).get("extracted_text", "")

    if not co_name or not is_valid_alpha_name(co_name):
        issues.append("Invalid or missing Countersigning Officer Name.")

    if not co_designation or not co_designation.strip():
        issues.append("Missing Countersigning Officer Designation.")

    if not co_remarks or not co_remarks.strip():
        issues.append("Missing Countersigning Officer Remarks.")


    # 23. Head of Department Opinion
    hod = data.get("head_of_department_opinion", {})
    hod_opinion = hod.get("opinion", {}).get("extracted_text", "")
    hod_name = hod.get("name", {}).get("extracted_text", "")
    hod_designation = hod.get("designation", {}).get("extracted_text", "")
    if not hod_opinion:
        issues.append("Missing Head of Department Opinion.")
    if not is_valid_alpha_name(hod_name):
        issues.append("Invalid or missing Head of Department Name.")
    if not hod_designation:
        issues.append("Missing Head of Department Designation.")

    status = "Valid" if not issues else "InValid"

    return {
        "document_status": status,
        "issues": issues
    }


validation_functions = {
    "EarnedLeaveLetter": validate_earned_leave_letter,
    "PunishmentLetter": validate_punishment_letter,
    "RewardLetter": validate_reward_letter,
    "MedicalLeave": validate_medical_leave,
    "ProbationLetter": validate_probation_letter
}