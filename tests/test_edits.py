import pytest
from .erp_test import ERPTest
from uiqmako_api.utils.edits import *
from uiqmako_api.schemas.edits import *
from uiqmako_api.models.users import get_user
from uiqmako_api.errors.exceptions import OutdatedEdit
from uiqmako_api.models.templates import TemplateInfoModel

@pytest.mark.asyncio
class TestEdits:

    async def test_get_or_create_template_edit_existing(self, test_app):
        template_id = 1
        user = await get_user('UserAll')
        edit, created = await get_or_create_template_edit(template_id, user)
        assert not created
        assert edit.user_id == user.id

    @pytest.mark.parametrize("user_id,expected_len", [
        (1, 0),
        (2, 1),
    ])
    async def test_check_other_users_edits(self, user_id, expected_len, test_app):
        result = await check_other_users_edits(template_id=1, user_id=user_id)
        assert len(result) == expected_len

    async def test_save_user_edit(self, test_app):
        edit = RawEdit(
            def_body_text='New text',
            headers="{'def_subject':'new_subject'}",
            by_type='[]'
        )
        result = await save_user_edit(template_id=1, user_id=1, edit=edit)
        assert result
        current_edit = await get_edit_orm(1)
        assert current_edit.body_text == 'New text'
        assert current_edit.headers == "{'def_subject':'new_subject'}"

    async def test_transfer_edit(self, test_app):
        new_user = await get_user('UserBasic')
        old_user = await get_user('UserAll')
        edit = TemplateEditUpdate(
            user_id = new_user.id,
        )
        current_edit = await get_edit_orm(1)
        assert current_edit.user_id == old_user.id
        result = await transfer_user_edit(template_id=1, edit=edit)
        assert result
        transfered_edit = await get_edit_orm(1)
        assert transfered_edit.user_id == new_user.id

    async def test_transfer_edit__invalid_user(self, test_app):
        new_user = await get_user('UserBasic')
        old_user = await get_user('UserAll')
        edit = TemplateEditUpdate(
            user_id = 10,
        )
        current_edit = await get_edit_orm(1)
        assert current_edit.user_id == old_user.id
        result = await transfer_user_edit(template_id=1, edit=edit)
        assert result
        transfered_edit = await get_edit_orm(1)
        assert transfered_edit.user_id == old_user.id

    async def test_save_user_edit_by_type(self, test_app):
        edit = RawEdit(
            def_body_text='',
            headers="{'def_subject':'new_subject'}",
            by_type='[["html", "New text"]]'
        )

        result = await save_user_edit(template_id=1, user_id=1, edit=edit)
        assert result
        current_edit = await get_edit_orm(1)
        assert current_edit.body_text == 'New text\n'
        assert current_edit.headers == "{'def_subject':'new_subject'}"

    async def test_delete_user_edit(self, test_app):
        pre_result = await check_other_users_edits(template_id=1, user_id=2)
        assert len(pre_result) == 1
        await delete_user_edit(template_id=1, user_id=1)

        post_result = await check_other_users_edits(template_id=1, user_id=2)

        assert post_result == []

    async def test_delete_edit(self, test_app):
        template_id = 1
        user = await get_user('UserAll')
        edit, created = await get_or_create_template_edit(template_id, user)
        result = await delete_edit(edit_id=edit.id)
        assert result == 1
        post_result = await get_edit_orm(edit_id=edit.id)
        assert not post_result

    async def test_upload_edit(self, test_app):
        template_id = 2 # with no edits yet
        user = await get_user('UserAll')
        edit, created = await get_or_create_template_edit(template_id, user)
        assert created # Yep, with no edits yet
        edit = RawEdit(
            def_body_text='',
            headers='{"def_subject":"new_subject"}',
            by_type='[["html", "New text"]]'
        )
        edit_id = await save_user_edit(
            template_id=template_id,
            user_id=user.id,
            edit=edit,
        )

        await upload_edit(test_app.ERP, edit_id=edit_id)

        template_info = await test_app.db_manager.get(TemplateInfoModel, id=template_id)
        template = await test_app.ERP.service().load_template(template_info.xml_id)
        assert template.def_subject == "new_subject"

    async def test_upload_edit__when_outdated(self, test_app):
        template_id = 1
        user = await get_user('UserAll')
        edit = RawEdit(
            def_body_text='',
            headers='{"def_subject":"new_subject"}',
            by_type='[["html", "New text"]]'
        )

        result = await save_user_edit(template_id=template_id, user_id=user.id, edit=edit)
        edit = RawEdit(
            def_body_text='New text',
            headers="{'def_subject':'new_subject'}",
            by_type='[]'
        )

        edit_id = await save_user_edit(
            template_id=template_id,
            user_id=user.id,
            edit=edit,
        )
        with pytest.raises(OutdatedEdit):
            await upload_edit(test_app.ERP, edit_id=edit_id)

