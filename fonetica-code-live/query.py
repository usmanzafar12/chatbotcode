import psycopg2


fetch_latest = "SELECT * FROM response8 WHERE response8.facebookId = %s \
                ORDER BY response8.id DESC LIMIT 2"

insert_query =  "INSERT INTO response8 (inputFlag,apiFlag, \
                googleTranslateFlag,timeStampMessage,facebookId, \
                message_id, inputMessage, translatedMessage, \
                apiResponse,userOption, normalizedmessage) VALUES \
                ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

update_query = "UPDATE response8 SET inputFlag=(%s),apiFlag=(%s), \
                googleTranslateFlag=(%s),inputMessage=(%s), \
                translatedMessage=(%s),apiResponse=(%s), \
                message_id=(%s) WHERE message_id=(%s)"

update_query_translation = "UPDATE response8 SET  \
                translatedMessage=(%s) WHERE message_id=(%s)"

update_query_apiai = "UPDATE response8 SET  \
                apiResponse=(%s) WHERE message_id=(%s)"

delete_query = "UPDATE response8 SET inputFlag=(%s),apiFlag=(%s), \
               googleTranslateFlag=(%s),inputMessage=(%s), \
               translatedMessage=(%s),apiResponse=(%s),message_id=(%s) \
               WHERE message_id=(%s)"

update_query_normalization = "UPDATE response8 SET  \
                normalizedmessage=(%s) WHERE message_id=(%s)"


def query(sql=None, values=None, insert=False):
    conn = psycopg2.connect(database="postgres", user="postgres", password="usman",\
                            host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    temp = conn.close()
    return temp
