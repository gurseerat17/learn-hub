import re
import bson
from bson.objectid import ObjectId
from flask.globals import session
from learnHub import mongo, study_room
from profanity_check import predict_prob
from datetime import datetime
from dateutil import parser

def addCourseForStudent(user_email, course_code, enrollment_key):

    course = getCourseDetails(course_code)
    student = getStudentDetails(user_email)

    if enrollment_key != course["enrollment_key"]:
        return False

    student['courses'].append(course_code)   
    course['id_students'].append(student['email'])
    course_no_of_students = course['no_of_students'] + 1
    
    mongo.db.courses.update_one({"course_code":course_code}, {"$set":{"no_of_students":course_no_of_students,
                                 "id_students":course['id_students']}})
    
    mongo.db.students.update_one({"email":user_email},{"$set":{"courses":student['courses']}})

    return True

def addNewStudent(email, password, first_name, last_name):
    mongo.db.students.insert({
        "first_name" : first_name,
        "last_name"  : last_name,
        "email"      : email,
        "password"   : password,
        "courses" : [],
        "status"     : "offline"  
    })

def addQuestionToStudyRoomDiscussion(course_code, question, question_by):
        
    new_question = {
        "question_id" : str(bson.objectid.ObjectId()),
        "question" : question,
        "question_by" : {
            "email": question_by["email"],
            "name" : question_by["first_name"] + " " + question_by["last_name"],
        },
        "replies" : []
    }

    chat = getStudyRoomChat(course_code)
    chat.append(new_question)
    
    updateStudyRoomChat(course_code, chat)
    
    return new_question["question_id"]

def addReplyToStudyRoomDiscussion(course_code, question_id, reply, replied_by):
    
    chat = getStudyRoomChat(course_code)

    discussion_idx = next((i for i, discussion in enumerate(chat) if discussion["question_id"] == question_id), None)    
    discussion = chat[discussion_idx]

    new_reply = {
        "reply_id" : str(bson.objectid.ObjectId()),
        "reply" : reply,
        "replied_by" : {
            "email": replied_by["email"],
            "name" : replied_by["first_name"] + " " + replied_by["last_name"],
        },
        "upvotes" : 0,
        "upvoted_by" : []
    }

    discussion["replies"].append(new_reply)
    chat[discussion_idx] = discussion

    updateStudyRoomChat(course_code, chat)

    return new_reply["reply_id"]

def addCommentToCourseAnnouncements(course_code, announcement_id, comment, comment_by):
     
    mongo.db.courseannouncements.update_one({
        "course_code": course_code ,
        "announcements.announcement_id": announcement_id 
        }, { 
        "$push": { "announcements.$.comments": { 
            "comment_id" : str(bson.objectid.ObjectId()),
            "comment" : comment,
            "comment_by" : {
                "email": comment_by["email"],
                "name": comment_by["first_name"] +" "+comment_by["last_name"]
            }
            } 
        }
    }, upsert=True)

def getStudentInStudyRoom(course_code, user_email):
    course_students = mongo.db.studyrooms.find_one({
        "course_code": course_code,
    })["students"]

    return next((student for student in course_students if student["email"] == user_email), None)

def getStudyRoomStudentBlockedList(course_code, user_email):
    
    user = getStudentInStudyRoom(course_code, user_email)

    user_block_list = []
    if user.get("blocked") is not None:
        user_block_list = user["blocked"]

    return user_block_list

def blockStudentInStudyRoom(user_email, user_to_block, course_code):

    user_to_block_name = user_to_block["first_name"] +" "+ user_to_block["last_name"]
    
    user_block_list = getStudyRoomStudentBlockedList(course_code, user_email)
    
    if user_to_block["email"] in user_block_list:
        return user_to_block_name + " has already been blocked for you"
    
    user_block_list.append(user_to_block["email"])

    mongo.db.studyrooms.update_one({
        "course_code": course_code ,
        "students.email": user_email 
        }, { 
        "$set": { 
        "students.$.blocked": user_block_list
        } 
    }, upsert=True)

    return "Successfully blocked " + user_to_block_name

def unblockStudentInStudyRoom(user_email, user_to_unblock, course_code):

    user_to_unblock_name = user_to_unblock["first_name"] +" "+ user_to_unblock["last_name"]

    user_block_list = getStudyRoomStudentBlockedList(course_code, user_email)

    if user_to_unblock["email"] not in user_block_list:
        return user_to_unblock_name + " was not blocked"
    
    user_block_list.remove(user_to_unblock["email"])

    mongo.db.studyrooms.update_many({
        "course_code": course_code ,
        "students.email": user_email }, { 
        "$set": { 
        "students.$.blocked": user_block_list     
            } 
        }, 
        upsert=True
    )

    return "Successfully unblocked " + user_to_unblock_name

def reportStudentInStudyRoom(course_code, user_to_report_email, reported_by_email):
    
    user_to_report_name = getStudentDetails(user_to_report_email)["first_name"] +" "+ \
                          getStudentDetails(user_to_report_email)["last_name"]
    spam_reports_by = getStudentInStudyRoom(course_code, user_to_report_email).get("spam_reports_by")
    
    spam_reports = 0
    if spam_reports_by is not None:
        spam_reports = len(spam_reports_by) 
        
        if reported_by_email in spam_reports_by:
            return None, "You have already reported "+user_to_report_name, False

    mongo.db.studyrooms.update_one({
        "course_code": course_code ,
        "students.email": user_to_report_email }, { 
        "$push": { "students.$.spam_reports_by" : reported_by_email
            } 
        }, 
        upsert=True
    )

    spam_reports = spam_reports + 1
    total_students = len(getStudentsInStudyRoom(course_code))
    
    reported_message = user_to_report_name + " has been reported for spamming"
    
    if spam_reports == 1 :
        return "Some of your coursemates have reported against you. You are requested not to disturb \
                fellow learners by spamming on this platform. ", reported_message , False

    block_message = "You have been blocked out of the study room for the next 12 hours due to multiple spam\
                    reports against you."
 
    if total_students < 5 :
        return None, None, False  
    elif total_students < 15 :
        if spam_reports > total_students*(2/3) :
            blockFromStudyRoom(course_code, user_to_report_email)
            return block_message, reported_message, True

    elif total_students < 30 :
        if spam_reports > total_students*(1/2) :
            blockFromStudyRoom(course_code, user_to_report_email)
            return block_message, reported_message, True
    
    else : 
        if spam_reports > total_students*(1/3) :
            blockFromStudyRoom(course_code, user_to_report_email)
            return block_message, reported_message, True

    return None, reported_message, False

def blockFromStudyRoom(course_code, user_to_report_email):
    mongo.db.studyrooms.update_one({
        "course_code": course_code }, { 
        "$push": {  "students_blocked": {
            "email":user_to_report_email ,
            "blocked_at": datetime.now()
                } 
            } 
        }, 
        upsert=True
    )

def unblockStudentFromStudyRoom(course_code, user_email):
    mongo.db.studyrooms.update_one({
        "course_code": course_code }, { 
        "$pull": {  "students_blocked": {
            "email":user_email } 
            } 
        }
    )

def isBlockedFromStudyRoom(course_code, user_email):
    course_study_room = mongo.db.studyrooms.find_one({ "course_code": course_code })
    
    if course_study_room.get("students_blocked") is None :
        return False, -1

    for blocked_student in course_study_room["students_blocked"]:
        if blocked_student["email"] == user_email :
            blocked_for_time = (datetime.now() - blocked_student["blocked_at"]).total_seconds()
            if blocked_for_time >= 6*60*60:
                unblockStudentFromStudyRoom(course_code, user_email)
                return False, -1
            else:
                return True, 6*60*60 - blocked_for_time 
    
    return False, -1

def updateStudyRoomSessionId(course_code, user_email, sid) :
    mongo.db.studyrooms.update_many({
        "course_code": course_code }, { 
        "$set": { 
        "students.$[student].sid": sid     
            } 
        }, 
        upsert=True,
        array_filters=[{ "student.email": user_email }] 
    )

def courseAvailable(course_code, user_email):

    if course_code in getStudentDetails(user_email)['courses']:
        return False, "You are already enrolled for the course : "+str(course_code)

    course_details = getCourseDetails(course_code)
    
    if course_details is None:
        return False, "Course does not exist !"

    if course_details['no_of_students'] == course_details['students_allowed'] :
        return False, "No seats available"

    return True, "Course : " + str(course_code) + " is available for enrollment"

def getCourseAnnouncements(course_code):
    announcements = list(mongo.db.courseannouncements.find_one({
        "course_code" : course_code
        })["announcements"]
    )
    for announcement in announcements:
        announcement_datetime = announcement["time_posted"].split(' ')
        time = announcement_datetime[4].split(":")
        announcement["time_posted"] = time[0]+" : "+time[1]
        announcement["date_posted"] = announcement_datetime[1]+ " " + announcement_datetime[2]+", "+announcement_datetime[3]

    return announcements

def getCourseDetails(course_code):
    
    course = mongo.db.courses.find_one({
        "course_code" : course_code
    })
    if course is None:
        return course
        
    instructor = getInstructorDetails(ObjectId(course['instructor_id']))
    course['instructor'] = instructor['first_name'] + " " + instructor['last_name']

    return course

def getInstructorDetails(instructor_id):
    return mongo.db.instructors.find_one({
        "_id" : instructor_id
    })
    
def getStudentDetails(user_email):
    
    return mongo.db.students.find_one({
        "email" : user_email
    })
 
def getStudentsInStudyRoom(course_code): 
    study_room_students =  list(mongo.db.studyrooms.find_one({"course_code":course_code})["students"])
    return [getStudentDetails(student['email']) for student in study_room_students]

def getStudyRoomChat(course_code):
    course_chat = mongo.db.studyroomschat.find_one({
        "course_code" : course_code
    })

    if course_chat is None:
        mongo.db.studyroomschat.insert({
            "course_code" : course_code,
            "chat" : []
        })
        return []

    return list(course_chat['chat'])

def getStudyRoomSessionId(user, course_code):
    course_study_room_students = list(mongo.db.studyrooms.find_one({"course_code":course_code})["students"])
    for student in course_study_room_students:
        if student["email"] == user["email"] :
            return student["sid"]

    return None

def getUserCourseList(user_email):

    user_course_code_list = getStudentDetails(user_email)['courses']
    user_course_list = []

    for course_code in user_course_code_list :
        course = getCourseDetails(course_code)
        user_course_list.append(course)

    return user_course_list

def getUserName(user_email):
    return session['user_first_name']+" "+session['user_last_name']

def dropCourse(user_email, course_code):

    course = getCourseDetails(course_code)
    student = getStudentDetails(user_email)

    student['courses'].remove(course_code)   
    course['id_students'].remove(student['email'])
    course_no_of_students = course['no_of_students'] - 1
    
    mongo.db.courses.update_one({"course_code":course_code},
        {"$set":{"no_of_students":course_no_of_students, "id_students":course['id_students']}})
    
    mongo.db.students.update_one({"email":user_email},{"$set":{"courses":student['courses']}})

    return True, "Course : " + str(course_code) + " dropped"
    return False, "Cannot drop course "

def loggedIn():
    
    if session.get('user_email') is None:
        return False
    return True

def logInStudyRoom(user_email, course_code):    

    course = mongo.db.studyrooms.find_one({
        "course_code" : course_code
    })

    for student in course["students"]:
        if student["email"] == user_email:
            mongo.db.studyrooms.update_one({
                "course_code": course_code ,
                "students.email": user_email 
                }, { 
                "$set": { 
                "students.$.activity_updated": datetime.now(),
                "students.$.spam_reports_by" : [],
                "students.$.sid" : ""     
                } 
            })
            return 

    mongo.db.studyrooms.update({
        "course_code" : course_code},{
        "$push": { "students": { 
            "email": user_email,
            "activity_updated" : datetime.now(),
            "sid" : "" ,
            "spam_reports" : 0}
            }
        }
    )
      
def logoutStudent(user_email): 
    
    mongo.db.students.update_one({"email":user_email},{"$set":{"status":"offline"}})
    mongo.db.studyrooms.update_many({},{
        "$pull": { "students": { "email": user_email } }
        }
    )

def logOutStudyRoom(user_email, course_code):

    mongo.db.studyrooms.update_many({
        "course_code" : course_code},{
        "$pull": { "students": { "email": user_email } }
        }
    )

def profanityCheck(message):
    profanity_prob = predict_prob([message])
    
    if profanity_prob < 0.3:
        return False
    else :
        return True 

def updateStudyRoomChat(course_code, chat):
    
    mongo.db.studyroomschat.update_one({
        "course_code": course_code,
        },
        {"$set" : {
            "chat" : chat
        }
    })

def updateStudyRoomActivityStatus(course_code, user_email):

    mongo.db.studyrooms.update_one({
        "course_code": course_code }, { 
        "$set": { 
        "students.$[student].activity_updated": datetime.now()     
            } 
        }, 
        upsert=True,
        array_filters=[{ "student.email": user_email }] 
    )

def getAllStudyRooms():
    return list(mongo.db.studyrooms.find())

def upvoteStudyRoomReply(course_code, question_id, reply_id, upvoted_by):

    chat = getStudyRoomChat(course_code)

    discussion_idx = next((i for i, discussion in enumerate(chat) if discussion["question_id"] == question_id), None)    
    discussion = chat[discussion_idx]

    replies = discussion["replies"]
    reply_idx = next((i for i, reply_data in enumerate(replies) if reply_data["reply_id"] == reply_id), None)    
    reply_data = replies[reply_idx]

    if upvoted_by == reply_data["replied_by"]["email"]:
        return None

    if upvoted_by in reply_data["upvoted_by"]:
        reply_data["upvoted_by"].remove(upvoted_by)
        reply_data["upvotes"] = reply_data.get("upvotes") - 1
        result = "unvoted"

    else:
        reply_data["upvoted_by"].append(upvoted_by)
        reply_data["upvotes"] = reply_data.get("upvotes") + 1
        result = "upvoted"
    
    replies[reply_idx] = reply_data
    discussion["replies"] = replies
    chat[discussion_idx] = discussion

    updateStudyRoomChat(course_code, chat)

    return result 

def userBlockedBy(inviter, invitee, course_code):
    
    invitee_block_list = getStudyRoomStudentBlockedList(course_code, invitee)
    if inviter in invitee_block_list:
        return True
    
    return False
 
def validateCredentialsAndLogin(user_email, user_password, session):
    
    student_exists = mongo.db.students.find_one({
        "email"      : user_email,
        "password"   : user_password
    })
    
    if student_exists is None:
        return False

    session['user_email'] = student_exists['email']
    session['user_first_name'] = student_exists['first_name']
    session['user_last_name'] = student_exists['last_name']

    mongo.db.students.update_one({"email":session['user_email']},{"$set":{"status":"online"}})

    return True

def validateSignUpCredentials(email):

    student_exists = mongo.db.students.find_one({
        "email"      : email,
    })
    
    if student_exists is not None:
        return "User with this email ID already exists !"
    
    return True

def getTimeString(time):
    if time < 60:
        str_time = str(int(time))+" seconds"
    elif time < 3600:
        str_time = str(int(time/60))+" minutes"
    else :
        str_time = str(int(time/3600))+" hours"
        str_time = str_time + ", " +str(int((time%3600)/60)) +" minutes"
    
    return str_time
