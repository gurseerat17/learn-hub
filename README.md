# learn-hub
<br />
Learn Hub is a Flask based web application which allows learns to manage their courses, interact and collaborate on course content and stay connected to their peers and mentors while being physically apart.
<br /><br /><br />
Refer to the below mentioned steps to run the application :
<br /> <br />

* Install **Python 3.6** (preferrably 3.6.9)

* Clone this repository to your local machine : 
  ```
  $ git clone https://github.com/gurseerat17/learn-hub.git
  ```
* Navigate into in the learn-hub folder. 
  ```
  cd learn-hub
  ```
* Create a virtual environment and install dependencies:
  #### Bash on Linux Systems
  ```
  python3.6 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
  #### Git Bash on Windows Systems
  ```
  py -3.6 -m venv .venv
  source .venv\\scripts\\activate
  pip install -r requirements.txt
  ```
  #### Powershell / Cmd
  ```
  py -3.6 -m venv .venv
  .venv\scripts\activate
  pip install -r requirements.txt
  ```
* Run the development server:
  #### Windows Systems
  ```
  py -3.6 learnHub.py
  ```
  #### Linux Systems
  ```
  python3.6 learnHub.py
  ```

  Ignore the time zone related warnings and you should see something similar to :
  ```
  wsgi starting up on http://127.0.0.1:5000
  ```
  Visit the link and enjoy Learn Hub ! Refer to `/resources/students.md` to login existing users.

  You may quit the server by pressing (Ctrl + C)

__Note__ : 
* In case you are running the development server at any other port number, you will need to update the same in [`/static/js/study-room.js/`](static/js/study-room.js/) `line 81`  and  [`/static/js/course-announcements.js/`](static/js/course-announcements.js/) `line 39`

<br />

* Flask-SocketIO has been used to enable real time display of comments, replies and all other sorts of communication supported by this application. Incase of any [disconnection](https://socket.io/docs/v4/troubleshooting-connection-issues/#problem-the-socket-gets-disconnected) (which was never encoutered while testing of the application) , a refresh should re-establish the socket connections. 

<br />

# Database (MongoDB)
<br />

MongoDB has been used as the database for learn-hub and hosted using MongoDB Atlas. To connect to the databse cluster, either of the following may be used :

* ##### Connection String:
  `
  mongodb+srv://engage:engage@learn-hub.hvs2a.mongodb.net/learnHub?retryWrites=true&w=majority
  `

* ##### Indiviual Connection Credentials (SRV Record) : 
  
  Hostname : `learn-hub.hvs2a.mongodb.net`

  Authenication : Username/Password<br />
  Username : `engage`<br />
  Password : `engage`<br />
  
This is how you can enter these details in [MongoDB Compass](https://www.mongodb.com/products/compass) and connect to the database : 


<img src="resources/mongoDB/mongodb-connect.png" align= "center" width=49% alt= "resources/mongoDB/mongodb-connect.png"> <img src="resources/mongoDB/mongodb-courses-sample.png" align= "center" width=49% alt = "resources/mongoDB/mongodb-courses-sample.png">