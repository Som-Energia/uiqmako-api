from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional


def validate_xml_id(value: str):
    if not value:
        return value
    if '.' not in value:
        raise ValueError("XML ID must contain module and id separeted by '.'")
    module, name = value.split('.')
    if not name:
        raise ValueError("XML ID name cannot be empty")
    if not module:
        raise ValueError("XML ID module cannot be empty")
    return value


class TemplateInfoBase(BaseModel):
    id: int
    name: str
    model: str
    xml_id: Optional[str] = None
    erp_id: Optional[int] = None
    last_updated: Optional[datetime] = None

    @validator('xml_id')
    def validate_xml_id(cls, v):
        return validate_xml_id(v)

    class Config:
        orm_mode = True


class CaseBase(BaseModel):
    name: str
    case_xml_id: Optional[str] = None
    case_id: Optional[int] = None

    @validator('case_xml_id')
    def validate_xml_id(cls, v):
        return validate_xml_id(v)

    class Config:
        orm_mode = True


class Template(BaseModel):
    id: int
    def_subject: str
    def_subject: str
    def_body_text: str
    def_to: str
    def_cc: str
    def_bcc: str
    model_int_name: str
    lang: str
    name: str
    #xml_id: str

    class Config:
        orm_mode = True


class Case(CaseBase):
    pass

