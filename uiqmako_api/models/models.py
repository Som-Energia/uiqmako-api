import asyncio
import peewee
import peewee_async
import config
from . import database

class TemplateInfoModel(peewee.Model):
    id = peewee.AutoField()
    name = peewee.CharField(unique=True)
    model = peewee.CharField()
    xml_id = peewee.CharField(null=True, unique=True)
    erp_id = peewee.IntegerField(null=True, unique=True)
    class Meta:
        database = database
        table_name = "template_info"

class CaseModel(peewee.Model):
    id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    case_id = peewee.IntegerField(null=True)
    case_xml_id = peewee.CharField(null=True)
    class Meta:
        database = database
        table_name = "case_info"

# Look, sync code is working!

# def setup_database():
#     TemplateInfoModel.create_table(True)
#     CaseModel.create_table(True)
#     database.close()


# loop = asyncio.get_event_loop()
# #loop.run_until_complete(handler())
# loop.close()

# Clean up, can do it sync again:
# with objects.allow_sync():
#     time.sleep(500)
#     TestModel.drop_table(True)
