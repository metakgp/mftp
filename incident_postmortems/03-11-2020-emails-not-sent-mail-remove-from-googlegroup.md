## The Issue

In the process of removing alums and suspicious accounts, the email ID, "no-reply@mftp.herokuapp.com`, was removed from the list of members and hence managers. Due to this, the script was successfully sending all emails without error though Google group was rejecting as it was from an "outsider". So, all in all, no new notices were posted for the day of November 3, 2020.

## How Did We Diagnose It?

1. Ran the script locally with custom environment to ensure that every step was working properly. :heavy_check_mark:  Done by @iakshat
2. Ran the script locally with the same environment variables as the heroku machine - no exceptions raised. :heavy_check_mark:  Done by @iakshat
3. Accessed the mLab instance with mongo shell and check the last 20 notices in reverse order using the following command and it had the latest one from CDC notice board. :heavy_check_mark:
```
shell> mongo $MONGODB_URI
mongo> use CLIENT_STRING_FROM_END_OF_URI
mongo> db.notices.find().sort({$natural: -1}).limit(11)
```
4. @iakshat suggested that it seems the member may not have permission as mailtrack was able to send the mails successfully. I checked for the presence of no-reply@mftp.herokuapp.com and it was not there. I confirmed the settings and only managers had the permission to post. So, @iakshat had pin pointed the error :fire:

## The Fix

1. Confirm with @Ishita Lade and she was kind enough to convey all the information. It was confirmed that all but emails given to her by @kaustubh were removed.
2. Added back no-reply@mftp.herokuapp.com and @Ishita Lade confirmed that she will not remove managers from now on - irrespective of their year of study.
3. Removed the last 11 notices (which had not been sent) from the mongo DB using the following commands in mongo shell with previous connection:
```
mongo> toremove = db.notices.find().sort({$natural: -1}).limit(11).toArray().map(function(doc) {return doc._id})
mongo> db.notices.remove({_id: {$in: toremove}})
```
4. Triggered the MFTP script and sent the mail.