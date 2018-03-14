from pymongo import MongoClient
import random


client = MongoClient()
db = client.test_db
COLLECTION = db.test_collection


def add_records(collection):
    data_arr = []
    for i in range(100000):
        data_arr.append({
            'num': float(random.randint(0, 10000)) / 100.0,
            'txt': random.choice(['easy', 'medium', 'hard'])
        })

    print(collection.insert_many(data_arr).inserted_ids)

def get_random_records_num():
    sample = {"$sample": {"size": 50}}
    match = {"$match": {"num": {"$gt": 33.33,
                                 "$lt": 66.66}}}
    return COLLECTION.aggregate([match, sample])

def get_random_records_txt():
    sample = {"$sample": {"size": 50}}
    match = {"$match": {"txt": "easy"}}
    return COLLECTION.aggregate([match, sample])


if __name__ == '__main__':
    # add_records(COLLECTION)

    import timeit
    n=10
    print('number match', timeit.timeit("get_random_records_num()", setup="from __main__ import get_random_records_num", number=n)/ n)
    print('text match', timeit.timeit("get_random_records_txt()", setup="from __main__ import get_random_records_txt", number=n)/ n)
    # [print(s) for s in get_random_records_txt()]


