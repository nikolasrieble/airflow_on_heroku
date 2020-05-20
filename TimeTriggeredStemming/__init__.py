import datetime
import logging
import pymongo

import azure.functions as func

def get_connection():
    try: 
        from utils.conn_str import conn_str
        return conn_str
    except: 
        import os
        return os.environ.get('MONGO_DB')

def extract_words(article):
    # TODO : Implement nlp logic here
    return None

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    myclient = pymongo.MongoClient(get_connection())
    mydb = myclient['newspaper']

    for name in mydb.collection_names():
        logging.info('now checking collection %s', name)
        collection = mydb[name]

        # get all collection for which a statistic has not been computed
        cursor = collection.find({"unique_words": None})
        for article in cursor:
            
            unique_words = None #extract_words(article["text"])

            collection.update_one(
                {"url" :article["url"]}, # update the document identified by the given url
                {"unique_words": unique_words}) # with the list of unique words
            

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
