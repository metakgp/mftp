from pymongo import MongoClient
from pymongo import errors
from os import environ as env
import bson
from bson.json_util import dumps, loads

def export_db():
    '''
        Tries to Exports the whole Database (each and every notice)
        Saves notices already in target Database in repeated_notices.bson
        Saves notices failed to be inserted in defaulters.bson

        Can be run multiple times with no fear of multiple entries in case of any confusion
    '''
    print("connecting to mlab DB")
    mc_mlab = MongoClient(env['MONGODB_URI'])
    print("collecting notices cursor from MLab")
    notices_cursor = mc_mlab.get_default_database().notices.find()
    print("connecting to atlas DB")
    mc_atlas = MongoClient(env['MONGODB_URI_ATLAS'])
    print("connected to atlas DB")

    defaulters = []
    repeated_notices = []
    for notice in notices_cursor:
        try:
            mc_atlas.get_default_database().notices.insert(notice)
            print("inserted notice: ", notice)
        except errors.DuplicateKeyError:
            print("entry already in database")
            repeated_notices.append(notice)
        except Exception as ex:
            print("error in inserting: ", ex)
            defaulters.append(notice)

    if(len(defaulters)):
        print("Defaulters Present!!!")

    print(repeated_notices)
    print(type(repeated_notices[0]['_id']), (repeated_notices[0]['_id']))

    print("Saving defaulters and repeated notices...")
    open("defaulters.bson", "w").write(dumps(defaulters))
    open("repeated_notices.bson","w").write(dumps(repeated_notices))

    print("Export Complete!")
    mc_mlab.close()
    mc_atlas.close()

def insert_notice(notice, mc_atlas):
    '''
        Tries to insert a notice in default database of MongoClient passed as second argument
        Returns 0 if insert successful
        Returns 2 if entry already in database
        Returns 1 if some other error occurs
    '''
    try:
        mc_atlas.get_default_database().notices.insert(notice)
        print("inserted specific notice: ", notice)
        return 0
    except errors.DuplicateKeyError:
        print("specific entry already in database")
        return 2
    except errors.ConnectionFailure:
        print("Error while connecting to DB")
        return 1
    except Exception as ex:
        print("error in specific inserting: ", ex)
        return 1

def insert_from_file(filename, further_defaulter_filename = "further_defaulters.bson", further_repeated_filename = "further_repeated.bson"):
    '''
        Reads a bson file with name 'filename' and tries to insert each notice in the bson to the target Database

        If a notice fails to be inserted it is pushed to further_defaulters and finally saved in file with filename 'further_defaulter_filename'
        If a notice already exists in target database, it is pushed to 'further_repeated_filename'
    '''
    mc_atlas = MongoClient(env['MONGODB_URI_ATLAS'])
    print("connected to atlas DB")

    notices = loads(open(filename, "r").read())
    print("Notice count: {}".format(len(notices)))
    further_defaulters = []
    further_repeated = []
    for notice in notices:
        out = insert_notice(notice, mc_atlas)
        if(out == 1):
            further_defaulters.append(notice);
        elif(out == 2):
            further_repeated.append(notice)

    print("Further defaulters count: {}".format(len(further_defaulters)))
    print("Further repeated count: {}".format(len(further_repeated)))

    print("Saving further defaulters to {}".format(further_defaulter_filename))
    open(further_defaulter_filename, "w").write(dumps(further_defaulters))

    print("Saving further repeated to {}".format(further_repeated_filename))
    open(further_repeated_filename, "w").write(dumps(further_repeated))

    print("Attempt to insert from file: {} complete".format(filename))