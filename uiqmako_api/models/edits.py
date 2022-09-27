from datetime import datetime
import peewee
from . import database, get_db_manager
from .users import UserModel
from .templates import TemplateInfoModel
from uiqmako_api.schemas.edits import TemplateEditInfo, TemplateEditUser

db = get_db_manager()


class TemplateEditModel(peewee.Model):
    id = peewee.AutoField()
    template = peewee.ForeignKeyField(TemplateInfoModel, backref="edits")
    user = peewee.ForeignKeyField(UserModel, backref="edits")
    body_text = peewee.TextField(null=True)
    headers = peewee.TextField(null=True)
    date_start = peewee.DateTimeField(null=True)
    last_modified = peewee.DateTimeField(null=True)
    original_update_date = peewee.DateTimeField()

    class Meta:
        database = database
        table_name = "template_edit"


async def get_or_create_template_edit_orm(template_id, user_id, last_updated):
    try:
        edit = await db.get(
            TemplateEditModel, template=template_id, user=user_id
        )
        created = False
    except peewee.DoesNotExist as ex:
        edit, created = await db.create_or_get(
            TemplateEditModel,
            template=template_id,
            user=user_id,
            original_update_date=last_updated,
            date_start=datetime.now(),
        )
    return edit, created


async def get_user_edits_info_orm(template_id, exclude_user):
    try:
        edits = await db.execute(
            TemplateEditModel.select(TemplateEditModel, UserModel).where(
                TemplateEditModel.user != exclude_user,
                TemplateEditModel.template_id == template_id
            ).join(UserModel, on=(UserModel.id == TemplateEditModel.user))
        )
        result = [TemplateEditUser.from_orm(e) for e in edits]
        return result
    except peewee.DoesNotExist as e:
        return []


async def update_user_edit_orm(template_id, user_id, text, headers):
    edit = await db.get(TemplateEditModel, template=template_id, user=user_id)
    edit.body_text = text
    edit.headers = headers
    edit.last_modified = datetime.now()
    await db.update(edit)
    return edit.id


async def transfer_user_edit_orm(template_id, new_user_id):
    edit = await db.get(TemplateEditModel, template=template_id)
    edit.user = new_user_id
    await db.update(edit)
    return edit.user.id


async def delete_user_edit_orm(template_id, user_id):
    edit = await db.get(TemplateEditModel, template=template_id, user=user_id)
    return await delete_edit_orm(edit.id)


async def get_edit_orm(edit_id):
    edit = await db.execute(
        TemplateEditModel.select(TemplateEditModel, TemplateInfoModel).where(
            TemplateEditModel.id == edit_id
        ).join(TemplateInfoModel, on=(TemplateInfoModel.id == TemplateEditModel.template)))
    instances = [e for e in edit]
    return instances[0] if instances else False

async def delete_edit_orm(edit_id):
    edit = await get_edit_orm(edit_id)
    return await db.delete(edit)

async def get_all_edits_orm():
    try:
        edits = await db.execute(
            TemplateEditModel
            .select(TemplateEditModel, UserModel, TemplateInfoModel)
            .join(TemplateInfoModel, on=(TemplateEditModel.template == TemplateInfoModel.id))
            .join(UserModel, on=(TemplateEditModel.user == UserModel.id))
        )
        result = [TemplateEditUser.from_orm(e) for e in edits]
        return result
    except peewee.DoesNotExist as e:
        return []
