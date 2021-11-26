var questionMinimiseAll = document.getElementsByClassName("question-minimise") 
var questionMaximiseAll = document.getElementsByClassName("question-maximise") 
var post_comment_buttons = document.getElementsByClassName("post_comment")
var alertPopup = document.getElementById("popup-alert");

window.onclick = function(event) {
    if (event.target == alertPopup) {
    alertPopup.style.display = "none";
    }
}

for(var i = 0; i < questionMaximiseAll.length; i++) {
    
    let questionMaximise = questionMaximiseAll[i]
    let questionMinimise = questionMinimiseAll[i]
    let question_id = $(questionMaximise).attr('data-announcement')
    let questionReplySection = document.querySelector('[class="question-replies"][data-announcement="'+ question_id.toString() +'"]')  
    
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

$(document).ready(function(){ 
    var socket = io.connect("http://127.0.0.1:5000/");
 
    function create_reply_element(question_id, reply, reply_id, replied_by_name, options){
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
        upvote_icon.setAttribute("data-announcement", question_id);

        upvote_icon.onclick = function() {upvote(upvote_icon)};

        
        if(options != "no_upvote"){
            td211.appendChild(upvote_icon)
            let td212 = document.createElement("td")
            td212.classList.add("upvote-num")
            td212.setAttribute("data-reply", reply_id);
            td212.setAttribute("data-announcement", question_id);

            td212.innerHTML = "0"
            tr21.appendChild(td211)
            tr21.appendChild(td212)
            table2.appendChild(tr21)
            div4.appendChild(table2)
        }

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

    function add_comment_to_announcements(announcement_id, comment, comment_by_name){

        let new_comment = create_reply_element (announcement_id, comment, "", comment_by_name, "no_upvote")
        let element = document.querySelector('[class="question-replies"][data-announcement="'+ announcement_id.toString() +'"]');
        if ( element !=null){
            element.appendChild(new_comment); 
        }    
    }
  
    for (let i = 0; i < post_comment_buttons.length; i++) {
        
        post_comment_buttons[i].onclick = function(){    
            elem = $(this)
            let announcement_id = elem.attr('data-announcement')
            let commentTextArea = document.querySelector('[id="comment"][data-announcement="'+ announcement_id.toString() +'"]')
            let comment = commentTextArea.value
            let comment_by = user_email

            if(comment.length == 0) return;
            
            socket.emit('post comment', {course_code : course_code, announcement_id: announcement_id, comment: comment,
            comment_by: comment_by});
            commentTextArea.value = ""
        }
    }
   
 
    socket.on('new comment', function(data){
        add_comment_to_announcements(data['announcement_id'], data['comment'], data['comment_by_name']);
    });
    
});