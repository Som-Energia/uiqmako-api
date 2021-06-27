from datetime import datetime
from pydantic import BaseModel, validator, Field
from typing import Optional
from bs4 import BeautifulSoup
import json

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
    id: int
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

    def __init__(self):
        super().__init__()
        self.def_body_text.strip()

    def headers(self):
        return {'def_subject': self.def_subject, 'def_to': self.def_to,
                'def_bcc': self.def_bcc, 'def_cc': self.def_cc,
                'lang': self.lang
                }

    def meta_data(self):
        return {'name': self.name, 'model_int_name': self.model_int_name, 'id': self.id}

    def body_text(self):
        from .templates import parse_body_by_language

        return {'def_body_text': self.def_body_text,
                'by_type': parse_body_by_language(self.def_body_text)}

    def __getitem__(self, key):
        return getattr(self, key)

class Case(CaseBase):
    pass


class TemplateEditInfo(BaseModel):
    from .registration.schemas import User
    template_id: int
    user_id: int
    date_start: datetime = None

    class Config:
        orm_mode = True


class TemplateEdit(TemplateEditInfo):

    body_text: str = None
    headers: str = None
    original_update_date: datetime
    class Config:
        orm_mode = True


class RawEdit(BaseModel):
    by_type: str = None
    def_body_text: str = None
    headers: str = None

    def __init__(self, by_type, def_body_text, headers):
        super(RawEdit, self).__init__()

        self.by_type = json.loads(by_type)
        self.headers = headers
        self.def_body_text = def_body_text
        self.compose_text_types()

    def compose_text_types(self):
        if self.by_type:
            full_text = ''
            for type, text in self.by_type:
                #if type == 'html':
                #    text = BeautifulSoup(text, "html.parser").prettify(formatter=None)
                full_text += text + '\n'
            self.def_body_text = full_text