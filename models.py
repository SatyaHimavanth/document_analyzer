from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Union
from uuid import uuid4
from fastapi import Form
from datetime import datetime


class DataModel(BaseModel):
    id: str = Field(description="Unique identifier for the data entry", default_factory=lambda: str(uuid4()))
    message: str = Field(description="The message content of the data entry")

    @classmethod
    def as_form(
        cls,
        id: str = Form(default_factory=lambda: str(uuid4())),
        message: str = Form(...)
    ):
        return cls(id=id, message=message)


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
    email: EmailStr = None
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
    rc_no: ExtractedField = Field(default_factory=ExtractedField, alias="Rc_No", description="R c No. e.g., B4/149/2020")
    hod_no: ExtractedField = Field(default_factory=ExtractedField, alias="HOD_No", description="H.O.D No. e.g., 72/2020")
    pc_no: ExtractedField = Field(default_factory=ExtractedField, alias="PC_No", description="PC/HC/ARSI No. e.g., PC-1158 or HC123")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name", description="Full name of the individual")
    date: ExtractedField = Field(default_factory=ExtractedField, alias="Date", description="Document date (DD-MM-YYYY)")
    no_of_days: ExtractedField = Field(default_factory=ExtractedField, alias="No_of_days", description="Number of leave days")
    leave_from_date: ExtractedField = Field(default_factory=ExtractedField, alias="leave_from_date", description="Leave start date")
    leave_to_date: ExtractedField = Field(default_factory=ExtractedField, alias="leave_to_date", description="Leave end date")
    leave_reason: ExtractedField = Field(default_factory=ExtractedField, alias="leave_reason", description="Reason for leave")
    stamp: ExtractedField = Field(default_factory=ExtractedField, alias="Stamp", description="Stamp details if any")
    stamp_validation: Optional[bool] = Field(None, alias="Stamp_Validation", description="Whether stamp is validated")
    signature: ExtractedField = Field(default_factory=ExtractedField, alias="Signature", description="Signature details")
    document_status: Literal["Valid", "Invalid"] = Field(..., description="Document validation status")


class PunishmentLetter(BaseModel):
    rc_no: ExtractedField = Field(default_factory=ExtractedField, alias="R c. No")
    do_no: ExtractedField = Field(default_factory=ExtractedField, alias="D. O No")
    order_date: ExtractedField = Field(default_factory=ExtractedField, alias="Order_date")
    punishment_awarded: ExtractedField = Field(default_factory=ExtractedField, alias="Punishment_awarded")
    deliquency_description: ExtractedField = Field(default_factory=ExtractedField, alias="Deliquency_Description")
    issued_by: ExtractedField = Field(default_factory=ExtractedField, alias="Issued By")
    issued_date: ExtractedField = Field(default_factory=ExtractedField, alias="Issued Date")
    signature: ExtractedField = Field(default_factory=ExtractedField, alias="Signature")
    document_status: Literal["Valid", "Invalid"] = Field(..., description="Document validation status")


class RewardDetail(BaseModel):
    rank: ExtractedField = Field(default_factory=ExtractedField)
    name: ExtractedField = Field(default_factory=ExtractedField)
    reward: ExtractedField = Field(default_factory=ExtractedField)

class RewardLetter(BaseModel):
    rc_no: ExtractedField = Field(default_factory=ExtractedField, alias="R c No.")
    hoo_no: ExtractedField = Field(default_factory=ExtractedField, alias="H.O.D No.")
    date: ExtractedField = Field(default_factory=ExtractedField, alias="Date")
    issued_by: ExtractedField = Field(default_factory=ExtractedField, alias="Issued By")
    subject: ExtractedField = Field(default_factory=ExtractedField, alias="Subject")
    reference_orders: List[ExtractedField] = Field(default_factory=list, alias="Reference Orders")
    reward_details: List[RewardDetail] = Field(default_factory=list, alias="Reward Details")
    reason_for_reward: ExtractedField = Field(default_factory=ExtractedField, alias="Reason for Reward")
    stamp: ExtractedField = Field(default_factory=ExtractedField, alias="Stamp")
    stamp_validation: Optional[bool] = Field(None, alias="Stamp_Validation")
    signature: ExtractedField = Field(default_factory=ExtractedField, alias="Signature")
    document_status: Literal["Valid", "Invalid"] = Field(..., description="Document validation status")


class UnitAndDistrict(BaseModel):
    unit: ExtractedField = Field(default_factory=ExtractedField)
    district: ExtractedField = Field(default_factory=ExtractedField)

class MedicalLeave(BaseModel):
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name")
    date_of_submission: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Submission")
    coy_belongs_to: ExtractedField = Field(default_factory=ExtractedField, alias="Coy Belongs to")
    rank: ExtractedField = Field(default_factory=ExtractedField, alias="Rank")
    leave_reason: ExtractedField = Field(default_factory=ExtractedField, alias="Leave Reason")
    hc_no: ExtractedField = Field(default_factory=ExtractedField, alias="HC No")
    phone_number: ExtractedField = Field(default_factory=ExtractedField, alias="Phone Number")
    unit_and_district: UnitAndDistrict = Field(default_factory=UnitAndDistrict, alias="Unit and District")
    stamp: ExtractedField = Field(default_factory=ExtractedField, alias="Stamp")
    stamp_validation: Optional[bool] = Field(None, alias="Stamp_Validation")
    signature: ExtractedField = Field(default_factory=ExtractedField, alias="Signature")
    document_status: Literal["Valid", "Invalid"] = Field(..., description="Document validation status")


class ReportingOfficer(BaseModel):
    date: ExtractedField = Field(default_factory=ExtractedField, alias="Date")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation")

class CounterSingingOfficer(BaseModel):
    date: ExtractedField = Field(default_factory=ExtractedField, alias="Date")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation")
    remarks: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks")

class HeadOfDepartmentOpinion(BaseModel):
    opinion: ExtractedField = Field(default_factory=ExtractedField, alias="Opinion")
    date: ExtractedField = Field(default_factory=ExtractedField, alias="Date")
    name: ExtractedField = Field(default_factory=ExtractedField, alias="Name")
    designation: ExtractedField = Field(default_factory=ExtractedField, alias="Designation")

class ProbationLetter(BaseModel):
    service_class_category: ExtractedField = Field(default_factory=ExtractedField, alias="Service Class Category")
    name_of_probationer: ExtractedField = Field(default_factory=ExtractedField, alias="Name of Probationer")
    date_of_regularization: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Regularization")
    period_of_probation_prescribed: ExtractedField = Field(default_factory=ExtractedField, alias="Period of Probation Prescribed")
    leave_taken_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Leave Taken During Probation")
    date_of_completion_of_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Completion of Probation")
    tests_to_passed_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Tests to be Passed During Probation")
    punishment_during_probation: ExtractedField = Field(default_factory=ExtractedField, alias="Punishment During Probation")
    pending_pr_oe: ExtractedField = Field(default_factory=ExtractedField, alias="Pending PR/OE")
    character_and_conduct: ExtractedField = Field(default_factory=ExtractedField, alias="Character and Conduct")
    firing_practice_completed: ExtractedField = Field(default_factory=ExtractedField, alias="Firing Practice Completed")
    remarks_of_ic_officer: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of I/C Officer")
    remarks_of_commandant: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of Commandant")
    remarks_of_dig: ExtractedField = Field(default_factory=ExtractedField, alias="Remarks of DIG")
    adgp_orders: ExtractedField = Field(default_factory=ExtractedField, alias="ADGP Orders")
    dob: ExtractedField = Field(default_factory=ExtractedField, alias="Date of Birth")
    salary: ExtractedField = Field(default_factory=ExtractedField, alias="Salary")
    qualification: ExtractedField = Field(default_factory=ExtractedField, alias="Qualification")
    acceptance_of_self_appraisal_report_part1: ExtractedField = Field(default_factory=ExtractedField, alias="Acceptance of Self Appraisal Report Part 1")
    assessment_of_officers_permormance_during_the_year: ExtractedField = Field(default_factory=ExtractedField, alias="Assessment of Officer's Performance During the Year")

    reporting_officer: ReportingOfficer = Field(default_factory=ReportingOfficer, alias="Reporting Officer")
    counter_singing_officer: CounterSingingOfficer = Field(default_factory=CounterSingingOfficer, alias="Counter Singing Officer")
    head_of_department_opinion: HeadOfDepartmentOpinion = Field(default_factory=HeadOfDepartmentOpinion, alias="Head of Department Opinion")

    # DIG
    stamp1: ExtractedField = Field(default_factory=ExtractedField, alias="DIG Stamp")
    stamp_validation1: Optional[bool] = Field(None, alias="DIG_Stamp_Validation")
    signature1: ExtractedField = Field(default_factory=ExtractedField, alias="DIG Signature")

    # ADGP
    stamp2: ExtractedField = Field(default_factory=ExtractedField, alias="ADGP Stamp")
    stamp_validation2: Optional[bool] = Field(None, alias="ADGP_Stamp_Validation")
    signature2: ExtractedField = Field(default_factory=ExtractedField, alias="ADGP Signature")

    # Reporting Officer
    stamp3: ExtractedField = Field(default_factory=ExtractedField, alias="Reporting Officer Stamp")
    stamp_validation3: Optional[bool] = Field(None, alias="Reporting_Officer_Stamp_Validation")
    signature3: ExtractedField = Field(default_factory=ExtractedField, alias="Reporting Officer Signature")

    # Counter Signing Officer
    stamp4: ExtractedField = Field(default_factory=ExtractedField, alias="Counter Singing Officer Stamp")
    stamp_validation4: Optional[bool] = Field(None, alias="Counter_Singing_Officer_Stamp_Validation")
    signature4: ExtractedField = Field(default_factory=ExtractedField, alias="Counter Singing Officer Signature")

    # HOD
    stamp5: ExtractedField = Field(default_factory=ExtractedField, alias="Head Of Department Stamp")
    stamp_validation5: Optional[bool] = Field(None, alias="Head_Of_department_Stamp_Validation")
    signature5: ExtractedField = Field(default_factory=ExtractedField, alias="Head Of Department Signature")

    document_status: Literal["Valid", "Invalid"] = Field(..., description="Status of the document validation")



document_models = {
    "EarnedLeaveLetter": EarnedLeaveLetter,
    "PunishmentLetter": PunishmentLetter,
    "RewardLetter": RewardLetter,
    "MedicalLeave": MedicalLeave,
    "ProbationLetter": ProbationLetter
}