# Table of Contents
1. [Overview of Solution](README.md#understanding-the-challenge)
2. [Decision to Ignore File Names](README.md#decision-to-ignore-file-names)
3. [Corner Case](README.md#corner-case)


# Overview of Solution
I created a UserSession class to hold all the relevant information for each solution.  This tracks the user's IP address, the date/time of the first and most recent request, the order of the first request (compared with other user sessions), and the session duration.

I tried a few different methods of keeping track of current user sessions, and I eventually selected one that had good performance across many different inactivity_period ranges.  As I discuss below, there are ways to make a faster solution if inactivity_period is small and there are smaller number of active users, but these solutions perform very badly if inactivity is large and the number of active user sessions is large.

I chose to create a dictionary that maps expiry time to a list of user sessions that will expire at that time (expiry_to_ip), and also a dictionary (current_users) that maps IP addresses to user sessions.  When a new request comes in, I check if this IP is already in my list of current users. If so, I update its user session, remove its IP from the old expiry_to_ip time, and add it to the new expiry_to_ip.

When a new timestamp is detected, I walk through the expiry times that are before the current time, and output the user sessions in those lists. I then pop those off the front of the expiry time ordered dict and delete the IPs from my current users dictionary.

I separated the lists by expiry time to keep the lists shorter, so that deletion & adding would be faster.  If it's known that inactivity_period is small and the list of current_users at any time is smaller, then it is faster just to have one list of expiry times.  In that case, with a new request I pull it from the list and then add it to the end.  I then walk through the list and output items who have expired and stop when I reach a user session that is still current. However, without dividing them into time buckets, that solution gets very slow if the list of current users is large.

# Decision to Ignore File Names
I read the problem description several times, but I can't find a reason that we need to track the file names
(cik, acc, and extention).  The description says we count a request as a new request, even if it is for the 
exact same file, so there doesn't seem to be any reason to save the file name.

I included an assertion in the function that reads the csv file header, to test if the file includes
the categories needed to form the file name requests.  If the file doesn't include the
categories cik, acc, and extention, the assertion will fail.  (This could obviously be taken out.)

I also have check for individual lines of the file that don't have the expected number of columns, and I skip those. I tested this on real EDGAR data and found this was a very small number of lines.  This check could also be easily removed.

# Corner Case
There is a corner case which doesn't seem to be addressed in the problem description.

Example:
inactivity time = 5 seconds

time: 1  -  IP1 makes a request
time: 2  -  IP2 makes a request
time: 3  -  IP1 makes another request
time: 10 - IP3 makes a request

Here we discover that both IP1 and IP2 have timed out.  I'm unclear if here the output order should be IP1 then IP2, or IP2 first since its session ended earlier?

The closest info I can find is:
If your program is able to detect multiple user sessions ending at the same time, it should write the results to the sessionization.txt output file in the same order as the user's first request for that session appeared in the input log.csvfile. 

The problem is IP1 and IP2 sessions don't end at the same time, they're just detected at the same time.

I chose to follow IP2 and then IP1 (output first in order of when the user session ends, and in a case of tie of user session end, then output in order of when user session began).  I included an alternate function that would yield the opposite order, but it is not currently hooked into the program.  