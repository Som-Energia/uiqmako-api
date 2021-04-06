import asyncio
import peewee
import peewee_async
import config

database = peewee_async.PostgresqlDatabase(
    database=config.settings.DB_NAME,
)

def get_db_manager():
    objects = peewee_async.Manager(database)
    database.set_allow_sync(False)
    return objects

class TemplateInfoModel(peewee.Model):
    name = peewee.CharField(unique=True)
    model = peewee.CharField()
    xml_id = peewee.CharField(null=True, unique=True)
    template_id = peewee.IntegerField(null=True, unique=True)
    class Meta:
        database = database
        table_name = "template_info"

class CaseModel(peewee.Model):
    name = peewee.CharField()
    case_id = peewee.IntegerField(null=True)
    case_xml_id = peewee.CharField(null=True)
    class Meta:
        database = database
        table_name = "case_info"

# Look, sync code is working!

def setup_database():
    TemplateInfoModel.create_table(True)
    CaseModel.create_table(True)
    database.close()


# loop = asyncio.get_event_loop()
# #loop.run_until_complete(handler())
# loop.close()

# Clean up, can do it sync again:
# with objects.allow_sync():
#     time.sleep(500)
#     TestModel.drop_table(True)
