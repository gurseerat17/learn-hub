var invitePrompts = document.getElementsByClassName("invite");
var inviteModal = document.getElementById("invite-modal");
var inviteClose = document.getElementById("invite-close");
var inviteCancel = document.getElementById("invite-cancel");
var questionMinimiseAll = document.getElementsByClassName("question-minimise") 
var questionMaximiseAll = document.getElementsByClassName("question-maximise") 
var addDiscussionButton = document.getElementById("add-discussion")
var newQuestionModal = document.getElementById("new-question-modal")
var newQuestionClose = document.getElementById("new-question-close")
var questionTextArea = document.getElementById("new-question")
var refreshDiscuss = document.getElementById("refresh-discuss")
var studentIcons = document.getElementsByClassName("fa fa-user-circle")
var alertPopup = document.getElementById("popup-alert");
var post_reply_buttons = document.getElementsByClassName("post_reply");
    
for(var i = 0; i < invitePrompts.length; i++) {
    invitePrompts[i].onclick = function() {
        inviteModal.style.display = "block";
    }
}

inviteClose.onclick = function() {
    inviteModal.style.display = "none";
}

inviteCancel.onclick = function() {
    inviteModal.style.display = "none";
}

addDiscussionButton.onclick = function() {
    newQuestionModal.style.display = "block";
}

newQuestionClose.onclick = function() {
    newQuestionModal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == alertPopup) {
    alertPopup.style.display = "none";
    }
}

for(var i = 0; i < questionMaximiseAll.length; i++) {
    
    let questionMaximise = questionMaximiseAll[i]
    let questionMinimise = questionMinimiseAll[i]
    let question_id = $(questionMaximise).attr('data-question')
    let questionReplySection = document.querySelector('[class="question-replies"][data-question="'+ question_id.toString() +'"]')  
    
    questionMaximise.onclick = function() {
        questionReplySection.style.display = "block";
        questionMinimise.style.display = "block";
        questionMaximise.style.display = "none";
    }
    
    questionMinimise.onclick = function() {
        questionReplySection.style.display = "none";
        questionMaximise.style.display = "block";
        questionMinimise.style.display = "none";
    }
}



for(var i = 0; i < studentIcons.length; i++) {
    studentIcons[i].style.color = getRandomColor();
} 

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}


$(document).ready(function(){ 
    var socket = io.connect("http://127.0.0.1:5000/");

    socket.on('connect', () => {
        socket.emit('joined study room', {course_code : course_code, user_email: user_email})
    }); 
        
    
    function create_reply_element(question_id, reply, reply_id, replied_by_name){
        let div1 = document.createElement("div")
        div1.setAttribute("id", "discussion-reply");
        let hr = document.createElement("hr")
        hr.style.margin = "auto";
        hr.style.marginBottom = "15px";
        hr.style.marginTop = "15px";
        hr.style.color = "#b8b8b8";
        let div2 = document.createElement("div")
        div2.classList.add("trainer")
        div2.className += " d-flex justify-content-between align-items-center"
        div2.style.width = "95%";
        div2.style.marginLeft = "auto"
        div2.style.marginRight = "auto"
        let div3 = document.createElement("div")
        div3.classList.add("trainer-profile")
        div3.className += " d-flex align-items-center"
        let table1 = document.createElement("table")
        let tr11 = document.createElement("tr")
        let td111 = document.createElement("td")
        let p1 = document.createElement("p")
        p1.classList.add("reply-name")
        p1.appendChild(document.createTextNode(replied_by_name));
        let tr12 = document.createElement("tr")
        let td121 = document.createElement("td")
        let span1 = document.createElement("span")
        span1.classList.add("reply")
        span1.appendChild(document.createTextNode(reply));
        let div4 = document.createElement("div")
        div4.classList.add("trainer-rank")
        div4.className += " d-flex align-items-center"
        let table2 = document.createElement("table")
        let tr21 = document.createElement("tr")
        let td211 = document.createElement("td")
        td211.classList.add("upvote-icon") 
        upvote_icon = document.createElement("i")
        upvote_icon.className += "bx bx-upvote upvote"
        upvote_icon.setAttribute("id", reply_id);
        upvote_icon.setAttribute("data-reply", reply_id);
        upvote_icon.setAttribute("data-question", question_id);

        upvote_icon.onclick = function() {upvote($(this))};

        td211.appendChild(upvote_icon)
        let td212 = document.createElement("td")
        td212.classList.add("upvote-num")
        td212.setAttribute("data-reply", reply_id);
        td212.setAttribute("data-question", question_id);

        td212.innerHTML = "0"
        tr21.appendChild(td211)
        tr21.appendChild(td212)
        table2.appendChild(tr21)
        div4.appendChild(table2)

        td111.appendChild(p1)
        tr11.appendChild(td111)
        td121.appendChild(span1)
        tr12.appendChild(td121)
        table1.appendChild(tr11)
        table1.appendChild(tr12)
        div3.appendChild(table1)

        div2.appendChild(div3)
        div2.appendChild(div4)

        div1.appendChild(hr)
        div1.appendChild(div2)

        return div1

    }
    
    function create_new_student(email, first_name, last_name){
        let div1 = document.createElement("div");
        div1.className += "col-lg-3 col-md-4";
        div1.setAttribute("id", email);
        let div2 = document.createElement("div");
        div2.className += "icon-box";
        let icon = document.createElement("i");
        icon.className += "fa fa-user-circle";
        icon.style.color = getRandomColor();
        let name = document.createElement("h3");
        name.innerHTML = first_name + " " + last_name;
        let nav = document.createElement("nav");
        nav.setAttribute("id", "navbar");
        nav.className += "navbar order-last order-lg-0";
        let ul1 = document.createElement("ul");
        let li1 = document.createElement("li");
        li1.className += "get-started-btn dropdown"
        li1.style.background = "transparent";
        li1.style.fontSize = "5px";
        let icon2 = document.createElement("i");
        icon2.className += "fa fa-ellipsis-v";
        icon2.style.float = "right";
        let ul2 = document.createElement("ul");
        let li21 = document.createElement("li");
        let a1 = document.createElement("a");
        a1.setAttribute("name", email);
        a1.className+="invite"
        a1.innerHTML = "Invite to Discuss"
        let li22 = document.createElement("li");
        let a2 = document.createElement("a");
        a2.setAttribute("name", email);
        a2.className+="report"
        a2.innerHTML = "Report Spam"
        let li23 = document.createElement("li");
        let a3 = document.createElement("a");
        a3.setAttribute("name", email);
        a3.className+="block"
        a3.innerHTML = "Block"

        a1.onclick = function() {
        set_invitee($(this))
        inviteModal.style.display="block";
        }

        a2.onclick = function() {
            report_user($(this))
        }

        a3.onclick = function() {
            set_blocked($(this))
        }

        li21.appendChild(a1);
        li22.appendChild(a2);
        li23.appendChild(a3);
        ul2.appendChild(li21);
        ul2.appendChild(li22);
        ul2.appendChild(li23);
        li1.appendChild(icon2);
        li1.appendChild(ul2);
        ul1.appendChild(li1);
        nav.appendChild(ul1);
        div2.appendChild(icon);
        div2.appendChild(name);
        div2.appendChild(nav);
        div1.appendChild(div2);
        return div1;
    }
 

    function add_reply_to_discussion(question_id, reply, reply_id, replied_by_name){

        let new_reply = create_reply_element (question_id, reply, reply_id, replied_by_name)
        let element = document.querySelector('[class="question-replies"][data-question="'+ question_id.toString() +'"]');
        if ( element !=null){
            element.appendChild(new_reply); 
        }    
    }

    function upvote(elem){

        let reply_id = $(elem).attr('data-reply')
        let question_id = $(elem).attr('data-question')
        let upvoted_by = user_email
        console.log(reply_id, question_id, upvoted_by)
        socket.emit('upvote reply', {course_code : course_code,question_id: question_id, reply_id: reply_id, upvoted_by: upvoted_by});
    }

    var invitee, to_block_or_unblock

    function set_invitee(elem){
        invitee = elem.attr('name')
    }

    function set_blocked(elem){
        to_block_or_unblock = elem.attr('name') 
        invite_to_discuss = document.querySelector('[class="invite"][name='+CSS.escape(to_block_or_unblock)+']')
        if(elem.context.innerHTML == "Block"){
            socket.emit('block or unblock user', {action: "Block", course_code: course_code, user_email: user_email, to_block: to_block_or_unblock});
            elem.context.innerHTML="Unblock";
            invite_to_discuss.onclick = function(){
                return false;
            }
            invite_to_discuss.setAttribute("id", "disabled")
        }
        else if(elem.context.innerHTML == "Unblock"){
            socket.emit('block or unblock user', {action: "Unblock", course_code: course_code, user_email: user_email, to_unblock: to_block_or_unblock});
            elem.context.innerHTML="Block";
            invite_to_discuss.onclick = function() {
                set_invitee($(this))
                inviteModal.style.display="block";
            }
            invite_to_discuss.setAttribute("id", null)
        }
    }

    function report_user(elem){
        to_report = elem.attr('name') 
        socket.emit('report user', { course_code: course_code, to_report: to_report, reported_by : user_email});
    }


    for (let i = 0; i < post_reply_buttons.length; i++) {
        
        post_reply_buttons[i].onclick = function(){    
            elem = $(this)
            let question_id = elem.attr('data-question')
            let replyTextArea = document.querySelector('[id="reply"][data-question="'+ question_id.toString() +'"]')
            let reply = replyTextArea.value
            let replied_by = user_email
            
            if(reply.length == 0) return;
            console.log("reply:", reply)
            
            socket.emit('post reply', {course_code : course_code,question_id: question_id, reply: reply, replied_by: replied_by});
            replyTextArea.value = ""
        }
    }

    $('.invite').click(function(event){
        set_invitee($(this))
        return;
    })    

    $('.report').click(function(event){
        report_user($(this))
        return;
    }) 

    $('.block').click(function(event){
        set_blocked($(this))
        return;
    })

    $('#send_invite').click(function(event){
        
        let meeting_link = $('#meeting-link').val();
        let topic_brief = $('#topic-brief').val();
        
        socket.emit('send invite', {course_code: course_code, meeting: meeting_link, topic:topic_brief, from: user_email, to: invitee});
        
        inviteModal.style.display = "none";          
    })
    


    $('#post_question').click(function(event){
        let question_by = user_email
        let question = $('#new-question').val();
        
        if(question.length == 0) return;
        
        socket.emit('post question', {course_code : course_code,question_by: question_by, question: question});
        newQuestionModal.style.display = "none"
    })
 
    $('#refresh-discuss-button').click(function(event){
        reload_at_discuss()
        refreshDiscuss.style.display = "none";
    })
    upvotes = document.getElementsByClassName("upvote")
    for(var i = 0; i < upvotes.length; i++) {

        let elem =upvotes[i]; 
        elem.onclick = function(){
            upvote(elem)
        }
    }

    var idleTime = 0;
    var activity_update_time = 0
    setInterval(timerIncrement, 60000); // 1 minute

    $(this).mousemove(function (e) {
        idleTime = 0;
    });
    $(this).keypress(function (e) {
        alertPopup.style.display="none";
        idleTime = 0;
    });
    
    function timerIncrement() {

        idleTime = idleTime + 1;
        activity_update_time = activity_update_time + 1

        if (idleTime > 25){
            display_alert(" You have been inactive for the last 30 minutes <br>\
                            Confirm your presence by pressing a key or clicking on the page ... " , "alert")
        }

        if (idleTime > 30) { 
            window.location.href = redirect_url_logout;
        }

        if(activity_update_time == 15){
            activity_update_time = 0
            socket.emit('active', {course_code:course_code, user_email:user_email} )
        }
    } 
    
    function display_alert(message, type){
        alertPopup.style.display="block";
        alertMessage = document.getElementById("alert-message");
        alertMessage.innerHTML = message;

        if(type == "alert"){
            alertIcon = document.getElementById("alert-icon");
            alertIcon.className = "bx bxs-error-circle"
            alertIcon.style.color = "gold"
        }

        if(type == "success"){
            alertIcon = document.getElementById("alert-icon");
            alertIcon.classList.remove("bxs-error-circle")
            alertIcon.classList.add("bxs-check-circle")
            alertIcon.style.color = "#3ac162"
        }

        if(type == "warning"){
                alertIcon = document.getElementById("alert-icon");
                alertIcon.classList.remove("bxs-error-circle")
                alertIcon.classList.add("bxs-x-circle")
                alertIcon.style.color = "red"
        }

    }

    socket.on('invitation', function(data) {
        console.log("invitation")
        meeting_link = data["meeting_link"];
        if (meeting_link.substring(0, 4) != "http"){
            meeting_link = "https://".concat(meeting_link)
        }
        display_alert(data["inviter"] + " invited you for a dicussion on <b>" + data["topic"] +"</b>" 
        + "<br> <a href='"+meeting_link+"'>Click here to join</a>", "alert")
    });
    
    socket.on('user blocked', function(data) {
        display_alert(data["message"], "success")
    })

    socket.on('reported', function(data) {
        console.log("reported")
        display_alert(data["message"], "warning")
    })

    socket.on('feedback', function(data) {
        display_alert(data["message"], "success")
    })

    socket.on('log out', function(data) {
        window.location.href = redirect_url_logout;
    })

    function reload_at_discuss(){
        location.reload()
        // $( "#discuss" ).load(window.location.href + " #discuss" );
    }

    socket.on('new question', function(data){
        console.log("new question")

        if(data["course_code"] != course_code )
            return
        if(data["question_by"] === user_email){
            reload_at_discuss();
        }
        else{
            refreshDiscuss.style.display = "block";
        }
    });

    socket.on('new reply', function(data){
        add_reply_to_discussion(data['question_id'], data['reply'], data['reply_id'], data['replied_by_name']);
    });

    socket.on('reply upvoted', function(data){
        
        let upvote_num = document.querySelectorAll('[class="upvote-num"][data-reply='+CSS.escape(data['reply_id'])+'][data-question='+ CSS.escape(data['question_id'])+']')[0];
        upvote_num.innerText = parseInt(upvote_num.innerText) + 1
        
        if(data['upvoted_by'] === user_email){
            let upvote_icon = document.getElementById(data['reply_id'])
            upvote_icon.classList.remove("bx-upvote")
            upvote_icon.classList.add("bxs-upvote")
        }
        
    });

    socket.on('reply unvoted', function(data){
        
        let upvote_num = document.querySelectorAll('[class="upvote-num"][data-reply='+CSS.escape(data['reply_id'])+'][data-question='+ CSS.escape(data['question_id'])+']')[0];
        upvote_num.innerText = parseInt(upvote_num.innerText) - 1
        
        if(data['unvoted_by'] === user_email){
            var upvote_icon = document.getElementById(data['reply_id'])
            upvote_icon.classList.remove("bxs-upvote")
            upvote_icon.classList.add("bx-upvote")
        }
    });

    socket.on('reply blocked', function(data){
        console.log("reply blocked")
        display_alert("Your reply might be disrespectful to the users.<br> Kindly note that you need to maintain the\
                     decorum of this educational platform", "alert")
    });

    socket.on('study room logout', function(data){
        console.log("study room logout")
        let data_course_code = data['course_code'];
        let user_email = data['email'];
        if(data_course_code === course_code){
        let student_left = document.getElementById(user_email)
        student_left.style.display = "none"
        }
    });

    socket.on('study room login', function(data){
        console.log("study room login")
        
        let data_course_code = data['course_code'];
        console.log(data, course_code)
        
        if(data_course_code == course_code){
            console.log("-><-")
            let student_new = create_new_student(data["student_email"], data["student_first_name"], data["student_last_name"])
            console.log("->",student_new)
            let element = document.getElementById('students');
            console.log(element)
            if ( element !=null){
                    element.appendChild(student_new); 
            }   
        }
    }); 
    
});