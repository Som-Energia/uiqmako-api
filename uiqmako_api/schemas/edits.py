from bs4 import BeautifulSoup
from datetime import datetime
import json
from pydantic import BaseModel
from uiqmako_api.schemas.users import User
from uiqmako_api.schemas.templates import TemplateInfoBase

class TemplateEditInfo(BaseModel):
    template_id: int
    user_id: int
    date_start: datetime = None

    class Config:
        orm_mode = True

class TemplateEditUser(TemplateEditInfo):
    user: User
    template: TemplateInfoBase

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
                full_text += text + '\n'
            self.def_body_text = full_text
