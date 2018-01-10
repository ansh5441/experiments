import motor.motor_asyncio
import asyncio
import pprint
client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.test_database
collection = db.test_collection


# async def do_insert():
#     document = {'key': 'value'}
#     result = await db.test_collection.insert_one(document)
#     print('result %s' % repr(result.inserted_id))

# loop = asyncio.get_event_loop()
# loop.run_until_complete(do_insert())


# async def do_insert():
#     for i in range(200):
#         result = await db.test_collection.insert_one({'i': i})
#         print (result)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(do_insert())


# async def do_find_one():
#     document = await db.test_collection.find_one({'i': {'$lt': 1}})
#     pprint.pprint(document)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(do_find_one())






async def do_find():
    cursor = db.test_collection.find({'i': {'$lt': 1000}}).sort('i')
    for document in await cursor.to_list(length=1000):
        pprint.pprint(document)

loop = asyncio.get_event_loop()
loop.run_until_complete(do_find())








