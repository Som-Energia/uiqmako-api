import pytest
from .erp_test import ERPTest
from uiqmako_api.utils.edits import *
from uiqmako_api.schemas.edits import *
from uiqmako_api.models.users import get_user
from uiqmako_api.utils.git import setup_template_repository


ERP = ERPTest()
GIT = setup_template_repository()


@pytest.mark.asyncio
class TestEdits:

    async def test_get_or_create_template_edit_existing(self):
        template_id = 1
        user = await get_user('UserAll')
        edit, created = await get_or_create_template_edit(template_id, user)
        assert not created
        assert edit.user_id == user.id

    @pytest.mark.parametrize("user_id,expected_len", [
        (1, 0),
        (2, 1),
    ])
    async def test_check_other_users_edits(self, user_id, expected_len):
        result = await check_other_users_edits(template_id=1, user_id=user_id)
        assert len(result) == expected_len

    async def test_save_user_edit(self):
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

    async def test_save_user_edit_by_type(self):
        edit = RawEdit(
            def_body_text='',
            headers="{'def_subject':'new_subject'}",
            by_type='[["html", "New text"]]'
        )

        result = await save_user_edit(template_id=1, user_id=1, edit=edit)
        assert result
        current_edit = await get_edit_orm(1)
        assert current_edit.body_text == 'New text\n\n'
        assert current_edit.headers == "{'def_subject':'new_subject'}"

    async def test_delete_user_edit(self):
        pre_result = await check_other_users_edits(template_id=1, user_id=2)
        assert len(pre_result) == 1
        await delete_user_edit(template_id=1, user_id=1)

        post_result = await check_other_users_edits(template_id=1, user_id=2)

        assert post_result == []

    async def test_delete_edit(self):
        template_id = 1
        user = await get_user('UserAll')
        edit, created = await get_or_create_template_edit(template_id, user)
        assert created
        assert edit.user_id == user.id

        result = await delete_edit(edit_id=edit.id)
        assert result == 1
        post_result = await get_edit_orm(edit_id=edit.id)
        assert not post_result
