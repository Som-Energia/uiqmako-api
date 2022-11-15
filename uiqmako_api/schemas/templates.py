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
    """
    Local database stored information to refer a ERP template
    """
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
    """
    Test Case for a template
    """
    id: int
    name: str
    case_xml_id: Optional[str] = None
    case_erp_id: Optional[int] = None
    template_id: int

    @validator('case_xml_id')
    def validate_xml_id(cls, v):
        return validate_xml_id(v)

    class Config:
        orm_mode = True


class Template(BaseModel):
    """
    Editable ERP Template content
    """
    id: int
    def_subject: str
    def_subject_es_ES: str
    def_subject_ca_ES: str
    def_body_text: str
    def_to: str
    def_cc: str
    def_bcc: str
    model_int_name: str
    lang: str
    name: str

    class Config:
        orm_mode = True

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.def_body_text.strip()

    def headers(self):
        return {
            'def_subject': self.def_subject,
            'def_to': self.def_to,
            'def_bcc': self.def_bcc,
            'def_cc': self.def_cc,
            'lang': self.lang,
            'def_subject_es_ES': self.def_subject_es_ES,
            'def_subject_ca_ES': self.def_subject_ca_ES,
        }

    def meta_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'model_int_name': self.model_int_name,
        }

    def body_text(self):
        from uiqmako_api.utils.templates import parse_body_by_language

        return {
            'def_body_text': self.def_body_text,
            'by_type': parse_body_by_language(self.def_body_text,
        )}

    def __getitem__(self, key):
        return getattr(self, key)

class TemplateRejects(BaseModel):
    """
    Editable ERP Template content
    """
    id: int
    notify_text: str
    info_rebuig: str
    name: str
    model_int_name: str
    def_body_text: str

    class Config:
        orm_mode = True

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.notify_text.strip()

    def headers(self):
        return {
        }

    def meta_data(self):
        return {
            'id': self.id,
            'name': self.info_rebuig,
        }

    def body_text(self):
        from uiqmako_api.utils.templates import parse_body_by_language

        return {
            'def_body_text': self.notify_text,
            'by_type': parse_body_by_language(self.notify_text,
        )}

    def __getitem__(self, key):
        return getattr(self, key)


class SourceInfo(BaseModel):
    """
    ERP server instance to fetch and push data
    """
    name: str
    uri: str = None
