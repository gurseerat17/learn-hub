__VoteKick__ is a feature often found in multi-user shared setting which allows the users to report against any spam user X and multiple such reports kicks X out of the setting for a particluar period of them. 

Multiple spam reports by students in any study room would lead to a votekick accoding to the following criteria :

### Case 1 : Total students in study room <= 3 :
`VoteKick not applicable`

<br /> 

### Case 2 : Total students in study room > 3 and < 15 :
`VoteKick if spam_reports > total_students_in_study_room*(2/3) `

<br /> 

### Case 3 : Total students in study room > 15 and < 30 :
`VoteKick if spam_reports > total_students_in_study_room*(1/2) `

<br /> 
    
### Case 4 : Total students in study room > 30 :
`VoteKick if spam_reports > total_students_in_study_room*(1/3) `

<br /> 

A user votekicked out won't be able to enter the study room for the next _6 Hours_ 
