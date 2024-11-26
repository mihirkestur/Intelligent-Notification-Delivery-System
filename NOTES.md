# Work to do

- generate useful data per person
- handle backlog how?
  - in a queue at night: 10:00 p.m. (bedtime?) -> show all
    - if they click -> negative reward
    - classify these separately somehow?

## Discussion
  - time 100: [Whatsapp_1, Linkedin_1] -> [YES, NO] -> [LinkedIn1]
  - time 101: [Whatsapp_2, LinkedIn_2] -> [YES, YES]
  - features: number_of_{app}_notifs_in_queue?, total_notifs? 
  - time -- end of day -> [LinkedIn_3] ???? -> show it -> negatively reward the model??

- What happens if a user doesn't click the notification immediately? Right now we assume they clicked it immediately => we could somehow make the reward -time it took to click.
  - What if they just don't click it

- When it comes to recording data, how did we record when we clicked? there will be two rows then

### Time interval

- Every minute 

### Learning objective

- Yes/No acc. to the features below

### Random papers

https://dl.acm.org/doi/pdf/10.1145/3099023.3099046 - synthesis of dataset

# Dataset features

- time of day (0-1)
- last recorded human activity (see below)
- application name (whatsapp, email)
- last recorded geofenced location - HOME, SCHOOL, LIBRARY, CAFETERIA
- queue features

Time 

// App name. : Randomly created notification for either app 
// Location: (HOME -> SCHOOL -> CAFETERIA -> P(L|Time)) + hard bounds -> if time is 5pm have to change to home!!
// Human activity -> based on time + location => probability (change between whatever -> IN_VEHICLE, BICYCLE)
// When do they click the notification? -> 0 ---> inf???
    // P(App name, location, human activity) => click or not click? w. some probability 0-1??
// Queue features ???

# Android activities

IN_VEHICLE 	The device is in a vehicle, such as a car.
ON_BICYCLE 	The device is on a bicycle.
ON_FOOT 	The device is on a user who is walking or running.
RUNNING 	The device is on a user who is running.
STILL 	    The device is still (not moving).
TILTING 	The device angle relative to gravity changed significantly.
UNKNOWN 	Unable to detect the current activity.
WALKING
