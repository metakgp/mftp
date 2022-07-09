#import sys
import argparse
#import bson
from pymongo import errors
#from os import environ as env
from pymongo import MongoClient
from bson.json_util import dumps, loads 

old_mongodb_uri = ""
new_mongodb_uri = ""

def export_db():
    '''
        Tries to Exports the whole Database (each and every notice)
        Saves notices already in target Database in repeated_notices.bson
        Saves notices failed to be inserted in defaulters.bson

        Can be run multiple times with no fear of multiple entries in case of any confusion
    '''
    print("connecting to old DB")
    mc_old = MongoClient(old_mongodb_uri)
    print("collecting notices cursor from old database")
    notices_cursor = mc_old.get_default_database().notices.find()
    print("connecting to new DB")
    mc_new = MongoClient(new_mongodb_uri)
    print("connected to new DB")

    defaulters = []
    repeated_notices = []
    for notice in notices_cursor:
        try:
            mc_new.get_default_database().notices.insert_one(notice)
            print("inserted notice: ", notice)
        except errors.DuplicateKeyError:
            print("entry already in database")
            repeated_notices.append(notice)
        except Exception as ex:
            print("error in inserting: ", ex)
            defaulters.append(notice)

    if(len(defaulters)):
        print("\nDefaulters Present!!!")
    else:
        print("\nYohoo!! No Defaulters")


    if (defaulters):
        print("Saving defaulters...")
        with open("defaulters.bson", "w") as f:
            f.write(dumps(defaulters))
    if (repeated_notices):
        print("Saving repeaters...")
        with open("repeated_notices.bson","w") as f:
            f.write(dumps(repeated_notices))

    print("Export Complete!")
    mc_old.close()
    mc_new.close()

def insert_notice(notice, mc_new):
    '''
        Tries to insert a notice in default database of MongoClient passed as second argument
        Returns 0 if insert successful
        Returns 2 if entry already in database
        Returns 1 if some other error occurs
    '''
    try:
        mc_new.get_default_database().notices.insert_one(notice)
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

def insert_from_file(filename):
    '''
        Reads a bson file with name 'filename' and tries to insert each notice in the bson to the target Database

        If a notice fails to be inserted it is pushed to further_defaulters and finally saved in file with filename 'further_defaulter_filename'
        If a notice already exists in target database, it is pushed to 'further_repeated_filename'
    '''
    further_defaulter_filename = "further_defaulters.bson"
    further_repeated_filename = "further_repeated.bson"

    mc_new = MongoClient(new_mongodb_uri)
    print("connected to new DB")

    further_defaulters = []
    further_repeated = []
    with open(filename, "r") as f:
        notices = loads(f.read())
        print("Notice count: {}".format(len(notices)))
        for notice in notices:
            out = insert_notice(notice, mc_new)
            if(out == 1):
                further_defaulters.append(notice)
            elif(out == 2):
                further_repeated.append(notice)

    print("Further defaulters count: {}".format(len(further_defaulters)))
    print("Further repeated count: {}".format(len(further_repeated)))

    print("Saving further defaulters to {}".format(further_defaulter_filename))
    with open(further_defaulter_filename, "w") as f:
        f.write(dumps(further_defaulters))

    print("Saving further repeated to {}".format(further_repeated_filename))
    with open(further_repeated_filename, "w") as f:
        f.write(dumps(further_repeated))

    print("Attempt to insert from file: {} complete".format(filename))

def start_database_export():
    '''
        Script for exporting database
        Using OLD_MONGODB_URI in env to act as original database
        Add NEW_MONGODB_URI in env to act as target database
    '''
    export_db()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database Export Script")
    parser.add_argument('--target', '-t', dest="new_mongodb_uri", help="URI for target database", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source', '-s', dest="old_mongodb_uri", help="URI for source database")
    group.add_argument('--try-defaulters', '-d', dest="defaulter_filename", help="bson file with defaulters dump to upload")

    args = parser.parse_args()

    old_mongodb_uri = args.old_mongodb_uri
    new_mongodb_uri = args.new_mongodb_uri

    if(args.defaulter_filename):
        print("Defaulter File: {}".format(args.defaulter_filename))
        print("Target DB: {}".format(new_mongodb_uri))
        insert_from_file(args.defaulter_filename)
    else:
        print("Source DB: {}".format(old_mongodb_uri))
        print("Target DB: {}".format(new_mongodb_uri))
        start_database_export()