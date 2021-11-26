from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask.globals import session
from flask.helpers import url_for
from werkzeug.utils import redirect
from flask_socketio import SocketIO, emit, join_room
from flask_pymongo import PyMongo
from flask import request, Flask
from helpers import *

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://engage:engage@learn-hub.hvs2a.mongodb.net/learnHub?retryWrites=true&w=majority"
app.config['SECRET_KEY']='well67839to302the094343he38209av320-en'

mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/", methods=["POST","GET"])
def home():
    return render_template("home.html", warning = request.args.get('warning'), 
                            success = request.args.get('success'), alert = request.args.get('alert'))

@app.route("/courses/add-course", methods=["POST","GET"])
def add_course():

    if request.method == "POST":
        
        course_code = request.form.get("CourseCode")
        enrollment_key = request.form.get("EnrollmentKey")

        course_available, message = courseAvailable(course_code, session['user_email'])
        if not course_available:    
            return redirect(url_for("courses", alert = message))
        else :
            if addCourseForStudent(session['user_email'], course_code, enrollment_key) :
                return redirect(url_for("courses", success = "Course : "+str(course_code)+" added !"))
            else :
                return redirect(url_for("courses", warning = "Wrong enrollment key"))
    else :
        return redirect(url_for("courses"))

@app.route("/courses", methods=["POST","GET"])
def courses(): 

    if loggedIn() == False:
        return redirect(url_for("login"))

    user_email = session['user_email']
    user_course_list = getUserCourseList(user_email)

    return render_template("courses.html", user_first_name = getUserName(user_email).split(' ', 1)[0], 
                            course_list = user_course_list, warning = request.args.get('warning'), 
                            alert = request.args.get('alert'), success = request.args.get('success'))

@app.route("/course--details/drop/<course_code>", methods=["POST","GET"])
def drop_course(course_code):
    course_dropped, message = dropCourse(session['user_email'], course_code)
    
    if not course_dropped:
        return redirect(url_for("courses", alert = message))

    return redirect(url_for("courses"))

@app.route("/course-details/<course_code>", methods=["POST","GET"])
def course_details(course_code):

    if loggedIn() == False:
        return redirect(url_for("login"))

    user = getStudentDetails(session['user_email'])
    if user['email'] not in getCourseDetails(course_code)["id_students"]:
        return redirect(url_for("courses"))

    course_details = getCourseDetails(course_code)
    course_announcements = getCourseAnnouncements(course_code)
    course_announcements.reverse()

    return render_template("course-details.html", user = user, course = course_details,
                            course_announcements = course_announcements, alert = request.args.get('alert'))

@app.route("/study-room/<course_code>", methods = ["POST", "GET"])
def study_room(course_code):

    if loggedIn() == False:
        return redirect(url_for("login"))

    if session['user_email'] not in getCourseDetails(course_code)["id_students"]:
        return redirect(url_for("courses"))

    study_room_students = getStudentsInStudyRoom(course_code)
    user = getStudentDetails(session['user_email'])
    
    is_blocked, time_left = isBlockedFromStudyRoom(course_code, session['user_email'])
    if  is_blocked == True:
        return redirect(url_for("course_details", course_code = course_code, alert = 
                        "You can not log into the study room for the next "+ getTimeString(time_left)))

    logInStudyRoom(session['user_email'], course_code)

    if user not in study_room_students:
        socketio.emit('study room login', {'course_code': course_code, 'student_email':session['user_email'],
                        'student_first_name': session['user_first_name'], 'student_last_name': session['user_last_name']},
                        broadcast=True)
    else :
        study_room_students.remove(user)

    study_room_discussion = getStudyRoomChat(course_code)
    study_room_discussion.reverse()

    return render_template("studyroom.html", course_code = course_code, students = study_room_students, user = user, 
                            blocked = getStudyRoomStudentBlockedList(course_code, session['user_email']),
                            discussions = study_room_discussion, invite = request.args.get('invite'), 
                            inviter = request.args.get('inviter'), invitee = request.args.get('invitee'),
                            warning = request.args.get('warning'), success= request.args.get('success'), 
                            alert = request.args.get('alert') )

@app.route("/study-room/logout/<course_code>/<user_email>", methods = ["POST", "GET"])
def study_room_logout(course_code, user_email):
    
    # user_email = request.args.get('user_email')
    if user_email is None:
        user_email = session["user_email"]

    study_room_logout_(course_code, user_email)

    return redirect(url_for("course_details", course_code = course_code))

@app.route("/login", methods=["POST","GET"])
def login():

    if request.method == "POST":
        
        user_email = request.form.get("LoginEmail")
        user_password = request.form.get("LoginPassword")

        if validateCredentialsAndLogin(user_email, user_password, session):    
            return redirect(url_for("courses"))

        else :
            return redirect(url_for("home", warning = "Incorrect Login Details"))

        
    else :
        return render_template("home.html")

@app.route("/signUp", methods=["POST","GET"])
def signUp():

    if request.method == "POST":

        email = request.form.get("SignUpEmail")
        password = request.form.get("SignUpPassword")
        first_name = request.form.get("SignUpFirstName")
        last_name = request.form.get("SignUpLastName")

        if validateSignUpCredentials(email) == True:
            
            addNewStudent(email, password, first_name, last_name)
            validateCredentialsAndLogin(email, password, session) # Logging In the new user
            return redirect(url_for("courses", user_email = session['user_email']))

        
        else :
            return redirect(url_for("home", warning = validateSignUpCredentials(email)))

    else :
        return redirect(url_for("home"))

@app.route("/logout")
def logout():

    logoutStudent(session['user_email'])
    session.clear()
    
    return redirect(url_for("home"))

@socketio.on('send invite', namespace ='/')
def send_invite(data):

    course_code = data.get('course_code')
    meeting_link = data.get('meeting') 
    topic = data.get('topic')
    inviter = getStudentDetails(data.get('from')) 
    invitee = getStudentDetails(data.get('to'))

    if userBlockedBy(inviter["email"], invitee["email"], course_code):
        return 

    invitee_sid = getStudyRoomSessionId(invitee, course_code)
    
    inviter_name = inviter['first_name']+ " " + inviter['last_name']

    room = session.get('room')
    join_room(room)

    emit('invitation', {'inviter': inviter_name, 'topic':topic, 'meeting_link': meeting_link} , room=invitee_sid)

@socketio.on('report user', namespace ='/')
def report_user(data):
    
    course_code = data.get('course_code')
    user_to_report = data.get('to_report')
    reported_by = data.get('reported_by')

    message, feedback , blocked = reportStudentInStudyRoom(course_code, user_to_report, reported_by)
   
    user_to_report_sid = getStudyRoomSessionId(getStudentDetails(user_to_report), course_code)
    reported_by_sid = getStudyRoomSessionId(getStudentDetails(reported_by), course_code)

    room = session.get('room')
    join_room(room)

    if blocked == True:
        emit('log out', room=user_to_report_sid)
        return 

    if message is not None:
        emit('reported', {'message': message} , room=user_to_report_sid)

    if feedback is not None:
        emit('feedback', {'message': feedback} , room=reported_by_sid)

@socketio.on('block or unblock user', namespace ='/')
def block_user(data):

    course_code = data.get('course_code')
    user_email = data.get('user_email') 
    user_sid = getStudyRoomSessionId(getStudentDetails(user_email), course_code)

    room = session.get('room')
    join_room(room)

    if(data.get('action') == "Block"):

        user_to_block = getStudentDetails(data.get('to_block'))
        message = blockStudentInStudyRoom(user_email, user_to_block, course_code)
        emit('user blocked', {'message': message} , room=user_sid)

    elif(data.get('action') == "Unblock"):

        user_to_unblock = getStudentDetails(data.get('to_unblock'))
        message = unblockStudentInStudyRoom(user_email, user_to_unblock, course_code)
        emit('user unblocked', {'message': message} , room=user_sid)

@socketio.on('unblock user', namespace ='/')
def unblock_user(data):

    course_code = data.get('course_code')
    user_email = data.get('user_email') 
    user_to_unblock = getStudentDetails(data.get('to_unblock'))
    message = unblockStudentInStudyRoom(user_email, user_to_unblock, course_code)

    user_sid = getStudyRoomSessionId(getStudentDetails(user_email), course_code)

    room = session.get('room')
    join_room(room)

    emit('user blocked', {'message': message} , room=user_sid)

@socketio.on('post reply')
def post_reply(data):

    course_code = data.get('course_code')
    question_id = data.get('question_id')
    reply = data.get('reply')
    replied_by = getStudentDetails(data.get('replied_by')) 
    

    if profanityCheck(str(reply)) == True:
        room = session.get('room')
        join_room(room)
        emit('reply blocked' , room=getStudyRoomSessionId(replied_by, course_code))
        return


    replied_by_name = replied_by['first_name']+ " " + replied_by['last_name']
    reply_id = addReplyToStudyRoomDiscussion(course_code, question_id, reply, replied_by)

    emit('new reply', {'question_id': question_id , 'reply':reply, 'reply_id' : reply_id ,
        'replied_by_name': replied_by_name} , broadcast=True)

@socketio.on('upvote reply')
def upvote_reply(data):

    course_code = data.get('course_code')
    question_id = data.get('question_id')
    reply_id = data.get('reply_id')
    upvoted_by = data.get('upvoted_by') 

    upvote_result = upvoteStudyRoomReply(course_code, question_id, reply_id, upvoted_by)
    
    if upvote_result == "upvoted":
        emit('reply upvoted', {'question_id': question_id , 'reply_id':reply_id, 'upvoted_by': upvoted_by},
             broadcast=True)
    elif upvote_result == "unvoted":
        emit('reply unvoted', {'question_id': question_id , 'reply_id':reply_id, 'unvoted_by': upvoted_by}, 
             broadcast=True)
    else :
        return

@socketio.on('post question')
def post_question(data):

    course_code = data.get('course_code')
    question = data.get('question')
    question_by = getStudentDetails(data.get('question_by')) 

    question_id = addQuestionToStudyRoomDiscussion(course_code, question, question_by)

    emit('new question', { 'course_code' : course_code, 'question_by': question_by["email"] }, broadcast=True)

@socketio.on('joined study room')
def new_login(data):    
    updateStudyRoomSessionId(data.get('course_code'),data.get("user_email"), request.sid) 

@socketio.on('post comment')
def post_comment(data):

    course_code = data.get('course_code')
    announcement_id = data.get('announcement_id')
    comment = data.get('comment')
    comment_by = getStudentDetails(data.get('comment_by'))  

    comment_by_name = comment_by['first_name']+ " " +comment_by['last_name']
    addCommentToCourseAnnouncements(course_code, announcement_id, comment, comment_by)

    emit('new comment', {'announcement_id': announcement_id , 'comment':comment, 'comment_by_name': comment_by_name},
         broadcast=True)


@socketio.on('active')
def update_study_room_status(data):
    
    updateStudyRoomActivityStatus(data.get('course_code'), data.get('user_email'))

def study_room_logout_(course_code, user_email):
    logOutStudyRoom(user_email, course_code)
    socketio.emit('study room logout', {'course_code': course_code, 'email': user_email}, broadcast=True)

def checkIdleStudyRoomStudents():
    study_rooms = getAllStudyRooms()
    for course in study_rooms:
        course_code = course["course_code"]
        for student in course["students"]:
            if (datetime.now() - (student["activity_updated"])).total_seconds() > 15*60:
                study_room_logout_( course_code = course_code, user_email = student["email"])
            

@app.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return __builtins__.zip(*args, **kwargs)


if __name__ == "__main__":
    scheduler = APScheduler()
    scheduler.add_job(func=checkIdleStudyRoomStudents, trigger='interval', id="checkIdle", seconds=15*60)
    scheduler.start()
    socketio.run(app, debug=True)