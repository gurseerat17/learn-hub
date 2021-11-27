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
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
  #### Git Bash on Windows Systems
  ```
  py -3 -m venv .venv
  source .venv\\scripts\\activate
  pip install -r requirements.txt
  ```
  #### Powershell / Cmd
  ```
  py -3 -m venv .venv
  .venv\scripts\activate
  pip install -r requirements.txt
  ```
* Run the development server:
  ```
  python3 learnHub.py
  ```
  Ignore the time zone related warnings and you should see something similar to :
  ```
  wsgi starting up on http://127.0.0.1:5000
  ```
  Visit the link and enjoy Learn Hub !

  You may quit the server by pressing (Ctrl + C)
<br /><br />
# Database (MongoDB)
<br />

MongoDB has been used as the database for learn-hub and hosted using MongoDB Atlas. To connect to the databse cluster, either of teh following may be used :

* ##### Connection String:
  `
  mongodb+srv://engage:engage@learn-hub.hvs2a.mongodb.net/learnHub?retryWrites=true&w=majority
  `

* ##### Indiviual Connection Credentials (SRV Record) : 
  
  Hostname : `learn-hub.hvs2a.mongodb.net`

  Authenication : Username/Password
  Username : `engage`
  Password : `engage`
  
