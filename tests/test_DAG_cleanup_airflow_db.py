from unittest import TestCase

import mongomock as mongomock


class Test(TestCase):
    def test_MockMongo(self):

        def increase_votes(collection):
            collection.update_many({}, {'$inc': {'votes': 1}})

        collection = mongomock.MongoClient().db.collection
        objects = [dict(votes=1), dict(votes=2)]
        for obj in objects:
            obj['_id'] = collection.insert_one(obj).inserted_id
        increase_votes(collection)
        for obj in objects:
            stored_obj = collection.find_one({'_id': obj['_id']})
            stored_obj['votes'] -= 1
            assert stored_obj == obj  # by comparing all fields we make sure only votes changed
