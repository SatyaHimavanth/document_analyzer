from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Union
from uuid import uuid4
from fastapi import Form
from datetime import datetime

class LoginModel(BaseModel):
    user_name: str
    password: str
    remember_me: bool = Field(default_factory=False)

class FileModel(BaseModel):
    file_id: str | None = Field(description="Unique identifier for the file")
    upload_date: str = Field(description="Date when the file was uploaded. Format: DD MM YYYY HH:MM:SS")
    filename: str | None = Field(description="Name of the uploaded file")
    file_path: str | None = Field(description="Path where the file is stored on the server")
    document_type: Optional[str] = "OtherTemplate"
    extracted_text: Optional[dict] = {}
    content_type: Literal["application/pdf", "image/jpeg", "image/png"]


class InsertUserFileModel(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    files: List[FileModel] = Field(description="List of files uploaded by the user")


class UserModel(BaseModel):
    user_id: str = None
    name: str = None
    email: str = None
    password: Optional[str] = None
    phone: Optional[str] = None


class FileFiltersModel(BaseModel):
    template_type: str | None
    upload_date: str | None
    file_type: str | None


## Initial document invocation
## document_type, extracted_text, stamps, signatures

class ExtractedTextSpan(BaseModel):
    text: str = Field(..., description="Extracted text snippet")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    text_type: Literal["machine_printed", "handwritten"] = Field(..., description="Text type")


class DocumentClassificationResult(BaseModel):
    document_type: Literal[
        "PunishmentLetter",
        "EarnedLeaveLetter",
        "RewardLetter",
        "MedicalLeave",
        "ProbationLetter"
    ] = Field(..., description="Classified document type")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score for classification")
    extracted_text: List[ExtractedTextSpan] = Field(..., description="List of extracted text segments")



class ExtractedTextSpan(BaseModel):
    text: str = Field(..., description="Extracted text snippet")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    text_type: Literal["machine_printed", "handwritten"] = Field(..., description="Text type")


class DocumentClassificationResult(BaseModel):
    document_type: Literal[
        "PunishmentLetter",
        "EarnedLeaveLetter",
        "RewardLetter",
        "MedicalLeave",
        "ProbationLetter"
    ] = Field(..., description="Classified document type")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score for classification")
    extracted_text: List[ExtractedTextSpan] = Field(..., description="List of extracted text segments")



## Document Parsing
# Note: ""document_type"" shouuld be in all document models to identify the type of document being parsed.
class ExtractedField(BaseModel):
    extracted_text: Optional[Union[str, int]] = Field(None, description="Extracted field text (or None if not found)")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0 to 1), None if not available")
    text_type: Optional[Literal["machine_printed", "handwritten"]] = Field(
        None, description="Type of text: machine_printed or handwritten"
    )

class EarnedLeaveLetter(BaseModel):
    """
    Structured model for Earned Leave Letter.
    Each field includes the extracted value, confidence score, and text type.
    Fields not found by the extractor will return None values.
    """

    rc_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Rc_No",
        description="The Revised Current Number (R c. No.) is used to uniquely track and reference official leave-related documents within departmental records. Format: Combination of section code, serial number, and year (e.g., B4/149/2020)."
    )

    hod_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="HOD_No",
        description="The Head of Department Number (H.O.D No.) is used to officially record and authorize departmental orders. Format: Serial number and year separated by a slash (e.g., 72/2020)."
    )

    pc_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="PC_No",
        description="The Police Constable Number (PC No.), HC or ARSI uniquely identifies an individual constable. Format: Prefix 'PC-', 'HC' or 'ARSI' followed by 1 to 4-digit number (e.g., PC-1158)."
    )

    name: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Name",
        description="Full name of the individual police personnel. Format: 'Initial. Full Name' or 'Full Name' (e.g., S. Praveen Kumar). Only alphabets and valid separators (period and space); no numbers or special characters."
    )

    date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Date",
        description="Specific date associated with the document, such as issue date. Format: DD-MM-YYYY."
    )

    no_of_days: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="No_of_days",
        description="Total number of days associated with the leave period. Format: Positive whole number (e.g., 7)."
    )

    leave_from_date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="leave_from_date",
        description="The start date from which earned leave is availed. Format: DD-MM-YYYY."
    )

    leave_to_date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="leave_to_date",
        description="The end date up to which the earned leave is availed. Format: DD-MM-YYYY."
    )

    leave_reason: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="leave_reason",
        description="Reason for availing leave, such as personal, medical, or official. Format: Quoted explanation of the reason."
    )

    stamp: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Stamp",
        description="Stamp details if any, typically includes department seal impression or text."
    )

    stamp_validation: Optional[bool] = Field(
        default=None,
        alias="Stamp_Validation",
        description="Whether the stamp on the document is validated."
    )

    signature: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Signature",
        description="Signature details as extracted from the document, Only handwritten. assign True of False"
    )

    document_status: Literal["Valid", "Invalid"] = Field(
        ...,
        description="Document validation status. Indicates whether the document passed automated validation."
    )


from typing import Literal
from pydantic import BaseModel, Field

class ExtractedField(BaseModel):
    extracted_text: str | None = None
    confidence: float | None = None
    text_type: str | None = None

class PunishmentLetter(BaseModel):
    rc_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="R c. No",
        description=(
            "Revised Current Number used to uniquely identify the punishment order. "
            "Format: Combination of reference number, obliques, section code, case type (e.g., PR), "
            "hyphenated serial number, and the year range. Example: B1/123/PR-309/22-23."
        )
    )

    do_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="D. O No",
        description=(
            "Departmental Order Number referencing the official issue of punishment. "
            "Format: Reference Number/YYYY (e.g., 709/2022)."
        )
    )

    order_date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Order_date",
        description=(
            "Date on which the punishment order was issued. "
            "Format: DD/MM/YY or DD-MM-YYYY."
        )
    )

    punishment_awarded: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Punishment_awarded",
        description=(
            "Type of punishment awarded to the personnel. "
            "Format: PP I or PP II followed by duration and conditions. "
            "Should clearly indicate punishment level, duration, and applicable clause."
        )
    )

    deliquency_description: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Deliquency_Description",
        description=(
            "Details of the misconduct or delinquency for which the punishment is awarded. "
            "Format: A quoted explanation of the violation. "
            "Should include details and effective date (w.e.f.)."
        )
    )

    issued_by: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Issued By",
        description=(
            "The authority who issued the punishment order. "
            "Format: Designation and Unit. Should include officer rank and unit details."
        )
    )

    issued_date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Issued Date",
        description=(
            "Date when the signed document was finalized and issued. "
            "Format: DD/MM/YY or DD-MM-YYYY."
        )
    )

    signature: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Signature",
        description="Signature details from the document (handwritten or printed)."
    )

    document_status: Literal["Valid", "Invalid"] = Field(
        ...,
        description="Document validation status. Indicates whether the document passed verification."
    )


class RewardDetail(BaseModel):
    rank: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Rank of the officer receiving the reward."
    )
    name: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Full name of the officer receiving the reward."
    )
    reward: ExtractedField = Field(
        default_factory=ExtractedField,
        description="Reward amount or type awarded to the officer."
    )

class RewardLetter(BaseModel):
    rc_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="R c No.",
        description=(
            "Revised Current Number (Rc. No.) used to uniquely track and reference the reward document. "
            "Format: Combination of section code, serial number, and year (e.g., B4/149/2020)."
        )
    )
    hoo_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="H.O.D No.",
        description=(
            "Head of Office Communication number associated with the reward letter. "
            "Format: Reference Number/YYYY (e.g., 709/2020)."
        )
    )
    date: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Date",
        description=(
            "The date on which the reward order was issued. "
            "Format: DD-MM-YYYY."
        )
    )
    issued_by: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Issued By",
        description=(
            "The name and designation of the issuing authority. "
            "Must include valid designation and office name."
        )
    )
    subject: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Subject",
        description=(
            "Title of the document indicating the purpose of the reward order. "
            "Format: Short description line from the document."
        )
    )
    reference_orders: List[ExtractedField] = Field(
        default_factory=list,
        alias="Reference Orders",
        description=(
            "List of official order references used in the reward sanction. "
            "Should list valid government order references."
        )
    )
    reward_details: List[RewardDetail] = Field(
        default_factory=list,
        alias="Reward Details",
        description=(
            "Details of each officer receiving the reward. "
            "Each entry must include valid officer rank, full name, and reward."
        )
    )
    reason_for_reward: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Reason for Reward",
        description=(
            "The reason provided for granting the reward to the officers. "
            "Format: A descriptive sentence."
        )
    )
    stamp: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Stamp",
        description="Stamp details if present on the document."
    )
    stamp_validation: Optional[bool] = Field(
        None,
        alias="Stamp_Validation",
        description="Whether the stamp is valid and present."
    )
    signature: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Signature",
        description="Signature details from the document."
    )
    document_status: Literal["Valid", "Invalid"] = Field(
        ...,
        description="Document validation status indicating whether the document is verified."
    )


class UnitAndDistrict(BaseModel):
    unit: ExtractedField = Field(
        default_factory=ExtractedField,
        description=(
            "Indicates the unit or company the personnel belongs to. "
            "Format: Alphanumeric name (e.g., A Coy, B Coy, HQ Coy)."
        )
    )
    district: ExtractedField = Field(
        default_factory=ExtractedField,
        description=(
            "Represents the district associated with the unit. "
            "Format: Standard district name (e.g., Vizianagaram)."
        )
    )
    validation: Literal["Valid", "InValid"] = Field(description="Valid if above two fields are valid.")

class MedicalLeave(BaseModel):
    name: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Name",
        description=(
            "Full name of the personnel submitting the form. "
            "Should contain only alphabets, periods (.) and spaces. No digits or special characters."
        )
    )
    date_of_submission: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Date of Submission",
        description=(
            "The date on which the document or request was submitted. "
            "Format: DD-MM-YYYY."
        )
    )
    coy_belongs_to: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Coy Belongs to",
        description=(
            "Indicates the company (Coy) or division the personnel belongs to. "
            "Format: Alphanumeric unit or company name (e.g., A Coy, B Coy, HQ Coy)."
        )
    )
    rank: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Rank",
        description=(
            "The official designation or rank of the personnel (e.g., PC, HC, SI). "
            "Format: Standard police ranks (abbreviations or full form)."
        )
    )
    leave_reason: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Leave Reason",
        description=(
            "The stated reason for requesting or availing leave. "
            "Format: A descriptive sentence explaining the purpose (e.g., medical emergency)."
        )
    )
    hc_no: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="HC No",
        description="House/Constable Number or personal identifier for internal use."
    )
    phone_number: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Phone Number",
        description=(
            "The contact number of the individual for communication during leave or for official purposes. "
            "Format: 10-digit mobile number starting with 6-9 (e.g., 9876543210)."
        )
    )
    unit_and_district: UnitAndDistrict = Field(
        default_factory=UnitAndDistrict,
        alias="Unit and District",
        description=(
            "Represents the full unit name and its associated district. "
            "Format: Unit name followed by district (e.g., 5th Bn. APSP, Vizianagaram)."
        )
    )
    stamp: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Stamp",
        description="Official stamp included in the document, if any."
    )
    stamp_validation: Optional[bool] = Field(
        None,
        alias="Stamp_Validation",
        description="Whether the stamp is identified and validated."
    )
    signature: ExtractedField = Field(
        default_factory=ExtractedField,
        alias="Signature",
        description="Signature of the issuing or approving authority."
    )
    document_status: Literal["Valid", "Invalid"] = Field(
        ...,
        description="Document validation status indicating if the document is complete and authentic."
    )


class ReportingOfficer(BaseModel):
    date: Optional[ExtractedField] = Field(default_factory=ExtractedField, alias="Date", description="Date the report was signed by the Reporting Officer. Format: DD-MM-YYYY")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name", description="Name of the Reporting Officer.")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation", description="Designation of the Reporting Officer. Format: Officer Designation")

class CounterSingingOfficer(BaseModel):
    date: Optional[ExtractedField] = Field(default_factory=ExtractedField, alias="Date", description="Date the countersigning was made. Format: DD-MM-YYYY or Not Found")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name", description="Name of the Countersigning Officer.")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation", description="Designation of the Countersigning Officer. Format: Officer Designation")
    remarks: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks", description="Remarks given by the Countersigning Officer. Example: I agree with Remarks of the reporting officer")

class HeadOfDepartmentOpinion(BaseModel):
    opinion: ExtractedField = Field(default_factory=ExtractedField, alias="Opinion", description="Final status regarding probation. Example: Probation Declared")
    date: Optional[ExtractedField] = Field(default_factory=ExtractedField, alias="Date", description="Date of issuance of HOD opinion. Format: DD-MM-YYYY")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name", description="Name of the Head of Department.")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation", description="Designation of the HOD. Format: Officer Designation")

class SignField(BaseModel):
    extracted_text: Optional[bool] = Field(None, description="True if signed else False")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0 to 1), None if not available")
    text_type: Optional[Literal["machine_printed", "handwritten"]] = Field(
        None, description="Type of text: machine_printed or handwritten"
    )

class ProbationLetter(BaseModel):
    service_class_category: ExtractedField = Field(default_factory=ExtractedField, alias="Service Class Category", description="The class of police service the officer belongs to. Must be a valid designation like 'Reserve Inspector of Police'.")
    name_of_probationer: ExtractedField = Field(default_factory=ExtractedField, alias="Name of Probationer", description="Full name of the probationer officer. Should only contain alphabets and valid initials.")
    date_of_regularization: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Regularization", description="Date on which probation period officially starts. Format: DD-MM-YYYY")
    period_of_probation_prescribed: ExtractedField = Field(default_factory=ExtractedField, alias="Period of Probation Prescribed", description="Duration of the probation period. Descriptive duration such as 'one year', 'two years' etc.")
    leave_taken_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Leave Taken During Probation", description="Details of any leave availed during the probation period. Must include From and To dates or 'NIL'.")
    date_of_completion_of_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Completion of Probation", description="Date when the probation is completed after leave deductions. Format: DD-MM-YYYY")
    tests_to_passed_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Tests to be Passed During Probation", description="Any exams required to be cleared during probation. If none, value must be 'NIL'.")
    punishment_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Punishment During Probation", description="Any punishments awarded during the probation period. If none, value must be 'NIL'.")
    pending_pr_oe: ExtractedField = Field(default_factory=ExtractedField, alias="Pending PR/OE", description="Details of any pending PR (Punishment Register) or OE (Oral Enquiry). If none, value must be 'NIL'.")
    character_and_conduct: ExtractedField = Field(default_factory=ExtractedField, alias="Character and Conduct", description="Assessment of officer's behavior and discipline. Common values: 'Satisfactory', 'Good', 'Excellent'.")
    firing_practice_completed: ExtractedField = Field(default_factory=ExtractedField, alias="Firing Practice Completed", description="Whether the officer completed mandatory firing practice. Accepted values: 'YES', 'NO'.")
    remarks_of_ic_officer: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of I/C Officer", description="Initial commanding officer's recommendation regarding probation. Must be a clear statement of recommendation.")
    remarks_of_commandant: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of Commandant", description="Final remarks of the Commandant regarding probation. Must be a recommendation statement.")
    remarks_of_dig: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of DIG", description="Opinion of the Deputy Inspector General of Police. Should confirm or disagree with earlier recommendations.")
    # probation_extended_for: ExtractedField = Field(default_factory=ExtractedField, alias="Probihition Extended duration", description="Extended Duration for prohibition")
    adgp_orders: ExtractedField = Field(default_factory=ExtractedField, alias="ADGP Orders", description="Final order and status of probation from ADGP. Must include effective dates and 'A list' inclusion if mentioned.")
    dob: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Birth", description="Date of birth of the probationer. Format: DD-MM-YYYY")
    salary: ExtractedField = Field(default_factory=ExtractedField, alias="Salary", description="The salary taken by the officer during probationer per month. Format: Integer Example: 55540. Just number")
    qualification: ExtractedField = Field(default_factory=ExtractedField, alias="Qualification", description="Educational qualification of the probationer. Example: B.Tech (CSE)")
    acceptance_of_self_appraisal_report_part1: ExtractedField = Field(default_factory=ExtractedField, alias="Acceptance of Self Appraisal Report Part 1", description="Whether the self appraisal report was accepted or not. Accepted values: 'Accepted', 'Not Accepted'")
    assessment_of_officers_permormance_during_the_year: ExtractedField = Field(default_factory=ExtractedField, alias="Assessment of Officer's Performance During the Year", description="Annual assessment of officer’s performance. Typical values: 'Satisfactory', 'Good', 'Excellent'")
    reporting_officer: ReportingOfficer = Field(default_factory=ReportingOfficer, alias="Reporting Officer")
    counter_singing_officer: CounterSingingOfficer = Field(default_factory=CounterSingingOfficer, alias="Counter Singing Officer")
    head_of_department_opinion: HeadOfDepartmentOpinion = Field(default_factory=HeadOfDepartmentOpinion, alias="Head of Department Opinion")

    stamp1: ExtractedField = Field(default_factory=ExtractedField, alias="DIG Stamp")
    stamp_validation1: Optional[bool] = Field(None, alias="DIG_Stamp_Validation")
    signature1: SignField = Field(default_factory=SignField, alias="DIG Signature")

    stamp2: ExtractedField = Field(default_factory=ExtractedField, alias="ADGP Stamp")
    stamp_validation2: Optional[bool] = Field(None, alias="ADGP_Stamp_Validation")
    signature2: SignField = Field(default_factory=SignField, alias="ADGP Signature")

    stamp3: ExtractedField = Field(default_factory=ExtractedField, alias="Reporting Officer Stamp")
    stamp_validation3: Optional[bool] = Field(None, alias="Reporting_Officer_Stamp_Validation")
    signature3: SignField = Field(default_factory=SignField, alias="Reporting Officer Signature")

    stamp4: ExtractedField = Field(default_factory=ExtractedField, alias="Counter Singing Officer Stamp")
    stamp_validation4: Optional[bool] = Field(None, alias="Counter_Singing_Officer_Stamp_Validation")
    signature4: SignField = Field(default_factory=SignField, alias="Counter Singing Officer Signature")

    stamp5: ExtractedField = Field(default_factory=ExtractedField, alias="Head Of Department Stamp")
    stamp_validation5: Optional[bool] = Field(None, alias="Head_Of_department_Stamp_Validation")
    signature5: SignField = Field(default_factory=SignField, alias="Head Of Department Signature")

    document_status: Literal["Valid", "Invalid"] = Field(..., description="Status of the document validation")




document_models = {
    "EarnedLeaveLetter": EarnedLeaveLetter,
    "PunishmentLetter": PunishmentLetter,
    "RewardLetter": RewardLetter,
    "MedicalLeave": MedicalLeave,
    "ProbationLetter": ProbationLetter
}
