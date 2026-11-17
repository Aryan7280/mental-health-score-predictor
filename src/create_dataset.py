"""Script to create the dataset CSV from the provided data."""
import csv
import os

data_header = "Age,Gender,Country,Academic_Level,Most_Used_Platform,Purpose_Of_Use,Avg_Daily_Usage_Hours,Daily_Unlocks,Study_Hours,Physical_Activity_Hours,Sleep_Hours_Per_Night,Stress_Level,Mental_Health_Score"

# The dataset was provided inline in the user request - writing it here
# This is a subset of the full dataset provided
dataset_rows = """21,Male,Other,Undergraduate,Facebook,Networking,4.0,134,4.5,2.2,6.7,Medium,6.8
23,Female,Other,Graduate,LinkedIn,Education,1.6,73,7.0,2.4,8.6,Low,7.6
22,Male,Canada,Undergraduate,Instagram,Entertainment,4.6,166,4.0,1.8,6.7,Medium,7.0
18,Male,Other,High School,Snapchat,Entertainment,7.0,220,1.0,1.7,5.4,Very High,5.3
24,Female,Other,Graduate,Facebook,Networking,7.5,237,1.0,1.1,5.0,Very High,4.4
19,Female,Other,Undergraduate,Twitter,News,4.1,138,4.6,2.2,6.8,Low,6.8
22,Female,Other,Undergraduate,Instagram,Entertainment,8.0,246,1.0,0.9,5.2,Very High,5.3
21,Female,Other,Undergraduate,Facebook,Networking,6.0,209,1.0,1.3,5.7,High,4.7
24,Male,USA,Graduate,YouTube,Education,4.7,154,2.4,1.1,7.0,High,6.2
19,Male,Other,Undergraduate,TikTok,Entertainment,3.6,130,3.7,1.1,8.1,Medium,8.6
18,Male,Other,High School,LinkedIn,Education,4.1,133,4.3,1.8,7.3,High,6.8
18,Male,Other,High School,Snapchat,Entertainment,7.6,240,1.0,1.1,5.3,Very High,5.5
20,Male,Other,Undergraduate,Facebook,Networking,2.4,86,6.2,1.8,8.8,Low,8.5
23,Female,Other,Graduate,LinkedIn,Education,6.2,189,1.5,1.4,5.3,Very High,5.4
24,Male,India,Graduate,Instagram,Entertainment,2.7,120,5.4,2.4,8.6,Medium,7.8
18,Female,Other,High School,Twitter,News,5.2,155,3.3,0.6,7.0,High,6.3
22,Female,USA,Undergraduate,YouTube,Education,6.5,226,1.3,0.9,5.4,Very High,5.0
21,Male,Australia,Undergraduate,YouTube,Education,6.8,211,1.6,1.5,5.7,Very High,5.0
21,Male,Canada,Undergraduate,Facebook,Networking,6.9,212,1.0,1.5,5.9,High,5.0
20,Male,Other,Undergraduate,Instagram,Entertainment,5.5,183,2.2,1.0,6.8,Very High,6.8
23,Female,Other,Graduate,Facebook,Networking,2.0,100,5.7,2.6,7.9,Low,7.1
19,Female,Other,Undergraduate,Snapchat,Entertainment,5.1,170,1.9,2.2,7.1,High,6.5
24,Male,Other,Graduate,Facebook,Networking,2.0,110,6.4,2.9,7.8,Low,8.5
23,Male,India,Graduate,TikTok,Entertainment,2.0,113,5.6,2.5,7.2,Medium,8.6
23,Female,Other,Graduate,LinkedIn,Education,7.1,210,1.0,1.0,5.4,Very High,5.1
21,Male,Other,Undergraduate,Instagram,Entertainment,6.2,208,2.2,1.1,4.7,Very High,5.7
20,Female,Other,Undergraduate,LinkedIn,Education,2.8,107,5.6,2.5,8.3,Low,8.2
21,Female,Other,Undergraduate,TikTok,Entertainment,7.4,249,1.1,1.2,4.6,Very High,4.7
20,Female,USA,Undergraduate,TikTok,Entertainment,5.6,175,2.3,1.9,5.7,Very High,5.1
23,Female,USA,Graduate,YouTube,Education,2.7,103,5.0,2.4,7.8,Medium,7.7
20,Male,Australia,Undergraduate,YouTube,Education,7.3,235,1.0,1.6,6.0,High,5.7
24,Male,Other,Graduate,Snapchat,Entertainment,2.3,113,4.4,2.5,8.2,Low,8.1
19,Male,India,Undergraduate,LinkedIn,Education,5.6,170,1.2,2.0,6.9,High,6.6
22,Female,India,Undergraduate,Facebook,Networking,7.5,234,1.0,1.6,5.2,Very High,4.0
24,Male,UK,Graduate,TikTok,Entertainment,5.9,185,1.3,1.1,5.9,Very High,4.9
18,Male,UK,High School,Instagram,Entertainment,6.8,219,1.5,0.4,5.5,Very High,4.2
23,Male,Other,Graduate,Snapchat,Entertainment,6.7,214,1.0,2.1,5.5,Very High,5.0
22,Male,Other,Undergraduate,Instagram,Entertainment,4.5,176,3.2,2.0,6.1,High,6.6
22,Male,USA,Undergraduate,LinkedIn,Education,5.7,204,3.3,0.7,6.8,Medium,6.3
19,Female,Other,Undergraduate,Facebook,Networking,2.3,108,5.4,2.1,8.0,Low,8.5
24,Male,Other,Graduate,Twitter,News,8.3,259,1.0,1.3,5.5,Very High,4.3
21,Female,Other,Undergraduate,Twitter,News,6.5,222,1.0,1.2,5.7,High,4.2
22,Female,Other,Undergraduate,Twitter,News,6.9,204,1.0,1.0,5.3,Very High,4.5
20,Male,Other,Undergraduate,TikTok,Entertainment,8.1,256,1.0,1.7,4.5,Very High,5.7
20,Female,Other,Undergraduate,Instagram,Entertainment,7.2,235,1.0,0.7,4.8,Very High,4.2
20,Male,Other,Undergraduate,Twitter,News,4.1,132,4.6,1.6,6.6,Medium,6.7
18,Male,Other,High School,LinkedIn,Education,7.2,240,1.0,1.3,4.5,Very High,5.9
19,Female,Other,Undergraduate,Twitter,News,5.2,182,3.1,1.9,7.5,High,6.4
20,Male,UK,Undergraduate,Instagram,Entertainment,7.4,223,1.0,1.4,5.2,Very High,5.0
21,Male,Germany,Undergraduate,Instagram,Entertainment,3.6,134,3.9,2.6,7.1,Medium,8.5
22,Female,Other,Undergraduate,YouTube,Education,8.0,244,1.0,1.1,5.4,Very High,4.7
19,Female,Other,Undergraduate,Twitter,News,7.9,258,1.0,1.3,5.0,Very High,4.9
21,Female,India,Undergraduate,YouTube,Education,6.8,233,1.0,1.2,5.3,Very High,4.6
22,Male,Australia,Undergraduate,Twitter,News,7.3,239,1.0,1.2,5.5,Very High,4.7
21,Male,Other,Undergraduate,LinkedIn,Education,3.4,136,4.6,2.2,8.6,Low,8.8
21,Female,UK,Undergraduate,LinkedIn,Education,4.4,139,4.9,2.0,6.4,High,6.6
22,Male,Other,Undergraduate,Twitter,News,5.9,208,1.9,1.9,4.7,Very High,5.4
23,Male,UK,Graduate,TikTok,Entertainment,6.0,180,1.2,1.8,4.8,Very High,5.5
24,Female,Other,Graduate,TikTok,Entertainment,3.0,106,5.1,2.3,8.1,Medium,8.0
19,Male,Other,Undergraduate,Instagram,Entertainment,2.7,94,5.5,1.9,8.5,Low,7.6
24,Male,Other,Graduate,Instagram,Entertainment,1.7,104,7.4,2.6,7.7,Low,8.7
22,Female,Other,Undergraduate,YouTube,Education,6.2,199,2.5,1.4,5.3,Very High,5.5
21,Male,Other,Undergraduate,TikTok,Entertainment,1.8,79,6.5,2.6,7.9,Low,8.1
24,Female,Other,Graduate,Twitter,News,7.1,205,2.1,2.3,5.2,Very High,4.8
20,Female,India,Undergraduate,Snapchat,Entertainment,6.5,203,1.0,1.1,5.7,High,4.1
22,Male,Other,Undergraduate,Snapchat,Entertainment,7.6,243,1.0,1.3,5.9,Very High,6.0
19,Female,Other,Undergraduate,LinkedIn,Education,4.9,186,2.4,2.3,6.8,High,6.6
24,Female,Other,Graduate,Instagram,Entertainment,8.2,251,1.0,1.0,5.3,Very High,4.4
21,Male,Other,Undergraduate,Snapchat,Entertainment,5.2,179,1.7,2.9,6.4,High,6.1
19,Female,Other,Undergraduate,Instagram,Entertainment,2.9,130,5.6,2.1,7.9,Medium,7.7
23,Female,Other,Graduate,YouTube,Education,4.4,171,3.4,2.1,7.3,High,6.2
20,Female,Other,Undergraduate,Snapchat,Entertainment,4.0,136,2.8,1.6,7.5,Medium,7.2
23,Male,Other,Graduate,TikTok,Entertainment,6.4,224,1.0,1.2,5.2,Very High,4.6
22,Male,UK,Undergraduate,Facebook,Networking,8.2,249,1.0,1.1,4.6,Very High,4.1
22,Male,Other,Undergraduate,Twitter,News,5.1,189,3.6,2.1,6.5,High,6.9
19,Male,Other,Undergraduate,YouTube,Education,2.5,91,7.1,2.5,7.6,Medium,8.4
22,Male,Other,Undergraduate,Facebook,Networking,6.5,190,3.8,2.0,5.8,Very High,5.5
24,Female,Australia,Graduate,YouTube,Education,7.5,247,1.0,1.1,4.7,Very High,5.3
24,Male,Other,Graduate,LinkedIn,Education,3.2,131,4.0,2.0,7.1,Medium,8.6
23,Male,Germany,Graduate,Facebook,Networking,7.3,214,1.0,2.5,5.7,Very High,5.3
18,Female,USA,High School,Instagram,Entertainment,5.7,202,2.5,1.8,5.1,High,4.9
23,Female,Other,Graduate,Instagram,Entertainment,4.7,146,2.6,1.5,6.1,High,6.6
22,Male,Other,Undergraduate,Twitter,News,5.9,199,1.8,1.2,6.0,High,7.0
18,Male,Other,High School,YouTube,Education,7.4,218,1.0,0.7,5.0,Very High,4.7
18,Male,India,High School,TikTok,Entertainment,8.4,237,1.0,1.4,5.9,Very High,5.3
19,Male,India,Undergraduate,Instagram,Entertainment,8.1,259,1.0,0.8,4.8,Very High,4.1
22,Female,Other,Undergraduate,LinkedIn,Education,3.6,148,4.5,2.2,8.6,Medium,8.6
20,Male,Canada,Undergraduate,Twitter,News,5.8,174,2.1,1.5,5.6,High,5.5
21,Female,USA,Undergraduate,Snapchat,Entertainment,8.0,228,1.0,1.4,5.8,Very High,5.1
23,Male,India,Graduate,Snapchat,Entertainment,5.7,191,1.0,1.2,5.9,High,5.2
18,Male,Australia,High School,TikTok,Entertainment,8.0,226,1.0,0.5,4.6,Very High,5.8
23,Male,UK,Graduate,Instagram,Entertainment,3.7,146,4.3,2.2,8.4,Low,7.2
20,Male,Other,Undergraduate,Facebook,Networking,3.4,146,6.0,2.5,8.6,Low,8.7
23,Female,Australia,Graduate,Facebook,Networking,3.3,137,4.8,2.3,8.6,Medium,8.3
18,Female,Canada,High School,Snapchat,Entertainment,3.1,111,5.7,1.8,7.8,Medium,7.5
21,Male,Other,Undergraduate,LinkedIn,Education,8.2,236,1.0,1.3,6.0,Very High,5.4
20,Male,USA,Undergraduate,LinkedIn,Education,4.1,154,3.0,1.6,7.2,Medium,6.8
18,Female,Other,High School,TikTok,Entertainment,3.5,114,3.7,1.9,7.0,Medium,6.5
21,Male,Other,Undergraduate,Facebook,Networking,5.9,193,1.5,1.1,6.0,Very High,6.7
22,Male,Germany,Undergraduate,YouTube,Education,5.6,182,4.1,2.3,5.6,High,5.7
22,Male,Canada,Undergraduate,YouTube,Education,3.8,149,3.5,2.4,7.5,Medium,7.9
20,Male,Other,Undergraduate,Facebook,Networking,3.8,128,4.9,2.4,7.6,High,8.7
21,Female,Other,Undergraduate,Facebook,Networking,5.8,200,1.5,2.2,5.8,Very High,4.9
18,Male,Other,High School,Snapchat,Entertainment,3.7,144,5.0,3.5,7.5,Low,7.0
20,Female,Other,Undergraduate,LinkedIn,Education,2.9,106,5.4,1.4,8.3,Medium,8.4
21,Male,India,Undergraduate,LinkedIn,Education,4.5,151,3.4,1.5,7.5,Medium,7.0
21,Male,Other,Undergraduate,Snapchat,Entertainment,3.8,122,4.2,1.7,7.2,Medium,6.1
20,Male,Other,Undergraduate,Twitter,News,2.9,114,4.6,1.8,8.2,Low,7.6
23,Male,Other,Graduate,Twitter,News,5.0,160,3.4,1.2,6.7,High,6.8
21,Male,Other,Undergraduate,Instagram,Entertainment,6.5,191,1.1,1.2,5.6,Very High,4.3
22,Female,UK,Undergraduate,Instagram,Entertainment,3.6,137,3.4,1.5,7.1,Medium,6.0
18,Male,Other,High School,LinkedIn,Education,6.9,219,1.0,1.4,5.9,Very High,4.9
23,Female,Other,Graduate,TikTok,Entertainment,2.3,85,5.8,2.5,8.3,Low,8.8
19,Male,Other,Undergraduate,Snapchat,Entertainment,2.6,97,6.7,2.6,7.8,Low,8.8
22,Male,Other,Undergraduate,Instagram,Entertainment,6.2,183,1.9,1.7,4.8,Very High,5.9
24,Female,Australia,Graduate,Instagram,Entertainment,3.8,147,4.1,2.4,7.3,High,6.5
20,Female,Other,Undergraduate,Instagram,Entertainment,7.5,225,1.0,0.9,4.7,Very High,4.6
20,Male,India,Undergraduate,Instagram,Entertainment,3.8,122,5.2,3.1,8.2,High,7.8
21,Female,Other,Undergraduate,TikTok,Entertainment,8.4,242,1.0,1.0,5.3,Very High,5.9
24,Female,Other,Graduate,Twitter,News,5.9,211,1.8,0.6,4.9,Very High,4.1
22,Male,Australia,Undergraduate,YouTube,Education,6.0,185,2.9,1.0,6.8,High,6.9
23,Male,Other,Graduate,TikTok,Entertainment,3.5,139,4.8,1.3,8.5,Medium,7.3
21,Male,Other,Undergraduate,LinkedIn,Education,3.1,120,6.1,2.2,8.5,Low,8.5
19,Female,Canada,Undergraduate,Instagram,Entertainment,4.5,144,3.6,1.8,6.1,High,6.6
21,Female,Other,Undergraduate,Instagram,Entertainment,5.6,177,1.4,1.4,5.4,Very High,5.1
21,Female,Other,Undergraduate,Facebook,Networking,3.6,115,3.3,3.1,7.2,Medium,9.0
18,Male,UK,High School,LinkedIn,Education,7.3,236,2.0,1.4,5.3,Very High,4.0
21,Female,Other,Undergraduate,YouTube,Education,8.3,245,1.1,1.3,5.1,Very High,4.2
20,Female,India,Undergraduate,LinkedIn,Education,5.1,171,2.8,1.3,6.3,High,6.1
24,Female,India,Graduate,YouTube,Education,3.4,116,4.3,1.7,8.0,Medium,7.5
22,Female,Other,Undergraduate,Instagram,Entertainment,8.0,257,1.2,1.0,4.9,Very High,4.0
18,Male,Other,High School,LinkedIn,Education,3.7,125,3.4,2.2,6.9,Medium,6.9
18,Female,Other,High School,Instagram,Entertainment,3.3,129,4.0,1.2,8.3,Medium,8.5
21,Male,Other,Undergraduate,Twitter,News,5.3,191,3.2,1.6,7.3,High,6.7
23,Female,USA,Graduate,Instagram,Entertainment,3.8,148,3.9,2.1,7.4,Medium,7.1
24,Male,Other,Graduate,Instagram,Entertainment,3.7,141,4.3,2.0,7.4,Medium,8.7
22,Female,Other,Undergraduate,Twitter,News,1.9,107,6.0,2.1,9.0,Low,8.6
21,Female,Germany,Undergraduate,Facebook,Networking,4.4,142,3.9,1.6,6.5,High,6.5
18,Female,UK,High School,LinkedIn,Education,4.0,163,5.1,1.9,6.9,High,6.1
20,Male,Other,Undergraduate,YouTube,Education,5.6,187,2.5,1.6,5.3,Very High,5.4
22,Female,Other,Undergraduate,YouTube,Education,3.2,121,5.3,2.5,8.3,Low,7.5
21,Female,UK,Undergraduate,Snapchat,Entertainment,6.1,187,1.0,2.0,4.5,Very High,4.1
18,Female,Australia,High School,TikTok,Entertainment,5.3,186,2.7,1.5,7.1,High,6.4
18,Female,Other,High School,LinkedIn,Education,5.6,204,1.7,1.4,5.9,High,5.2
24,Male,Other,Graduate,TikTok,Entertainment,6.3,209,1.0,1.6,5.5,Very High,5.6
23,Female,Other,Graduate,Snapchat,Entertainment,5.8,171,1.5,1.9,6.9,High,6.1
23,Male,Canada,Graduate,Twitter,News,2.8,113,4.9,2.1,7.7,Medium,8.1
18,Female,Other,High School,YouTube,Education,6.5,216,2.2,1.8,5.6,Very High,4.3
23,Female,Australia,Graduate,Snapchat,Entertainment,4.6,155,2.3,2.3,6.9,High,6.6
18,Female,USA,High School,TikTok,Entertainment,7.0,230,1.0,1.9,4.9,Very High,5.4
18,Male,Other,High School,Twitter,News,1.8,98,5.8,3.4,8.0,Low,8.0
18,Male,Other,High School,Instagram,Entertainment,3.7,119,4.0,1.6,6.3,Medium,6.5
18,Male,Other,High School,TikTok,Entertainment,7.9,244,1.0,1.0,5.9,Very High,4.7
22,Male,India,Undergraduate,Snapchat,Entertainment,4.6,146,3.8,1.9,6.6,Medium,6.9
20,Female,Other,Undergraduate,Twitter,News,8.2,248,1.0,0.9,5.8,Very High,4.6
21,Female,Other,Undergraduate,TikTok,Entertainment,8.4,250,1.0,0.6,5.9,Very High,5.0
22,Female,Other,Undergraduate,TikTok,Entertainment,3.7,149,3.7,1.3,7.1,Medium,6.7
23,Female,Other,Graduate,TikTok,Entertainment,7.3,241,1.0,1.2,5.5,Very High,5.7
24,Female,Other,Graduate,Twitter,News,2.9,115,5.3,1.9,7.7,Medium,8.1
18,Male,Other,High School,Twitter,News,1.8,91,6.3,2.6,8.9,Low,8.6
23,Female,Other,Graduate,Snapchat,Entertainment,6.3,207,1.0,1.0,5.7,Very High,5.9
19,Male,Other,Undergraduate,YouTube,Education,3.4,136,4.7,1.6,8.6,Low,7.6
24,Male,Other,Graduate,Facebook,Networking,5.7,192,2.5,1.7,6.8,High,6.6
24,Female,Other,Graduate,Facebook,Networking,3.8,151,6.2,2.1,7.4,Medium,6.3
21,Male,Other,Undergraduate,TikTok,Entertainment,3.6,154,5.9,2.4,7.4,Medium,7.8
18,Female,Other,High School,Facebook,Networking,6.5,220,1.0,2.5,4.7,Very High,4.8
24,Female,Other,Graduate,YouTube,Education,7.8,225,1.0,1.2,5.4,Very High,5.6
22,Male,USA,Undergraduate,TikTok,Entertainment,3.7,136,3.1,2.3,7.1,Medium,7.5
18,Male,Other,High School,LinkedIn,Education,3.7,135,3.8,1.5,6.7,Medium,6.2
19,Male,India,Undergraduate,Facebook,Networking,5.7,187,2.6,0.9,7.2,Very High,6.2
18,Female,USA,High School,Facebook,Networking,3.3,128,5.7,3.0,8.0,Medium,8.8
21,Female,Other,Undergraduate,Facebook,Networking,3.3,135,4.1,1.7,8.2,Low,8.6
20,Male,Other,Undergraduate,Snapchat,Entertainment,1.8,86,5.7,2.0,8.5,Low,7.5
23,Female,Canada,Graduate,Snapchat,Entertainment,5.4,170,1.0,1.6,7.1,High,6.5
20,Female,Other,Undergraduate,YouTube,Education,5.9,190,2.0,1.5,4.9,High,5.1
20,Male,Australia,Undergraduate,LinkedIn,Education,3.3,141,3.9,1.7,8.8,Medium,7.9
24,Male,Other,Graduate,Snapchat,Entertainment,7.2,217,1.0,1.0,4.7,Very High,5.4
18,Male,Other,High School,Snapchat,Entertainment,1.6,65,5.7,3.2,8.1,Low,8.6
24,Female,Other,Graduate,YouTube,Education,3.4,149,4.5,1.7,8.2,Low,8.2
22,Female,Other,Undergraduate,Twitter,News,2.6,97,4.0,1.7,7.5,Low,8.5
20,Female,USA,Undergraduate,Twitter,News,5.1,176,1.7,2.2,6.5,High,6.9
23,Female,Other,Graduate,Instagram,Entertainment,5.8,202,3.9,1.8,6.2,High,6.2
19,Male,Australia,Undergraduate,Instagram,Entertainment,4.3,142,2.7,1.6,6.7,Medium,6.3
20,Female,Other,Undergraduate,TikTok,Entertainment,2.5,100,4.6,1.6,7.7,Medium,8.5
22,Female,Other,Undergraduate,YouTube,Education,5.8,181,3.7,1.2,6.0,High,4.7
20,Male,Other,Undergraduate,LinkedIn,Education,2.5,92,7.8,2.3,7.4,Medium,8.2
19,Female,Australia,Undergraduate,TikTok,Entertainment,6.4,191,1.0,2.0,5.5,Very High,4.4
20,Male,Other,Undergraduate,Twitter,News,7.8,227,1.0,0.5,5.2,Very High,5.2
20,Male,USA,Undergraduate,Twitter,News,6.5,205,1.8,1.3,4.5,Very High,4.2
22,Female,India,Undergraduate,YouTube,Education,3.0,121,6.4,2.6,8.9,Low,7.1
24,Female,Other,Graduate,Facebook,Networking,1.5,62,5.7,1.4,7.2,Low,7.6
19,Female,Other,Undergraduate,TikTok,Entertainment,8.1,260,1.0,1.5,5.6,Very High,5.5
21,Female,Other,Undergraduate,Snapchat,Entertainment,2.6,117,6.0,1.8,7.4,Medium,7.4
18,Male,Other,High School,Snapchat,Entertainment,2.7,94,5.6,2.5,8.5,Low,7.6
23,Female,Other,Graduate,Snapchat,Entertainment,2.4,118,5.3,2.5,7.6,Medium,7.6
23,Female,Other,Graduate,TikTok,Entertainment,6.6,191,1.3,1.9,6.0,High,5.0
22,Male,USA,Undergraduate,YouTube,Education,3.8,142,3.1,2.3,7.9,Medium,7.3
21,Female,USA,Undergraduate,LinkedIn,Education,5.8,188,2.0,0.4,7.0,High,6.4
20,Male,Other,Undergraduate,LinkedIn,Education,8.2,249,1.0,0.6,6.0,Very High,5.7
22,Male,Other,Undergraduate,Facebook,Networking,4.5,175,3.7,1.9,6.0,High,6.3
18,Female,Other,High School,Twitter,News,5.6,202,2.0,1.5,4.8,Very High,5.9
20,Male,Other,Undergraduate,TikTok,Entertainment,3.5,123,4.9,2.4,7.9,High,7.8
23,Female,Other,Graduate,YouTube,Education,2.9,120,5.9,2.7,7.3,Medium,8.5
19,Male,USA,Undergraduate,TikTok,Entertainment,6.6,228,1.5,1.7,5.9,Very High,5.0
24,Male,India,Graduate,Twitter,News,8.0,254,1.0,0.9,5.1,Very High,5.3
18,Male,Other,High School,LinkedIn,Education,7.3,242,1.0,0.3,5.1,Very High,4.1
19,Female,Other,Undergraduate,Twitter,News,2.5,104,5.5,2.1,7.3,Low,8.3
19,Male,Canada,Undergraduate,TikTok,Entertainment,2.6,101,4.8,2.6,8.4,Low,8.2
24,Male,India,Graduate,Twitter,News,2.3,102,6.0,1.9,8.3,Low,8.9
21,Male,Other,Undergraduate,Twitter,News,5.3,189,2.6,2.0,7.3,Medium,6.1
19,Female,Other,Undergraduate,Snapchat,Entertainment,7.7,254,2.0,1.5,5.7,Very High,5.3
19,Female,Other,Undergraduate,Snapchat,Entertainment,4.6,167,4.7,1.9,6.2,High,6.2
21,Male,Other,Undergraduate,YouTube,Education,5.9,200,2.4,0.0,7.1,High,6.4
18,Male,Other,High School,LinkedIn,Education,7.5,232,1.0,0.5,5.0,Very High,5.4
18,Male,Canada,High School,LinkedIn,Education,6.3,194,1.0,2.4,6.0,High,6.0
19,Male,Other,Undergraduate,YouTube,Education,5.3,173,3.7,1.4,7.0,High,6.7
23,Female,Other,Graduate,TikTok,Entertainment,1.6,84,6.6,1.6,8.7,Low,8.9
20,Male,Other,Undergraduate,LinkedIn,Education,6.5,219,1.9,2.0,4.5,Very High,4.7
20,Female,Other,Undergraduate,Twitter,News,8.2,251,1.0,1.0,5.0,Very High,5.9
23,Male,Other,Graduate,LinkedIn,Education,6.1,208,2.6,2.0,5.9,Very High,4.8
22,Male,Other,Undergraduate,LinkedIn,Education,5.7,168,2.7,1.7,7.3,High,6.9
19,Female,Other,Undergraduate,Twitter,News,5.1,182,2.0,2.0,7.1,High,6.6
24,Male,Other,Graduate,Twitter,News,3.8,140,3.8,2.2,6.3,Medium,6.2
20,Male,India,Undergraduate,YouTube,Education,5.7,206,2.5,1.9,5.1,Very High,4.2
20,Female,UK,Undergraduate,Facebook,Networking,6.6,208,1.4,2.5,5.3,Very High,4.6
20,Male,USA,Undergraduate,Instagram,Entertainment,8.3,251,1.0,1.4,5.1,Very High,5.8
20,Male,Other,Undergraduate,Instagram,Entertainment,7.1,207,1.0,0.4,6.0,Very High,4.5
18,Male,Other,High School,Facebook,Networking,3.0,132,4.8,2.5,8.4,Medium,7.9
22,Male,Other,Undergraduate,Instagram,Entertainment,8.5,265,1.0,1.4,6.0,Very High,5.3
24,Female,Other,Graduate,Twitter,News,3.5,146,5.7,2.7,7.2,Medium,7.3
18,Female,USA,High School,Twitter,News,3.8,123,2.1,1.8,8.4,Medium,7.2
19,Male,Other,Undergraduate,Instagram,Entertainment,2.0,83,5.8,3.1,7.1,Medium,8.2
18,Female,Other,High School,Twitter,News,4.2,165,3.9,2.4,6.9,High,6.8
21,Female,Other,Undergraduate,YouTube,Education,4.5,138,3.7,3.2,6.1,High,6.3
24,Female,Other,Graduate,YouTube,Education,4.2,150,3.5,1.6,7.3,High,6.1
24,Female,Other,Graduate,Facebook,Networking,5.6,181,1.0,1.3,5.5,High,4.1
21,Female,India,Undergraduate,Facebook,Networking,3.1,139,5.2,2.1,7.2,Medium,8.5
19,Female,Other,Undergraduate,Instagram,Entertainment,5.9,206,3.5,1.3,5.5,High,4.0
22,Female,India,Undergraduate,YouTube,Education,7.5,247,1.0,0.7,5.5,Very High,4.7
20,Male,Other,Undergraduate,Snapchat,Entertainment,3.8,131,4.9,0.7,6.7,High,6.2
21,Female,Other,Undergraduate,LinkedIn,Education,3.3,130,4.4,2.0,8.9,Low,7.9
24,Male,Other,Graduate,Facebook,Networking,4.1,155,3.9,2.2,6.1,Medium,6.0
19,Female,Other,Undergraduate,YouTube,Education,6.8,233,1.0,1.1,5.6,Very High,5.0
23,Male,Other,Graduate,Snapchat,Entertainment,3.5,112,4.2,3.1,7.0,Medium,6.0
19,Male,Canada,Undergraduate,YouTube,Education,3.4,149,5.6,2.2,8.5,Low,8.0
19,Male,Other,Undergraduate,LinkedIn,Education,5.8,184,2.7,2.2,6.3,Very High,6.4
19,Female,India,Undergraduate,TikTok,Entertainment,6.0,180,3.4,1.6,6.8,High,6.5
23,Female,Other,Graduate,TikTok,Entertainment,3.0,124,5.9,2.7,8.6,Low,7.7
19,Male,USA,Undergraduate,Twitter,News,5.0,181,3.4,1.9,7.5,High,6.6
24,Female,India,Graduate,Twitter,News,5.5,167,3.9,2.3,4.6,High,5.1
20,Female,India,Undergraduate,TikTok,Entertainment,5.3,158,3.1,1.7,6.0,Very High,6.5
21,Male,Canada,Undergraduate,Facebook,Networking,5.6,200,3.1,1.8,6.0,High,6.3
19,Female,India,Undergraduate,Facebook,Networking,5.8,207,2.0,1.7,7.4,High,6.5
18,Male,Other,High School,Twitter,News,2.2,86,5.9,2.3,8.3,Medium,7.4
24,Male,Other,Graduate,LinkedIn,Education,1.7,103,5.7,2.8,8.4,Low,7.6
21,Male,India,Undergraduate,Instagram,Entertainment,3.0,136,5.8,3.4,7.2,Medium,7.2
18,Female,Other,High School,TikTok,Entertainment,4.7,181,2.4,1.7,6.6,High,7.0
23,Male,Other,Graduate,YouTube,Education,6.2,188,2.4,1.7,5.9,High,5.6
18,Male,Other,High School,TikTok,Entertainment,6.2,203,1.6,2.1,5.9,Very High,4.9
20,Female,Other,Undergraduate,Instagram,Entertainment,1.9,111,7.0,3.1,7.8,Low,7.8
23,Male,UK,Graduate,LinkedIn,Education,2.6,126,6.0,2.4,8.8,Low,8.1
18,Male,Other,High School,Facebook,Networking,5.9,196,3.6,0.3,6.1,High,6.2
20,Male,Other,Undergraduate,LinkedIn,Education,3.9,129,4.7,2.3,6.9,Medium,6.6
22,Female,India,Undergraduate,Instagram,Entertainment,7.1,205,1.0,0.1,5.1,Very High,4.1
19,Male,USA,Undergraduate,Twitter,News,3.9,132,4.0,2.8,6.1,Medium,6.0
20,Male,Other,Undergraduate,TikTok,Entertainment,8.0,227,1.0,1.1,4.9,Very High,4.8
24,Male,Other,Graduate,Snapchat,Entertainment,5.9,179,1.7,2.0,6.1,High,6.1
24,Female,Australia,Graduate,Facebook,Networking,8.4,237,1.0,0.4,5.9,Very High,5.5
21,Female,Other,Undergraduate,YouTube,Education,7.5,242,1.0,0.3,4.7,Very High,6.0
20,Female,Australia,Undergraduate,Snapchat,Entertainment,7.5,235,1.0,1.3,5.2,Very High,4.8
19,Male,India,Undergraduate,Snapchat,Entertainment,5.3,177,1.9,1.7,7.0,Medium,6.8
18,Male,Canada,High School,Twitter,News,6.2,212,1.8,1.2,4.7,Very High,4.2
19,Male,Other,Undergraduate,Facebook,Networking,5.2,171,1.8,1.7,6.5,High,6.1
21,Male,Other,Undergraduate,Facebook,Networking,5.5,178,2.0,3.0,5.7,High,6.0
20,Male,Canada,Undergraduate,Instagram,Entertainment,7.9,230,1.0,1.4,4.7,Very High,5.2
23,Male,Other,Graduate,Snapchat,Entertainment,7.7,234,1.2,1.6,5.3,Very High,4.5
20,Male,Other,Undergraduate,YouTube,Education,3.9,128,4.6,2.4,6.7,Medium,6.0
21,Female,Other,Undergraduate,LinkedIn,Education,3.9,145,2.3,2.8,6.9,Medium,6.1
21,Female,Canada,Undergraduate,YouTube,Education,5.9,211,2.3,1.4,6.0,High,5.1
18,Male,Other,High School,Facebook,Networking,3.8,141,4.3,1.0,8.4,Low,8.3
19,Male,Other,Undergraduate,TikTok,Entertainment,7.4,221,1.0,1.1,5.5,Very High,4.1
20,Female,Other,Undergraduate,LinkedIn,Education,7.2,232,2.1,1.6,5.9,Very High,4.2
19,Male,Other,Undergraduate,TikTok,Entertainment,6.1,209,1.0,1.0,4.6,Very High,4.9
22,Male,India,Undergraduate,Facebook,Networking,3.9,140,3.6,1.9,8.6,Low,8.3
20,Female,Australia,Undergraduate,LinkedIn,Education,5.6,175,2.9,1.3,4.9,High,5.9
22,Female,Other,Undergraduate,Snapchat,Entertainment,6.3,210,1.0,2.2,5.1,Very High,5.7
22,Female,Other,Undergraduate,Facebook,Networking,2.3,89,6.9,2.8,9.0,Low,7.1
19,Male,India,Undergraduate,YouTube,Education,6.4,224,1.9,1.7,5.9,Very High,5.9
19,Female,USA,Undergraduate,YouTube,Education,5.2,167,3.5,2.0,7.0,High,6.7
21,Female,Germany,Undergraduate,LinkedIn,Education,7.1,216,1.0,1.2,5.5,Very High,4.4
23,Female,India,Graduate,Instagram,Entertainment,6.1,206,2.6,1.6,4.6,Very High,5.2
20,Male,Other,Undergraduate,Twitter,News,7.9,222,1.0,0.4,5.4,Very High,5.3
19,Female,Canada,Undergraduate,Twitter,News,7.4,218,1.0,0.1,4.6,Very High,5.8
20,Female,UK,Undergraduate,TikTok,Entertainment,7.1,207,1.1,1.3,5.9,Very High,4.2
24,Male,Other,Graduate,YouTube,Education,5.2,170,3.0,1.9,6.5,Very High,6.0
21,Male,Other,Undergraduate,Twitter,News,5.8,192,1.5,2.2,5.4,High,4.9
21,Female,Other,Undergraduate,YouTube,Education,5.8,177,2.1,2.3,4.9,Very High,4.1
19,Female,Other,Undergraduate,Twitter,News,2.2,93,5.7,3.2,7.6,Low,8.9
24,Male,Germany,Graduate,Snapchat,Entertainment,6.9,227,1.4,0.8,5.3,Very High,4.3
22,Female,Other,Undergraduate,Snapchat,Entertainment,6.9,234,1.9,1.1,4.6,Very High,4.3
20,Female,Other,Undergraduate,Facebook,Networking,6.3,182,1.0,1.7,5.9,High,5.3
24,Female,Other,Graduate,Twitter,News,4.4,160,3.5,3.2,6.2,Medium,6.2
23,Male,Germany,Graduate,TikTok,Entertainment,3.2,106,6.0,2.9,8.9,Low,8.0
21,Female,UK,Undergraduate,Facebook,Networking,7.6,235,1.0,1.7,5.9,Very High,4.7
22,Female,Other,Undergraduate,Instagram,Entertainment,3.5,147,3.8,1.9,8.7,Medium,8.0
24,Male,Australia,Graduate,Snapchat,Entertainment,4.6,171,3.6,1.4,6.4,High,6.8
21,Female,Other,Undergraduate,Twitter,News,6.1,186,2.6,1.9,4.5,Very High,5.3
22,Male,Other,Undergraduate,TikTok,Entertainment,3.3,117,4.7,1.6,8.2,Medium,7.4
24,Male,Other,Graduate,LinkedIn,Education,5.2,186,3.9,1.6,6.9,Medium,6.9
20,Female,UK,Undergraduate,LinkedIn,Education,5.9,204,2.8,1.5,5.5,Very High,4.3
23,Female,Other,Graduate,Twitter,News,6.1,188,2.6,2.3,5.1,Very High,4.9
21,Male,Other,Undergraduate,TikTok,Entertainment,3.9,122,4.5,1.8,7.7,Medium,7.5
20,Male,Other,Undergraduate,Facebook,Networking,7.2,222,2.7,0.0,4.6,Very High,4.4
22,Female,Other,Undergraduate,LinkedIn,Education,7.9,246,1.0,1.3,5.6,Very High,5.3
18,Female,Other,High School,TikTok,Entertainment,7.5,229,1.0,0.8,5.8,Very High,4.6
24,Female,USA,Graduate,Twitter,News,6.4,222,2.9,1.4,6.0,High,5.2
21,Male,India,Undergraduate,Facebook,Networking,7.6,247,1.0,1.1,5.8,Very High,4.8
18,Female,Other,High School,Twitter,News,5.8,201,2.3,1.4,5.0,Very High,5.6
23,Female,Canada,Graduate,Twitter,News,2.8,95,6.2,2.7,7.4,Low,8.4
20,Male,UK,Undergraduate,Facebook,Networking,6.3,216,1.0,0.7,4.7,Very High,4.3
23,Female,Canada,Graduate,Snapchat,Entertainment,4.3,162,2.7,1.7,7.4,Medium,6.1
20,Female,Germany,Undergraduate,Snapchat,Entertainment,8.2,244,1.0,1.3,4.8,Very High,4.0
18,Male,Other,High School,Twitter,News,6.9,220,1.0,1.0,5.9,Very High,4.1
22,Male,Other,Undergraduate,Facebook,Networking,5.7,199,2.7,0.8,4.6,High,4.8
24,Female,Other,Graduate,TikTok,Entertainment,5.9,208,2.5,1.9,5.8,High,5.6
22,Female,Other,Undergraduate,Snapchat,Entertainment,1.9,94,6.3,3.1,8.4,Low,8.1
23,Male,Other,Graduate,Snapchat,Entertainment,7.7,218,1.0,1.1,5.1,Very High,5.7
24,Male,Other,Graduate,Twitter,News,3.2,129,3.0,1.2,7.8,Medium,8.4
24,Female,Other,Graduate,TikTok,Entertainment,1.7,94,6.3,2.9,8.7,Low,8.0
21,Male,India,Undergraduate,TikTok,Entertainment,7.8,222,1.0,0.2,5.0,Very High,4.5
21,Male,Germany,Undergraduate,Instagram,Entertainment,1.9,104,6.5,2.7,8.7,Low,8.1
19,Male,USA,Undergraduate,TikTok,Entertainment,7.5,220,1.1,0.7,4.9,Very High,4.2
21,Male,USA,Undergraduate,YouTube,Education,7.1,237,1.0,0.6,5.9,Very High,4.7
20,Female,Canada,Undergraduate,Facebook,Networking,4.3,154,4.3,1.7,6.4,High,6.2
23,Male,Other,Graduate,Twitter,News,8.2,241,1.0,0.9,5.7,Very High,4.9
21,Female,Other,Undergraduate,TikTok,Entertainment,8.3,234,1.0,0.6,4.6,Very High,4.8
18,Female,Other,High School,Facebook,Networking,8.1,227,1.0,1.3,4.7,Very High,5.6
19,Male,Other,Undergraduate,TikTok,Entertainment,4.8,174,3.1,1.6,7.0,High,6.1
20,Female,Other,Undergraduate,YouTube,Education,2.7,107,5.5,2.8,7.8,Low,7.5
18,Male,UK,High School,LinkedIn,Education,7.5,245,1.2,1.3,5.4,Very High,4.2
24,Male,Other,Graduate,LinkedIn,Education,3.8,129,3.9,1.7,7.9,Low,8.8
21,Female,Other,Undergraduate,Instagram,Entertainment,5.9,208,2.5,1.1,4.9,High,5.6
23,Male,Other,Graduate,Instagram,Entertainment,3.4,147,4.4,1.3,8.4,Low,7.3
19,Male,USA,Undergraduate,Twitter,News,3.9,126,4.0,2.2,6.6,Medium,6.9
19,Male,Other,Undergraduate,TikTok,Entertainment,7.9,247,1.0,0.8,5.4,Very High,4.2
24,Male,Other,Graduate,Instagram,Entertainment,2.1,114,4.3,1.3,7.2,Low,7.2
18,Male,Other,High School,Snapchat,Entertainment,6.3,194,1.0,1.2,4.5,Very High,5.2
24,Male,Other,Graduate,LinkedIn,Education,4.4,137,2.4,1.4,7.5,High,6.8
21,Female,Australia,Undergraduate,Twitter,News,3.7,152,2.4,2.9,6.7,Medium,6.6
24,Female,USA,Graduate,YouTube,Education,7.4,228,1.0,0.3,5.9,Very High,4.3
21,Female,India,Undergraduate,LinkedIn,Education,4.4,136,4.2,1.2,6.4,High,6.4
23,Male,Other,Graduate,LinkedIn,Education,2.5,120,5.3,2.9,7.1,Low,8.8
19,Female,Germany,Undergraduate,Facebook,Networking,6.5,214,1.7,2.1,5.9,Very High,5.3
21,Female,Other,Undergraduate,Twitter,News,3.7,119,5.2,1.7,8.2,Low,7.3
22,Female,Australia,Undergraduate,TikTok,Entertainment,7.6,225,1.5,0.8,5.2,Very High,4.5
18,Male,India,High School,Instagram,Entertainment,6.8,195,1.1,1.6,4.6,Very High,4.1
23,Male,Other,Graduate,Instagram,Entertainment,7.5,250,1.6,0.0,5.7,Very High,4.5
24,Female,Other,Graduate,YouTube,Education,7.1,202,1.0,0.3,4.7,Very High,4.0
24,Male,Canada,Graduate,Twitter,News,6.7,223,1.0,1.2,6.0,Very High,4.5
19,Male,Other,Undergraduate,Twitter,News,3.6,135,3.9,2.9,6.9,Medium,6.8
21,Male,Other,Undergraduate,Snapchat,Entertainment,3.1,125,3.7,2.0,7.5,Medium,8.9
21,Male,Other,Undergraduate,TikTok,Entertainment,5.2,187,2.1,1.8,6.4,High,7.0
18,Female,Other,High School,LinkedIn,Education,4.7,177,3.0,2.4,6.2,High,6.4
19,Male,Other,Undergraduate,YouTube,Education,2.9,102,5.7,3.3,8.0,Medium,7.4
23,Female,Other,Graduate,Snapchat,Entertainment,3.6,115,5.8,1.8,8.4,Medium,8.4
20,Female,USA,Undergraduate,TikTok,Entertainment,5.6,169,1.3,1.6,6.8,High,6.5
22,Male,Other,Undergraduate,Facebook,Networking,5.2,182,3.1,2.6,7.2,Medium,6.0
24,Female,Canada,Graduate,YouTube,Education,1.7,89,5.5,1.8,7.1,Medium,7.5
19,Male,Other,Undergraduate,YouTube,Education,3.7,120,4.7,2.6,7.0,Medium,6.7
22,Male,Australia,Undergraduate,Instagram,Entertainment,1.5,71,6.4,2.1,8.7,Low,8.6
21,Male,India,Undergraduate,Instagram,Entertainment,4.4,156,2.1,2.0,7.3,Medium,6.1
21,Male,Other,Undergraduate,Instagram,Entertainment,7.4,239,1.3,1.0,4.8,High,4.8
22,Female,Other,Undergraduate,Facebook,Networking,4.0,138,3.5,1.5,6.0,High,6.2
20,Male,Other,Undergraduate,Twitter,News,2.0,112,5.6,2.0,7.7,Low,7.7
20,Male,Other,Undergraduate,LinkedIn,Education,5.7,206,1.4,1.7,5.5,High,6.0
18,Male,Other,High School,LinkedIn,Education,4.5,167,3.0,2.4,6.1,High,6.4
24,Male,Canada,Graduate,TikTok,Entertainment,3.2,123,5.1,2.1,7.5,Medium,8.0
20,Female,Other,Undergraduate,Twitter,News,6.7,227,1.1,1.4,5.1,High,5.7
21,Male,Other,Undergraduate,Snapchat,Entertainment,8.3,261,1.0,1.2,4.7,Very High,5.0
18,Female,Other,High School,Snapchat,Entertainment,3.2,125,5.1,1.7,7.8,Medium,8.5
19,Female,Other,Undergraduate,TikTok,Entertainment,5.9,189,3.2,1.9,6.3,High,6.8
21,Male,Other,Undergraduate,YouTube,Education,5.2,188,2.5,2.1,6.6,High,6.3
22,Male,Other,Undergraduate,LinkedIn,Education,3.5,134,3.3,3.4,8.1,Low,7.2
22,Male,USA,Undergraduate,YouTube,Education,8.0,232,1.0,0.8,5.2,Very High,4.7
21,Female,Other,Undergraduate,TikTok,Entertainment,7.3,246,1.0,0.9,5.8,Very High,5.6
21,Male,Other,Undergraduate,YouTube,Education,6.3,184,2.6,1.8,5.9,Very High,4.5
21,Male,Other,Undergraduate,Snapchat,Entertainment,8.4,262,1.0,1.3,4.7,Very High,5.4
19,Male,USA,Undergraduate,LinkedIn,Education,2.4,111,5.5,2.1,7.2,Low,8.6
23,Female,Other,Graduate,Instagram,Entertainment,6.4,208,1.9,1.2,5.4,High,5.4
24,Female,Other,Graduate,LinkedIn,Education,4.8,147,4.8,2.1,6.7,High,6.4
23,Female,Other,Graduate,Snapchat,Entertainment,7.7,236,2.0,0.7,5.3,Very High,5.3
21,Male,Other,Undergraduate,Facebook,Networking,6.7,227,1.4,1.1,4.6,Very High,4.5
20,Female,Other,Undergraduate,Facebook,Networking,2.9,106,5.2,2.3,8.4,Medium,8.4
19,Female,Other,Undergraduate,LinkedIn,Education,8.3,259,1.0,1.4,5.0,Very High,4.5
18,Male,Other,High School,LinkedIn,Education,2.5,121,4.8,2.1,8.7,Medium,8.6
18,Female,Other,High School,Facebook,Networking,6.2,218,2.1,0.5,5.1,Very High,5.2
24,Male,Other,Graduate,Snapchat,Entertainment,2.8,115,5.2,1.3,8.5,Medium,7.6
18,Female,Other,High School,LinkedIn,Education,4.8,157,3.5,1.2,6.8,Medium,6.3
20,Male,India,Undergraduate,Instagram,Entertainment,7.6,242,1.0,0.4,5.4,Very High,4.1
19,Female,Other,Undergraduate,Facebook,Networking,4.5,156,2.2,1.8,6.2,High,6.6
21,Male,Other,Undergraduate,TikTok,Entertainment,2.6,115,3.7,1.8,7.4,Low,8.9
22,Female,Other,Undergraduate,YouTube,Education,2.3,111,4.8,2.1,8.8,Low,9.0
20,Male,Other,Undergraduate,Twitter,News,2.8,123,4.8,1.9,8.2,Medium,7.3
19,Male,Other,Undergraduate,Instagram,Entertainment,7.0,209,1.0,1.0,4.7,Very High,5.5
23,Female,Other,Graduate,YouTube,Education,5.6,195,3.9,2.3,6.6,High,6.5
21,Male,UK,Undergraduate,Instagram,Entertainment,3.5,133,5.4,2.5,8.5,Medium,8.4
18,Female,USA,High School,Twitter,News,5.9,209,1.3,1.5,4.5,High,5.8
19,Male,Other,Undergraduate,LinkedIn,Education,2.4,111,5.9,2.2,8.4,Low,7.6
20,Female,Other,Undergraduate,Facebook,Networking,6.4,220,1.3,1.2,5.5,Very High,4.3
21,Female,Other,Undergraduate,Twitter,News,2.7,131,5.1,2.5,7.5,Medium,7.9
24,Male,India,Graduate,Instagram,Entertainment,8.2,269,1.0,1.2,4.8,Very High,4.5
22,Male,Other,Undergraduate,Instagram,Entertainment,1.9,101,6.6,2.1,7.2,Medium,8.2
21,Male,Other,Undergraduate,Instagram,Entertainment,5.4,183,2.3,1.7,6.6,High,6.5
21,Female,USA,Undergraduate,Snapchat,Entertainment,6.1,181,2.8,0.5,5.3,High,6.0
23,Female,Other,Graduate,Instagram,Entertainment,7.4,225,1.0,1.3,5.3,Very High,5.5
24,Male,Germany,Graduate,LinkedIn,Education,7.1,221,1.0,1.6,5.8,Very High,4.2
21,Male,Australia,Undergraduate,Instagram,Entertainment,5.7,198,4.4,1.4,7.5,Medium,6.6
20,Female,Other,Undergraduate,Twitter,News,1.8,93,6.4,3.5,7.2,Low,7.5
22,Female,Other,Undergraduate,YouTube,Education,7.9,239,1.2,0.6,5.1,Very High,4.9
24,Male,Other,Graduate,Twitter,News,8.1,232,1.0,1.1,6.0,Very High,4.8
24,Female,Other,Graduate,Instagram,Entertainment,3.6,143,4.9,2.1,6.9,Medium,6.5
21,Male,India,Undergraduate,Facebook,Networking,7.8,237,1.0,1.0,5.5,Very High,5.7
22,Female,Other,Undergraduate,Instagram,Entertainment,7.0,201,1.0,1.2,5.9,Very High,4.0
22,Female,Canada,Undergraduate,TikTok,Entertainment,7.7,228,1.0,1.1,5.8,Very High,4.2
24,Female,Other,Graduate,Snapchat,Entertainment,5.7,202,2.6,2.0,6.9,High,6.4
19,Female,Other,Undergraduate,LinkedIn,Education,4.9,151,2.4,2.5,6.6,High,6.5
24,Female,USA,Graduate,Instagram,Entertainment,7.6,231,1.0,1.1,5.3,Very High,4.9
19,Female,India,Undergraduate,Snapchat,Entertainment,8.5,257,1.0,1.3,5.8,Very High,4.8
22,Female,India,Undergraduate,TikTok,Entertainment,6.6,193,1.7,1.0,5.3,Very High,5.0
20,Female,Other,Undergraduate,Snapchat,Entertainment,7.5,218,1.0,1.5,5.9,Very High,4.6
24,Female,Other,Graduate,YouTube,Education,7.5,249,1.0,0.7,4.8,Very High,5.4
23,Male,Other,Graduate,Facebook,Networking,8.2,252,1.0,1.5,5.7,Very High,4.0
20,Female,UK,Undergraduate,YouTube,Education,5.3,165,3.4,2.8,7.1,High,6.6
22,Female,Other,Undergraduate,LinkedIn,Education,4.9,153,1.6,1.7,7.0,High,6.7
21,Female,USA,Undergraduate,Instagram,Entertainment,5.8,187,1.9,0.5,5.8,Very High,5.1
23,Male,Other,Graduate,LinkedIn,Education,6.4,213,1.0,1.1,5.4,Very High,4.3
18,Female,Other,High School,Snapchat,Entertainment,3.8,149,3.0,2.7,6.2,Medium,6.8
22,Female,USA,Undergraduate,Facebook,Networking,3.8,127,5.3,2.3,6.9,High,6.5
18,Male,Australia,High School,Twitter,News,4.0,154,4.7,2.1,7.4,Medium,6.5
21,Male,Other,Undergraduate,LinkedIn,Education,8.0,260,1.0,1.5,5.5,Very High,5.6
23,Female,Other,Graduate,Snapchat,Entertainment,8.3,241,1.0,1.2,5.6,Very High,5.8
19,Male,USA,Undergraduate,LinkedIn,Education,5.8,171,1.0,2.2,5.3,High,5.0
23,Male,Other,Graduate,Snapchat,Entertainment,6.2,218,1.4,1.9,5.3,Very High,5.0
18,Male,Other,High School,Snapchat,Entertainment,2.3,102,7.6,3.2,7.5,Medium,8.2
19,Female,Other,Undergraduate,YouTube,Education,6.2,211,2.1,1.6,5.8,Very High,4.3
20,Female,Other,Undergraduate,Instagram,Entertainment,7.0,212,1.0,1.7,4.5,Very High,5.9
24,Male,Other,Graduate,LinkedIn,Education,3.8,131,4.6,1.9,7.2,Low,8.9
18,Female,Other,High School,TikTok,Entertainment,3.3,116,3.5,1.9,8.6,Low,8.7
19,Female,USA,Undergraduate,Instagram,Entertainment,1.5,70,6.3,3.5,8.2,Low,8.2
18,Male,Other,High School,YouTube,Education,6.7,210,1.4,1.4,5.8,Very High,4.5
23,Male,India,Graduate,YouTube,Education,2.9,101,5.0,2.7,7.7,Medium,7.6
24,Female,Other,Graduate,YouTube,Education,3.2,138,5.4,2.3,7.7,Medium,7.9
21,Female,Other,Undergraduate,Twitter,News,6.0,195,2.3,1.2,5.9,High,4.1
21,Female,Other,Undergraduate,YouTube,Education,3.2,141,5.3,2.2,7.6,Low,7.6
22,Male,Other,Undergraduate,Snapchat,Entertainment,2.3,102,5.1,3.1,8.1,Low,7.3
22,Male,Other,Undergraduate,YouTube,Education,8.1,239,1.0,1.3,5.6,Very High,5.4
21,Male,Other,Undergraduate,Twitter,News,3.5,132,5.8,1.3,7.5,Low,8.9
21,Male,USA,Undergraduate,TikTok,Entertainment,5.8,176,1.4,1.4,5.5,High,5.4
24,Female,Other,Graduate,Twitter,News,2.9,129,4.4,3.2,8.0,Medium,7.0
22,Male,Other,Undergraduate,YouTube,Education,6.0,203,3.1,1.4,6.7,High,6.4
19,Male,USA,Undergraduate,YouTube,Education,5.8,175,2.0,0.6,5.3,Very High,5.8
19,Male,Other,Undergraduate,Facebook,Networking,4.9,170,4.2,2.7,6.0,High,6.3
20,Male,Other,Undergraduate,TikTok,Entertainment,5.6,186,2.0,1.9,6.8,Medium,6.8
18,Male,Other,High School,YouTube,Education,5.6,173,3.6,1.6,4.5,Very High,5.7
19,Male,Other,Undergraduate,TikTok,Entertainment,7.5,216,1.0,0.9,4.7,Very High,4.1
20,Female,Other,Undergraduate,Instagram,Entertainment,8.2,260,1.0,1.5,5.8,Very High,4.9
18,Female,Other,High School,YouTube,Education,7.4,220,1.9,0.9,5.8,Very High,4.7
18,Female,Australia,High School,LinkedIn,Education,6.3,202,1.4,2.0,5.9,Very High,5.4
23,Female,Other,Graduate,LinkedIn,Education,2.1,86,5.1,2.7,8.1,Low,8.8
19,Male,Australia,Undergraduate,YouTube,Education,5.7,193,1.9,1.7,6.0,High,5.8
21,Male,Canada,Undergraduate,TikTok,Entertainment,7.1,203,1.3,1.3,4.5,Very High,4.5
23,Male,Other,Graduate,Snapchat,Entertainment,5.6,179,1.1,1.5,5.8,High,4.0
23,Female,Other,Graduate,Instagram,Entertainment,7.5,233,1.0,1.6,5.9,Very High,5.2
24,Female,India,Graduate,Snapchat,Entertainment,3.0,117,4.6,1.8,7.1,Medium,7.2
21,Female,Germany,Undergraduate,YouTube,Education,3.7,141,5.2,1.3,8.7,Low,8.6
21,Male,Other,Undergraduate,TikTok,Entertainment,3.6,122,2.5,2.4,8.5,Medium,7.1
19,Female,Other,Undergraduate,YouTube,Education,5.4,177,2.0,2.0,6.4,High,6.6
23,Male,Other,Graduate,Facebook,Networking,2.0,105,4.7,2.7,7.7,Low,7.9
22,Female,Other,Undergraduate,TikTok,Entertainment,5.8,183,1.5,1.8,5.7,High,4.1
21,Female,Other,Undergraduate,Instagram,Entertainment,4.5,143,3.7,1.7,6.4,High,6.7
24,Male,Other,Graduate,Snapchat,Entertainment,6.3,215,1.6,1.8,5.3,Very High,4.3
23,Female,Germany,Graduate,Instagram,Entertainment,7.9,253,1.0,1.0,5.6,Very High,5.1
24,Female,Other,Graduate,TikTok,Entertainment,6.0,202,1.9,1.3,4.9,High,5.4
19,Male,Other,Undergraduate,YouTube,Education,5.0,181,3.2,1.6,6.2,Medium,6.4
18,Female,UK,High School,Facebook,Networking,6.7,223,1.0,2.3,5.8,Very High,4.6
23,Male,India,Graduate,Twitter,News,7.2,234,1.4,0.3,5.3,Very High,6.0
21,Female,India,Undergraduate,LinkedIn,Education,3.8,140,4.7,2.3,7.2,Medium,7.5
22,Female,Other,Undergraduate,YouTube,Education,4.6,140,3.7,1.0,6.4,Medium,6.0
22,Male,Other,Undergraduate,Snapchat,Entertainment,5.7,190,2.7,1.5,6.6,Very High,6.4
22,Female,Other,Undergraduate,YouTube,Education,6.3,192,1.9,1.2,5.6,Very High,5.0
19,Male,Other,Undergraduate,LinkedIn,Education,7.9,252,1.7,0.0,5.8,Very High,4.1
23,Female,Other,Graduate,Snapchat,Entertainment,5.0,168,2.9,1.9,6.1,High,6.6
21,Female,Other,Undergraduate,TikTok,Entertainment,3.5,148,4.3,1.9,7.5,High,9.0
22,Female,Other,Undergraduate,LinkedIn,Education,5.2,178,2.2,0.7,7.2,High,6.3
19,Female,Other,Undergraduate,YouTube,Education,2.7,114,4.5,2.7,8.6,Low,7.5
23,Female,Other,Graduate,Twitter,News,6.5,223,1.0,2.1,5.6,High,4.6
23,Male,Other,Graduate,TikTok,Entertainment,4.1,146,3.2,2.7,7.4,High,6.9
23,Male,Other,Graduate,LinkedIn,Education,2.4,100,5.5,2.6,7.1,Medium,7.1
22,Male,India,Undergraduate,Twitter,News,5.1,166,3.2,1.7,6.3,High,6.9
18,Male,Other,High School,Twitter,News,5.9,207,2.1,2.2,6.0,Very High,6.5
19,Female,Germany,Undergraduate,TikTok,Entertainment,5.7,197,1.7,2.4,5.2,Very High,4.1
24,Female,Other,Graduate,Twitter,News,8.2,235,1.0,1.5,5.0,Very High,4.7
19,Male,Other,Undergraduate,TikTok,Entertainment,6.9,216,1.7,0.8,5.0,Very High,5.6
21,Male,Other,Undergraduate,Twitter,News,7.6,229,1.0,1.2,5.0,Very High,4.1
19,Male,UK,Undergraduate,Snapchat,Entertainment,2.0,100,5.5,2.7,7.5,Low,7.8
18,Male,Other,High School,Facebook,Networking,3.9,124,4.5,1.1,7.3,Medium,8.5
19,Female,Other,Undergraduate,LinkedIn,Education,4.5,165,3.7,2.1,6.1,Medium,6.3
20,Male,Other,Undergraduate,TikTok,Entertainment,3.5,141,3.3,3.3,7.1,Low,8.1
18,Male,Other,High School,Twitter,News,7.3,216,1.0,1.5,5.3,Very High,5.0
21,Female,USA,Undergraduate,Facebook,Networking,3.7,123,4.5,2.8,7.5,Medium,8.3
23,Male,USA,Graduate,YouTube,Education,4.7,167,2.6,1.9,6.9,High,6.2
18,Male,Other,High School,YouTube,Education,5.3,167,2.9,1.6,6.9,High,6.4
20,Male,Australia,Undergraduate,Twitter,News,7.3,244,1.0,1.4,5.3,Very High,6.0
19,Female,India,Undergraduate,LinkedIn,Education,3.8,151,5.3,1.6,7.4,Medium,6.9
22,Female,India,Undergraduate,Instagram,Entertainment,8.4,273,1.0,0.4,6.0,Very High,5.5
19,Female,Other,Undergraduate,Twitter,News,8.3,253,1.0,1.6,4.7,Very High,4.6
21,Male,Other,Undergraduate,Snapchat,Entertainment,4.0,162,4.3,2.7,6.6,High,6.9
23,Female,India,Graduate,YouTube,Education,7.6,215,1.0,0.6,4.7,Very High,4.8
23,Female,Other,Graduate,Facebook,Networking,5.3,168,1.8,2.2,7.3,High,6.2
18,Male,Other,High School,Snapchat,Entertainment,5.9,172,1.9,1.5,6.2,High,6.1
22,Female,Other,Undergraduate,TikTok,Entertainment,4.1,154,3.0,2.1,6.4,High,6.9
22,Male,Other,Undergraduate,TikTok,Entertainment,5.6,185,3.0,1.8,6.1,High,6.3
21,Female,Other,Undergraduate,Facebook,Networking,8.4,246,1.2,1.4,5.2,Very High,5.1
20,Male,Australia,Undergraduate,Snapchat,Entertainment,5.8,182,1.3,1.6,5.8,Very High,4.9
24,Female,Other,Graduate,YouTube,Education,8.2,254,1.0,1.7,4.5,Very High,5.6
21,Male,Other,Undergraduate,Twitter,News,4.8,152,3.4,2.0,6.6,Medium,7.0
21,Female,Germany,Undergraduate,Snapchat,Entertainment,7.6,235,1.7,1.4,4.9,Very High,5.1
22,Female,Other,Undergraduate,Twitter,News,3.1,126,3.9,1.8,8.5,Low,7.0
18,Male,Other,High School,Instagram,Entertainment,7.5,221,1.0,2.2,5.4,Very High,5.5
20,Female,Other,Undergraduate,Snapchat,Entertainment,3.9,131,5.6,2.3,6.3,Medium,6.2
20,Female,USA,Undergraduate,LinkedIn,Education,7.1,216,1.0,1.6,6.0,Very High,4.1
22,Male,Other,Undergraduate,TikTok,Entertainment,6.3,205,1.0,0.6,5.4,Very High,6.0
24,Female,Other,Graduate,LinkedIn,Education,6.2,190,1.5,1.0,6.0,Very High,4.8
21,Female,Other,Undergraduate,LinkedIn,Education,4.9,162,2.7,2.4,6.8,Medium,6.3
18,Male,India,High School,Instagram,Entertainment,3.0,121,5.7,2.4,7.7,Medium,8.5
19,Male,Other,Undergraduate,Twitter,News,8.0,232,1.0,0.0,4.8,Very High,4.9
21,Female,Other,Undergraduate,Facebook,Networking,8.2,251,1.0,1.5,5.7,Very High,5.0
18,Female,Other,High School,TikTok,Entertainment,6.0,180,2.4,1.2,5.5,Very High,5.0
19,Female,Other,Undergraduate,YouTube,Education,4.8,150,2.7,2.5,6.9,High,6.9
24,Female,Other,Graduate,Instagram,Entertainment,5.3,166,3.7,1.6,6.4,High,6.8
22,Female,Other,Undergraduate,Instagram,Entertainment,4.5,148,3.0,2.0,6.6,High,6.8
23,Female,India,Graduate,Twitter,News,1.7,68,5.8,3.2,7.0,Medium,8.9
18,Male,Germany,High School,YouTube,Education,6.1,215,2.3,1.0,4.6,Very High,5.1
18,Male,Canada,High School,Twitter,News,1.9,84,6.7,2.0,7.3,Medium,8.9
21,Male,Other,Undergraduate,Instagram,Entertainment,7.7,249,1.0,1.0,5.8,Very High,5.1
21,Female,Other,Undergraduate,Instagram,Entertainment,6.9,233,1.0,1.7,5.2,Very High,5.9
24,Male,Other,Graduate,Twitter,News,5.9,204,2.5,0.9,5.9,High,4.4
20,Male,Australia,Undergraduate,YouTube,Education,2.4,118,4.8,1.6,8.7,Low,7.2
18,Male,Other,High School,LinkedIn,Education,6.5,191,1.7,1.8,5.0,Very High,5.0
20,Male,Other,Undergraduate,LinkedIn,Education,2.6,104,4.3,2.0,8.8,Low,8.5
20,Male,Other,Undergraduate,TikTok,Entertainment,6.9,226,1.5,1.1,5.3,Very High,5.1
19,Female,Germany,Undergraduate,Snapchat,Entertainment,5.4,183,2.0,0.7,7.3,Medium,6.3
21,Male,Australia,Undergraduate,Instagram,Entertainment,4.7,142,2.3,1.5,7.4,High,6.6
21,Male,Other,Undergraduate,Facebook,Networking,2.9,119,5.7,2.3,8.7,Low,8.9
21,Male,Other,Undergraduate,Instagram,Entertainment,1.7,99,6.5,3.0,8.1,Low,7.8
23,Female,Other,Graduate,TikTok,Entertainment,6.2,213,1.3,1.1,6.0,Very High,4.3
23,Male,Other,Graduate,TikTok,Entertainment,5.6,180,3.6,2.4,5.5,High,4.2
19,Female,Other,Undergraduate,TikTok,Entertainment,4.5,146,3.1,1.5,6.5,High,6.8
24,Female,Other,Graduate,Snapchat,Entertainment,8.0,237,1.0,0.7,5.6,Very High,6.0
21,Male,Australia,Undergraduate,Twitter,News,3.5,123,4.7,2.9,7.4,Medium,6.7
22,Male,Canada,Undergraduate,Twitter,News,4.8,158,2.7,1.9,6.9,Medium,6.1
24,Female,Other,Graduate,YouTube,Education,2.3,94,6.1,2.1,8.8,Low,8.5
22,Male,Other,Undergraduate,LinkedIn,Education,8.0,243,1.0,0.9,4.5,Very High,5.4
22,Male,Other,Undergraduate,Snapchat,Entertainment,6.6,191,1.1,2.0,5.2,Very High,5.2
22,Male,Other,Undergraduate,TikTok,Entertainment,1.6,76,7.5,3.3,8.2,Low,8.6
22,Female,Canada,Undergraduate,Instagram,Entertainment,6.8,207,1.0,0.9,5.4,Very High,4.4
19,Male,UK,Undergraduate,TikTok,Entertainment,1.8,76,4.3,2.5,7.6,Low,8.3
20,Female,Other,Undergraduate,TikTok,Entertainment,3.9,157,5.4,2.1,8.8,Medium,8.5
24,Male,Other,Graduate,Snapchat,Entertainment,6.7,219,3.3,0.8,5.4,Very High,5.4
23,Male,Other,Graduate,Twitter,News,7.8,256,1.0,1.0,5.7,Very High,5.9
20,Female,Other,Undergraduate,TikTok,Entertainment,5.0,172,1.5,1.8,7.4,Medium,6.7
18,Female,Other,High School,Facebook,Networking,7.6,219,1.0,1.7,4.5,Very High,5.9
21,Female,Other,Undergraduate,Instagram,Entertainment,1.7,103,6.1,3.2,8.7,Low,7.4
22,Female,Other,Undergraduate,LinkedIn,Education,5.8,188,2.0,1.4,6.7,High,6.5
21,Male,India,Undergraduate,Snapchat,Entertainment,6.4,212,1.0,1.3,5.5,Very High,5.9
22,Female,Other,Undergraduate,Snapchat,Entertainment,2.5,102,6.0,2.7,8.0,Medium,8.6
24,Male,Germany,Graduate,YouTube,Education,5.2,174,3.2,1.4,6.5,High,6.4
23,Male,Other,Graduate,TikTok,Entertainment,5.2,174,1.6,2.0,6.8,Medium,6.9
20,Female,Germany,Undergraduate,TikTok,Entertainment,6.8,206,1.8,1.3,5.1,Very High,4.9
22,Female,Other,Undergraduate,LinkedIn,Education,7.1,224,2.5,0.7,6.0,Very High,4.1
21,Female,Canada,Undergraduate,Facebook,Networking,4.7,171,3.4,1.3,7.1,High,6.5
19,Male,Canada,Undergraduate,Facebook,Networking,7.7,217,1.0,1.8,5.4,Very High,4.4
21,Female,Other,Undergraduate,LinkedIn,Education,2.6,95,5.3,2.3,8.9,Medium,8.3
19,Female,Other,Undergraduate,TikTok,Entertainment,6.2,213,2.3,2.3,5.0,Very High,4.8
22,Male,Australia,Undergraduate,Snapchat,Entertainment,5.7,189,1.0,1.3,7.4,High,6.9
20,Female,USA,Undergraduate,Twitter,News,2.9,135,5.2,2.4,7.3,Medium,7.1
19,Female,Other,Undergraduate,Facebook,Networking,4.2,154,3.5,3.1,6.9,High,6.7
21,Male,Canada,Undergraduate,YouTube,Education,3.8,146,5.7,1.5,9.0,Low,8.5
23,Female,India,Graduate,Instagram,Entertainment,3.6,150,4.3,1.2,7.6,Medium,7.9
24,Female,Other,Graduate,Instagram,Entertainment,2.1,103,7.2,3.1,8.0,Low,8.7
23,Female,Other,Graduate,Twitter,News,4.7,155,2.4,1.4,7.3,Medium,6.0
24,Male,Other,Graduate,LinkedIn,Education,7.7,238,1.0,1.1,5.8,Very High,4.4
23,Female,Other,Graduate,Facebook,Networking,7.2,214,1.1,0.9,5.6,Very High,4.6
23,Male,India,Graduate,Twitter,News,8.4,248,1.0,1.0,5.6,Very High,5.7
22,Female,India,Undergraduate,Instagram,Entertainment,4.8,172,3.3,1.3,7.0,Medium,6.3
21,Female,India,Undergraduate,TikTok,Entertainment,2.6,95,6.4,2.3,8.7,Low,7.5
20,Male,Other,Undergraduate,Twitter,News,8.1,253,1.0,1.2,4.6,Very High,4.7
19,Male,Other,Undergraduate,TikTok,Entertainment,6.3,205,1.0,0.9,5.4,Very High,4.9
20,Male,Other,Undergraduate,LinkedIn,Education,7.6,227,1.0,0.7,4.6,Very High,5.0
20,Female,Other,Undergraduate,YouTube,Education,6.1,178,1.2,1.3,5.1,Very High,4.1
24,Female,Other,Graduate,Facebook,Networking,3.3,135,4.4,1.5,7.2,Medium,7.3
23,Female,Other,Graduate,TikTok,Entertainment,6.9,229,1.0,1.1,5.9,Very High,4.6
20,Male,Other,Undergraduate,YouTube,Education,2.9,126,3.7,2.3,7.6,Medium,7.6
24,Male,Other,Graduate,TikTok,Entertainment,5.6,181,1.1,1.4,5.6,High,5.3
19,Male,Other,Undergraduate,YouTube,Education,4.3,158,4.1,1.8,6.4,High,6.4
21,Male,Other,Undergraduate,Twitter,News,6.8,211,1.0,1.3,4.6,Very High,4.0
23,Female,Other,Graduate,Instagram,Entertainment,5.4,174,1.0,1.3,6.6,High,6.3
19,Male,Other,Undergraduate,YouTube,Education,8.1,240,1.0,1.3,4.5,Very High,5.8
22,Female,Other,Undergraduate,TikTok,Entertainment,7.3,215,1.0,1.9,4.8,Very High,5.7
24,Male,Other,Graduate,LinkedIn,Education,3.7,155,3.7,1.8,8.5,Low,8.0
18,Male,India,High School,LinkedIn,Education,3.7,143,3.2,2.3,8.6,Medium,7.4
24,Male,Canada,Graduate,Facebook,Networking,6.3,188,2.4,1.3,5.6,Very High,4.5
22,Male,Other,Undergraduate,Instagram,Entertainment,5.6,199,2.7,1.8,5.8,High,5.2
24,Female,Other,Graduate,YouTube,Education,3.7,123,6.2,2.9,7.4,Low,6.7
21,Male,Germany,Undergraduate,LinkedIn,Education,7.2,228,1.1,1.5,5.1,Very High,4.3
18,Male,Other,High School,YouTube,Education,7.0,206,1.3,0.4,5.2,Very High,4.9
24,Female,Germany,Graduate,Twitter,News,5.5,176,2.4,1.9,4.6,Very High,4.8
19,Female,Other,Undergraduate,Facebook,Networking,5.4,186,3.3,2.3,6.7,High,6.6
18,Male,Other,High School,TikTok,Entertainment,2.3,121,6.2,2.3,8.1,Low,7.1
18,Male,Other,High School,Facebook,Networking,5.9,211,3.1,2.0,5.1,High,4.1
19,Male,Other,Undergraduate,Facebook,Networking,5.3,192,2.3,1.3,6.8,High,6.4
20,Male,Other,Undergraduate,LinkedIn,Education,2.0,84,5.7,1.8,8.2,Low,7.7
24,Male,Other,Graduate,Snapchat,Entertainment,1.6,68,6.0,2.7,8.9,Low,7.4
21,Female,Australia,Undergraduate,LinkedIn,Education,5.7,203,2.9,0.7,6.8,High,6.6
23,Female,Germany,Graduate,Instagram,Entertainment,6.6,226,2.6,1.2,4.6,Very High,6.0
22,Male,Other,Undergraduate,LinkedIn,Education,6.6,201,1.0,2.0,4.8,Very High,4.7
20,Female,Other,Undergraduate,Instagram,Entertainment,6.9,197,1.0,0.3,4.5,Very High,4.4
18,Male,Other,High School,LinkedIn,Education,3.7,142,4.6,1.4,7.9,Medium,8.2
23,Male,USA,Graduate,LinkedIn,Education,2.3,85,5.5,1.9,7.5,Medium,7.4
24,Female,Other,Graduate,Snapchat,Entertainment,6.7,193,2.1,1.3,4.9,Very High,4.2
20,Female,Other,Undergraduate,LinkedIn,Education,6.3,219,1.0,1.2,5.7,High,5.3
21,Female,India,Undergraduate,TikTok,Entertainment,4.2,149,3.1,2.6,6.1,High,6.5
21,Female,Other,Undergraduate,Twitter,News,2.3,86,5.1,2.9,7.0,Medium,8.4
23,Female,Australia,Graduate,Instagram,Entertainment,2.2,106,3.9,2.7,8.6,Low,7.7
23,Male,Other,Graduate,TikTok,Entertainment,3.6,129,3.6,2.2,8.6,Medium,7.9
19,Male,Other,Undergraduate,Instagram,Entertainment,3.3,128,4.0,2.4,8.2,Medium,7.3
19,Male,Other,Undergraduate,TikTok,Entertainment,6.5,222,1.3,0.9,5.0,Very High,4.2
18,Male,Other,High School,Twitter,News,7.4,219,1.5,1.6,4.9,Very High,4.3
23,Female,Other,Graduate,Twitter,News,4.7,167,3.1,1.3,7.3,Medium,6.3
24,Female,Other,Graduate,Facebook,Networking,3.8,153,3.4,2.5,6.8,Medium,6.9
23,Female,Germany,Graduate,Snapchat,Entertainment,6.1,193,1.9,2.1,5.3,High,5.7
18,Male,Canada,High School,Instagram,Entertainment,6.1,215,2.7,1.6,5.6,High,4.6
18,Female,Other,High School,Facebook,Networking,7.7,234,1.0,1.0,5.4,Very High,4.0
18,Male,Other,High School,Snapchat,Entertainment,5.0,168,2.3,2.0,6.5,High,6.8
20,Female,Other,Undergraduate,YouTube,Education,5.9,207,2.5,0.1,5.0,Very High,5.6
18,Female,Other,High School,Twitter,News,8.0,250,1.0,1.2,5.4,Very High,5.7
20,Male,Germany,Undergraduate,YouTube,Education,4.4,169,4.1,1.8,6.1,Medium,6.5
20,Male,India,Undergraduate,LinkedIn,Education,7.5,243,1.0,1.1,5.2,Very High,5.2
22,Male,India,Undergraduate,Twitter,News,5.5,190,3.1,2.0,7.1,Medium,7.0
22,Male,Other,Undergraduate,Instagram,Entertainment,6.0,184,1.2,1.5,5.8,Very High,5.5
21,Male,Canada,Undergraduate,Twitter,News,2.1,92,5.9,1.9,8.8,Low,7.0
22,Male,Other,Undergraduate,Facebook,Networking,4.1,161,3.7,1.9,6.7,Medium,6.3
18,Female,Other,High School,Twitter,News,5.6,189,1.4,1.6,5.6,High,4.4
23,Male,India,Graduate,Instagram,Entertainment,1.8,81,4.9,2.6,7.8,Low,7.0
22,Male,Other,Undergraduate,Facebook,Networking,4.7,155,3.8,1.9,6.6,High,6.9
23,Male,UK,Graduate,Twitter,News,3.9,153,3.8,2.5,7.3,Medium,7.0
22,Female,Other,Undergraduate,YouTube,Education,6.6,197,1.0,0.8,5.0,Very High,4.1
21,Male,Other,Undergraduate,Facebook,Networking,5.9,176,2.0,1.6,4.6,Very High,5.2
24,Female,Other,Graduate,Facebook,Networking,3.8,150,5.1,2.7,7.5,Medium,8.8
18,Female,USA,High School,YouTube,Education,7.2,216,1.0,0.3,5.5,Very High,5.8
24,Female,Other,Graduate,YouTube,Education,7.5,242,1.0,1.2,4.9,Very High,4.9
18,Male,Other,High School,Snapchat,Entertainment,1.6,86,5.7,2.3,8.4,Low,7.7
22,Male,UK,Undergraduate,Snapchat,Entertainment,8.1,266,1.1,0.8,5.4,Very High,5.1
18,Male,Other,High School,Instagram,Entertainment,7.1,222,1.1,0.8,5.9,Very High,4.8
23,Male,India,Graduate,Instagram,Entertainment,2.7,126,5.9,2.2,8.8,Low,8.4
24,Male,Other,Graduate,Snapchat,Entertainment,5.8,204,1.3,2.5,4.8,High,4.9
21,Male,USA,Undergraduate,Facebook,Networking,6.8,203,1.0,0.7,5.7,Very High,5.6
24,Male,Other,Graduate,Twitter,News,7.4,249,1.0,0.6,5.3,Very High,4.1
22,Female,Canada,Undergraduate,YouTube,Education,4.1,156,3.9,1.3,7.2,Medium,6.3
22,Male,Other,Undergraduate,Snapchat,Entertainment,6.3,186,2.1,2.3,5.6,Very High,4.2
24,Male,Other,Graduate,Instagram,Entertainment,7.5,212,1.0,0.9,5.7,Very High,5.7
18,Female,Other,High School,TikTok,Entertainment,8.0,235,1.0,1.0,4.8,Very High,5.3
19,Male,India,Undergraduate,YouTube,Education,5.9,172,2.2,1.3,6.0,High,7.0
24,Male,USA,Graduate,TikTok,Entertainment,4.4,149,4.2,1.4,6.3,Medium,6.2
24,Male,Other,Graduate,YouTube,Education,7.0,239,1.6,1.1,5.6,Very High,5.7
21,Female,Other,Undergraduate,Twitter,News,8.0,244,1.0,2.2,5.2,Very High,5.6
21,Male,Canada,Undergraduate,Instagram,Entertainment,2.5,87,3.7,3.1,7.0,Low,8.2
19,Female,Australia,Undergraduate,Facebook,Networking,6.2,199,2.6,1.0,5.2,Very High,5.9
21,Female,Other,Undergraduate,LinkedIn,Education,7.4,218,1.6,1.5,4.6,Very High,5.4
20,Female,USA,Undergraduate,YouTube,Education,4.6,174,2.6,1.4,6.1,High,6.7
18,Male,Other,High School,Facebook,Networking,6.3,185,1.0,0.5,4.8,Very High,5.0
24,Female,Germany,Graduate,TikTok,Entertainment,3.2,135,4.9,2.7,7.9,Medium,7.4
19,Female,Other,Undergraduate,LinkedIn,Education,5.4,177,3.3,2.2,7.1,Medium,6.5
24,Male,Other,Graduate,LinkedIn,Education,2.5,87,6.9,2.9,7.9,Low,8.8
21,Female,Other,Undergraduate,LinkedIn,Education,2.0,101,6.4,2.3,8.7,Low,8.4
23,Female,Other,Graduate,Twitter,News,2.8,113,4.9,2.2,8.5,Low,8.3
22,Female,Other,Undergraduate,TikTok,Entertainment,5.2,185,2.1,2.1,6.3,Medium,6.8
21,Male,Other,Undergraduate,YouTube,Education,5.2,179,2.8,1.9,6.7,High,6.8
21,Female,Other,Undergraduate,YouTube,Education,8.1,258,1.0,0.8,5.6,Very High,4.5
18,Male,Other,High School,Instagram,Entertainment,2.8,113,4.4,1.5,7.3,Low,8.2
19,Male,Other,Undergraduate,LinkedIn,Education,5.9,172,3.7,1.6,7.4,Very High,6.5
22,Male,Other,Undergraduate,TikTok,Entertainment,1.6,70,7.8,3.1,7.7,Low,7.8
18,Female,Other,High School,Snapchat,Entertainment,7.6,233,1.3,0.5,5.4,Very High,5.8
18,Female,USA,High School,YouTube,Education,1.9,87,5.4,2.8,7.9,Low,7.2
18,Female,Other,High School,Snapchat,Entertainment,2.9,128,5.8,2.4,8.2,Low,7.4
18,Female,USA,High School,Instagram,Entertainment,2.1,93,6.4,2.9,8.7,Low,7.9
18,Male,Other,High School,LinkedIn,Education,5.8,204,2.6,2.0,5.9,High,5.5
18,Female,UK,High School,Twitter,News,3.6,122,5.4,1.8,7.1,High,7.0
18,Male,USA,High School,YouTube,Education,3.9,137,4.6,1.2,6.0,Medium,6.7
20,Male,Other,Undergraduate,LinkedIn,Education,8.1,257,1.0,0.7,5.9,Very High,5.9
20,Male,Other,Undergraduate,Twitter,News,8.2,233,1.0,1.4,5.2,Very High,5.4
23,Male,Canada,Graduate,Snapchat,Entertainment,6.0,187,2.3,1.2,6.5,High,6.1
19,Female,Other,Undergraduate,Facebook,Networking,6.1,207,1.0,1.1,4.6,Very High,4.3
22,Female,Other,Undergraduate,TikTok,Entertainment,7.2,228,1.0,0.3,4.5,Very High,5.9
21,Female,Other,Undergraduate,Facebook,Networking,2.5,118,5.1,3.3,8.7,Low,8.3
19,Male,UK,Undergraduate,Snapchat,Entertainment,3.8,140,3.2,2.5,6.6,Low,6.8
22,Male,USA,Undergraduate,YouTube,Education,5.5,196,3.8,2.0,5.2,Very High,4.6
20,Male,India,Undergraduate,Snapchat,Entertainment,5.6,200,3.8,2.1,5.8,Medium,5.1
22,Female,Other,Undergraduate,Snapchat,Entertainment,4.5,175,4.6,2.2,6.7,Medium,6.9
20,Male,Other,Undergraduate,LinkedIn,Education,2.8,99,5.4,2.2,8.5,Medium,8.7
20,Female,Other,Undergraduate,LinkedIn,Education,5.5,185,3.6,1.5,6.5,High,6.8
18,Female,Other,High School,LinkedIn,Education,6.3,186,1.7,1.2,5.1,High,4.2
22,Male,Other,Undergraduate,YouTube,Education,4.0,134,4.2,3.3,8.5,Low,8.5
22,Female,UK,Undergraduate,Facebook,Networking,5.1,164,2.0,2.0,7.1,Medium,6.1
20,Female,Other,Undergraduate,Twitter,News,4.9,172,3.4,1.5,6.0,High,7.0
24,Female,Australia,Graduate,LinkedIn,Education,2.2,97,5.8,2.7,7.1,Low,7.1
23,Female,Other,Graduate,Instagram,Entertainment,4.0,159,3.0,1.5,7.1,Medium,8.0
21,Female,Other,Undergraduate,LinkedIn,Education,5.1,163,2.9,2.5,6.9,High,6.0
22,Male,Other,Undergraduate,YouTube,Education,3.7,141,4.2,1.7,7.4,Medium,9.0
19,Male,Other,Undergraduate,TikTok,Entertainment,4.4,165,5.0,2.2,7.0,High,6.2
20,Male,USA,Undergraduate,TikTok,Entertainment,7.7,256,1.0,1.6,5.6,Very High,5.3
19,Male,USA,Undergraduate,LinkedIn,Education,6.0,184,2.0,1.7,5.5,High,4.7
22,Female,Other,Undergraduate,Instagram,Entertainment,7.0,229,1.2,1.3,5.8,High,4.3
19,Female,Other,Undergraduate,Twitter,News,5.2,158,2.8,1.7,6.8,High,6.2
18,Male,Other,High School,Snapchat,Entertainment,6.5,208,1.3,1.3,5.4,Very High,4.1
20,Female,Other,Undergraduate,TikTok,Entertainment,3.2,121,3.9,1.9,8.6,Low,7.5
23,Female,Other,Graduate,TikTok,Entertainment,4.3,170,3.6,1.7,6.1,High,6.3
22,Male,Australia,Undergraduate,YouTube,Education,6.2,210,1.2,2.2,5.5,Very High,4.8
20,Female,USA,Undergraduate,Facebook,Networking,6.4,222,1.0,1.3,5.5,Very High,5.7
24,Male,India,Graduate,LinkedIn,Education,8.1,261,1.0,0.6,5.1,Very High,5.1
21,Male,Other,Undergraduate,Facebook,Networking,5.2,171,3.1,1.4,7.3,Medium,6.6
22,Male,Other,Undergraduate,Snapchat,Entertainment,6.9,226,1.0,1.8,4.6,Very High,5.2
22,Male,Other,Undergraduate,YouTube,Education,2.6,91,5.3,2.7,7.7,Low,8.9
22,Female,Other,Undergraduate,LinkedIn,Education,1.6,87,7.2,2.9,7.1,Medium,7.4
21,Male,Other,Undergraduate,Snapchat,Entertainment,3.8,121,5.0,1.9,6.7,Medium,6.8
22,Female,Other,Undergraduate,TikTok,Entertainment,7.4,238,1.4,1.4,5.2,Very High,5.1
20,Female,Other,Undergraduate,TikTok,Entertainment,6.4,223,1.6,1.1,5.8,Very High,4.1
19,Male,USA,Undergraduate,Twitter,News,5.1,179,2.2,1.6,7.3,High,6.6
18,Male,UK,High School,Snapchat,Entertainment,6.3,215,1.0,1.9,5.8,High,5.6
23,Female,UK,Graduate,Snapchat,Entertainment,5.7,176,2.6,2.0,5.5,Very High,4.5
24,Female,Other,Graduate,YouTube,Education,7.3,246,1.0,0.7,5.6,Very High,5.0
19,Female,Other,Undergraduate,LinkedIn,Education,4.4,157,4.6,1.5,6.9,Medium,6.5
19,Male,Other,Undergraduate,LinkedIn,Education,6.5,213,2.4,1.4,5.4,Very High,5.8
23,Male,Other,Graduate,YouTube,Education,3.8,150,4.1,2.9,6.7,Medium,6.3
24,Male,Other,Graduate,YouTube,Education,4.8,170,2.2,0.8,6.7,High,6.1
18,Female,Other,High School,LinkedIn,Education,2.5,99,5.2,2.5,7.3,Low,7.3
18,Female,Other,High School,Twitter,News,2.8,119,5.4,1.6,8.6,Low,8.0
21,Male,Australia,Undergraduate,TikTok,Entertainment,7.2,231,1.0,0.9,4.7,Very High,5.8
19,Female,UK,Undergraduate,Snapchat,Entertainment,8.4,269,1.0,0.7,5.0,Very High,4.5
20,Female,USA,Undergraduate,Facebook,Networking,2.5,106,5.7,2.2,8.0,Low,9.0
19,Male,Other,Undergraduate,Snapchat,Entertainment,8.4,255,1.0,0.6,4.8,Very High,5.4
21,Male,India,Undergraduate,Snapchat,Entertainment,2.5,107,5.0,2.4,7.4,Low,8.0
22,Female,Germany,Undergraduate,Snapchat,Entertainment,6.6,194,1.6,1.1,4.7,Very High,5.4
19,Female,Other,Undergraduate,LinkedIn,Education,3.7,120,4.0,1.3,6.1,Medium,6.6
22,Female,Other,Undergraduate,Facebook,Networking,2.9,97,5.3,2.7,7.0,Low,7.2
23,Male,Other,Graduate,Instagram,Entertainment,3.3,133,4.9,2.6,8.8,Low,9.0
24,Male,Other,Graduate,Twitter,News,7.4,226,1.0,1.6,5.6,Very High,5.1
22,Female,Australia,Undergraduate,YouTube,Education,3.0,134,4.6,1.5,8.3,Medium,7.8
22,Male,Other,Undergraduate,Facebook,Networking,6.8,223,2.4,1.4,5.2,Very High,4.3
23,Female,India,Graduate,Facebook,Networking,2.6,95,4.5,2.7,7.7,Low,8.7
22,Male,Other,Undergraduate,Facebook,Networking,6.7,196,1.0,0.8,5.1,Very High,4.7
23,Female,Other,Graduate,Instagram,Entertainment,6.7,206,1.0,1.3,5.8,Very High,5.5
21,Male,Canada,Undergraduate,YouTube,Education,3.6,151,4.4,2.0,6.2,Medium,6.1
23,Male,Australia,Graduate,YouTube,Education,3.4,111,4.6,3.1,8.7,Medium,7.8
20,Male,Other,Undergraduate,YouTube,Education,6.8,202,1.1,2.3,6.0,Very High,5.1
18,Male,Other,High School,Twitter,News,2.4,86,6.6,1.6,7.3,Low,8.4
18,Male,Other,High School,Snapchat,Entertainment,6.0,191,1.0,2.7,5.0,High,5.5
23,Female,Other,Graduate,Instagram,Entertainment,7.4,249,1.0,0.7,4.6,Very High,4.3
23,Female,Other,Graduate,Twitter,News,4.5,164,4.7,2.4,6.9,High,6.1
23,Male,Other,Graduate,TikTok,Entertainment,6.6,209,1.0,1.8,5.6,High,5.0
19,Male,India,Undergraduate,Facebook,Networking,3.6,120,4.1,1.6,8.8,Medium,7.9
20,Male,Other,Undergraduate,LinkedIn,Education,2.0,89,5.4,2.7,7.6,Low,7.6
21,Female,India,Undergraduate,Facebook,Networking,3.9,142,3.4,2.0,7.8,Medium,7.1
20,Male,Other,Undergraduate,Instagram,Entertainment,5.5,172,2.2,1.9,6.7,High,6.8
18,Male,Other,High School,Instagram,Entertainment,6.7,220,2.4,1.4,4.8,Very High,5.8
21,Male,Other,Undergraduate,Snapchat,Entertainment,8.2,269,1.3,1.5,4.9,Very High,5.6
21,Female,Other,Undergraduate,TikTok,Entertainment,5.8,178,1.9,1.6,5.6,Very High,6.0
18,Female,Other,High School,Snapchat,Entertainment,5.9,182,3.6,1.4,4.6,Very High,5.6
18,Male,USA,High School,Instagram,Entertainment,7.2,210,1.0,1.7,5.9,High,4.4
24,Male,Other,Graduate,Instagram,Entertainment,6.5,216,2.9,1.7,5.3,Very High,4.8
19,Female,USA,Undergraduate,LinkedIn,Education,2.9,115,5.0,2.6,8.9,Low,7.4
24,Male,Other,Graduate,TikTok,Entertainment,6.3,193,1.8,1.1,5.7,Very High,5.6
18,Male,Australia,High School,Twitter,News,4.4,143,3.9,1.4,6.1,High,6.5
21,Female,Other,Undergraduate,TikTok,Entertainment,7.1,204,3.4,0.9,5.5,Very High,4.8
20,Female,UK,Undergraduate,TikTok,Entertainment,3.8,139,4.9,1.7,7.2,Medium,8.1
22,Female,Other,Undergraduate,Instagram,Entertainment,7.9,249,1.0,1.4,5.4,Very High,4.7
19,Female,Other,Undergraduate,LinkedIn,Education,5.6,174,3.2,2.1,6.3,Very High,6.4
20,Female,Other,Undergraduate,YouTube,Education,6.3,182,1.4,1.3,5.2,High,4.6
21,Male,Other,Undergraduate,TikTok,Entertainment,3.2,123,4.4,2.9,7.1,Medium,7.1
20,Male,Other,Undergraduate,Snapchat,Entertainment,2.0,102,6.7,3.2,7.1,Low,9.0
23,Male,Australia,Graduate,Snapchat,Entertainment,7.6,228,1.0,1.2,5.9,Very High,4.1
23,Female,Other,Graduate,YouTube,Education,7.4,220,1.0,0.7,5.7,Very High,4.2
21,Male,Other,Undergraduate,YouTube,Education,5.6,171,2.4,2.4,4.9,High,5.5
19,Female,Other,Undergraduate,LinkedIn,Education,4.6,169,3.7,1.8,7.2,High,6.5
19,Female,USA,Undergraduate,Facebook,Networking,6.1,211,2.2,1.5,4.8,Very High,4.2
20,Female,Other,Undergraduate,Snapchat,Entertainment,4.2,160,2.3,1.8,6.2,High,6.7
22,Female,Other,Undergraduate,LinkedIn,Education,3.7,137,4.8,1.6,6.2,High,6.9
23,Male,Other,Graduate,LinkedIn,Education,6.1,205,1.1,0.7,5.6,Very High,4.5
19,Female,USA,Undergraduate,TikTok,Entertainment,6.1,192,1.0,1.8,5.5,High,5.6
20,Male,USA,Undergraduate,LinkedIn,Education,2.7,92,5.3,1.9,7.6,Low,8.9
20,Male,Other,Undergraduate,Snapchat,Entertainment,6.0,189,2.1,3.0,5.8,Very High,4.9
23,Male,Other,Graduate,TikTok,Entertainment,6.4,213,1.0,0.9,5.4,Very High,4.6
21,Male,UK,Undergraduate,YouTube,Education,5.7,192,3.0,0.9,5.3,High,5.8
20,Male,Other,Undergraduate,Instagram,Entertainment,7.0,239,1.0,1.5,5.3,Very High,5.1
23,Female,Other,Graduate,Facebook,Networking,7.7,256,1.0,1.8,5.7,High,4.6
19,Male,Other,Undergraduate,TikTok,Entertainment,6.3,191,1.2,1.5,4.8,Very High,4.0
20,Female,Other,Undergraduate,Twitter,News,5.7,167,2.3,1.9,5.2,High,5.5
18,Male,Other,High School,LinkedIn,Education,8.2,239,1.0,0.0,5.2,Very High,4.6
19,Female,Other,Undergraduate,Twitter,News,6.4,220,1.0,1.1,5.5,Very High,4.4
22,Male,India,Undergraduate,TikTok,Entertainment,6.6,222,2.0,0.8,4.7,Very High,4.3
18,Female,Other,High School,LinkedIn,Education,6.0,178,2.1,0.6,4.6,Very High,5.4
21,Female,Germany,Undergraduate,LinkedIn,Education,5.9,178,1.0,1.6,5.1,High,5.9
23,Female,Australia,Graduate,LinkedIn,Education,7.4,232,1.0,0.0,5.1,Very High,4.3
19,Male,Other,Undergraduate,Snapchat,Entertainment,5.8,196,2.2,0.9,5.6,Very High,4.5
21,Female,Other,Undergraduate,Instagram,Entertainment,5.8,209,2.0,1.3,6.0,Very High,4.4
21,Male,Other,Undergraduate,LinkedIn,Education,1.8,100,6.1,2.1,9.0,Low,8.2
18,Male,Other,High School,Snapchat,Entertainment,6.5,195,1.5,1.6,5.4,High,4.1
23,Male,Other,Graduate,Instagram,Entertainment,3.8,121,4.4,2.2,6.5,Medium,6.6
18,Male,Other,High School,TikTok,Entertainment,8.0,250,1.0,1.4,5.6,Very High,4.5
19,Male,India,Undergraduate,Twitter,News,7.7,239,1.0,1.5,5.5,Very High,4.7
19,Male,Other,Undergraduate,Snapchat,Entertainment,8.1,263,1.0,1.5,5.2,Very High,5.0
22,Male,Other,Undergraduate,TikTok,Entertainment,6.2,203,1.0,1.4,5.2,Very High,5.8
18,Female,Other,High School,Facebook,Networking,4.9,167,3.3,1.9,7.1,High,6.6
23,Male,Other,Graduate,YouTube,Education,3.9,134,5.1,2.3,8.5,Low,8.9
21,Male,Other,Undergraduate,Twitter,News,6.6,193,1.1,1.4,5.0,Very High,6.0
22,Male,Other,Undergraduate,Instagram,Entertainment,6.2,215,1.0,1.3,4.7,Very High,4.4
24,Male,UK,Graduate,Facebook,Networking,2.4,118,4.2,2.2,7.5,Low,7.1
19,Male,Other,Undergraduate,Instagram,Entertainment,3.6,121,3.7,1.7,8.7,Low,8.5
18,Male,Other,High School,Instagram,Entertainment,2.8,123,4.8,2.5,8.8,Low,8.6
23,Male,Other,Graduate,YouTube,Education,1.6,79,6.1,2.6,7.1,Low,8.1
22,Male,USA,Undergraduate,Facebook,Networking,7.3,224,1.0,0.8,5.9,Very High,4.4
18,Female,Canada,High School,YouTube,Education,6.8,228,1.0,1.0,5.2,Very High,5.2
22,Male,Other,Undergraduate,Facebook,Networking,7.7,250,1.1,0.5,5.0,Very High,6.0
23,Female,Germany,Graduate,LinkedIn,Education,5.5,169,2.0,2.1,7.3,High,6.9
22,Male,Other,Undergraduate,TikTok,Entertainment,6.2,192,1.1,1.5,5.5,Very High,5.9
24,Female,Other,Graduate,LinkedIn,Education,4.6,172,3.8,1.4,6.8,High,6.4
20,Male,Other,Undergraduate,Facebook,Networking,7.2,241,1.0,1.6,5.6,Very High,5.6
24,Male,Other,Graduate,TikTok,Entertainment,3.3,110,5.0,1.9,7.7,Medium,7.7
23,Male,Other,Graduate,YouTube,Education,5.4,193,2.7,0.9,6.6,High,6.4
23,Female,Other,Graduate,TikTok,Entertainment,3.2,124,4.7,2.7,7.6,Medium,9.0
18,Female,Other,High School,Snapchat,Entertainment,3.7,140,5.6,1.8,7.9,Medium,7.3
19,Female,Other,Undergraduate,Snapchat,Entertainment,6.3,185,1.2,1.2,5.7,High,5.4
21,Female,Australia,Undergraduate,YouTube,Education,7.5,239,2.1,1.1,5.0,Very High,4.8
23,Female,Other,Graduate,Facebook,Networking,6.0,202,1.8,2.1,6.0,High,5.7
20,Male,India,Undergraduate,TikTok,Entertainment,8.2,255,1.0,1.0,5.8,Very High,5.9
18,Female,Other,High School,YouTube,Education,6.1,208,2.0,0.9,5.5,Very High,4.5
19,Female,Other,Undergraduate,Instagram,Entertainment,8.2,267,1.0,1.2,4.5,Very High,5.8
24,Male,Other,Graduate,LinkedIn,Education,5.3,190,2.1,1.4,7.0,Medium,6.2
22,Male,Other,Undergraduate,YouTube,Education,5.8,199,2.5,2.5,7.2,High,6.0
22,Female,USA,Undergraduate,YouTube,Education,7.2,244,1.2,1.2,4.6,Very High,5.4
23,Male,UK,Graduate,Snapchat,Entertainment,4.0,151,3.5,0.9,7.2,Medium,6.2
20,Female,Other,Undergraduate,LinkedIn,Education,3.3,133,5.5,2.4,7.5,Low,8.3
22,Male,India,Undergraduate,Snapchat,Entertainment,6.1,198,2.8,2.4,4.5,Very High,5.8
18,Female,India,High School,Facebook,Networking,6.8,225,2.3,2.1,4.8,Very High,4.2
24,Male,Other,Graduate,Snapchat,Entertainment,3.4,112,5.0,3.1,7.1,Medium,8.3
24,Female,Other,Graduate,Instagram,Entertainment,7.7,237,1.4,0.6,4.8,Very High,4.8
23,Female,Other,Graduate,Instagram,Entertainment,7.6,232,1.0,1.6,4.7,Very High,5.6
24,Female,India,Graduate,Snapchat,Entertainment,4.7,178,3.0,1.5,6.6,High,6.8
20,Male,Other,Undergraduate,Facebook,Networking,4.9,149,2.4,1.9,7.4,Medium,6.1
23,Male,Other,Graduate,LinkedIn,Education,8.0,250,1.0,0.4,4.9,Very High,5.9
24,Male,Other,Graduate,YouTube,Education,7.2,212,1.0,0.9,5.9,Very High,5.9
22,Female,USA,Undergraduate,LinkedIn,Education,1.7,102,6.2,2.2,7.9,Low,8.3
24,Female,Other,Graduate,TikTok,Entertainment,4.6,174,4.9,2.3,6.8,High,6.5
18,Male,Australia,High School,Facebook,Networking,4.4,144,3.5,2.3,6.5,Medium,6.5
24,Female,Other,Graduate,TikTok,Entertainment,3.7,151,4.6,2.2,8.8,Medium,8.8
18,Female,Other,High School,YouTube,Education,1.8,89,6.0,1.9,7.9,Low,8.0
23,Female,USA,Graduate,YouTube,Education,7.7,255,1.0,0.9,4.9,Very High,5.8
18,Male,USA,High School,Facebook,Networking,4.5,166,3.5,1.5,7.2,Medium,6.5
22,Male,Australia,Undergraduate,Facebook,Networking,8.1,228,1.0,1.4,5.2,Very High,5.5
23,Male,Other,Graduate,YouTube,Education,3.5,120,5.4,2.7,7.8,Medium,7.2
21,Female,Canada,Undergraduate,Instagram,Entertainment,3.4,126,5.9,2.7,7.0,Low,7.3
20,Male,Other,Undergraduate,TikTok,Entertainment,4.0,133,4.2,1.6,7.1,Medium,7.3
24,Male,Other,Graduate,TikTok,Entertainment,3.8,125,4.7,0.7,6.0,Low,6.1
23,Male,India,Graduate,Twitter,News,3.8,159,3.3,1.2,6.6,Medium,6.7
18,Male,Other,High School,Twitter,News,5.6,199,2.3,2.3,6.9,High,6.0
23,Female,Australia,Graduate,Instagram,Entertainment,4.3,149,4.5,1.7,6.4,Medium,6.5
22,Female,UK,Undergraduate,Snapchat,Entertainment,4.1,135,4.6,1.6,6.1,Medium,6.2
21,Female,India,Undergraduate,YouTube,Education,2.5,94,5.7,3.2,7.2,Low,7.0
23,Male,India,Graduate,LinkedIn,Education,4.5,173,4.2,2.5,6.2,High,6.4
22,Female,Other,Undergraduate,Facebook,Networking,7.7,230,1.0,1.1,5.8,Very High,5.5
24,Male,USA,Graduate,Facebook,Networking,5.2,155,3.8,1.6,7.3,High,6.1
22,Female,Australia,Undergraduate,Facebook,Networking,8.0,240,1.0,0.9,5.1,Very High,4.9
23,Male,Other,Graduate,Snapchat,Entertainment,6.9,215,1.0,1.4,5.7,Very High,5.7
20,Male,Canada,Undergraduate,LinkedIn,Education,4.3,156,4.0,2.7,6.6,Medium,6.7
20,Male,Other,Undergraduate,YouTube,Education,3.5,125,2.2,2.3,8.3,Medium,8.2
21,Male,UK,Undergraduate,LinkedIn,Education,7.6,251,1.0,1.5,6.0,Very High,4.5
19,Female,Other,Undergraduate,LinkedIn,Education,6.1,202,1.0,2.1,5.8,High,4.1
19,Male,Other,Undergraduate,YouTube,Education,7.0,239,1.0,0.7,5.4,Very High,5.9
18,Male,Other,High School,YouTube,Education,6.0,189,2.4,1.9,5.9,High,4.1
24,Male,Other,Graduate,LinkedIn,Education,7.0,226,1.4,1.1,5.0,Very High,4.5
23,Female,Other,Graduate,Instagram,Entertainment,2.7,106,4.4,1.1,7.8,Low,8.8
21,Male,USA,Undergraduate,Snapchat,Entertainment,3.9,149,3.5,1.0,7.1,Low,7.5
19,Female,Other,Undergraduate,Twitter,News,5.5,191,3.6,1.1,5.4,Very High,5.2
22,Male,Other,Undergraduate,Facebook,Networking,1.9,84,5.7,2.8,8.4,Low,8.5
23,Female,Other,Graduate,LinkedIn,Education,1.8,107,8.0,2.6,8.2,Low,7.2
23,Male,Other,Graduate,Facebook,Networking,4.9,181,3.1,1.9,6.3,High,6.1
20,Male,UK,Undergraduate,LinkedIn,Education,4.3,167,4.0,2.9,6.2,Medium,6.2
19,Female,Other,Undergraduate,YouTube,Education,2.9,105,6.4,1.6,7.1,Medium,8.8
22,Female,Germany,Undergraduate,Facebook,Networking,7.2,233,1.0,1.2,5.4,Very High,5.7
22,Male,Other,Undergraduate,LinkedIn,Education,7.9,226,1.0,1.2,4.7,Very High,4.1
19,Female,Germany,Undergraduate,Instagram,Entertainment,2.5,91,5.4,2.0,8.3,Low,7.2
21,Female,Other,Undergraduate,LinkedIn,Education,3.8,158,4.2,2.1,7.4,Medium,7.3
20,Female,Other,Undergraduate,Snapchat,Entertainment,5.8,176,1.1,0.8,7.2,High,6.1
20,Male,Other,Undergraduate,Facebook,Networking,5.9,206,1.9,2.2,5.8,High,4.7
22,Male,Other,Undergraduate,Instagram,Entertainment,2.6,107,4.8,2.0,7.5,Medium,8.8
18,Female,Other,High School,Twitter,News,5.2,167,3.5,2.7,6.8,High,6.9
21,Male,Other,Undergraduate,Snapchat,Entertainment,1.7,69,6.3,2.6,8.5,Low,7.7
20,Male,Australia,Undergraduate,Twitter,News,2.8,122,5.0,2.8,7.0,Medium,7.8
19,Male,Other,Undergraduate,Facebook,Networking,3.8,148,4.1,2.0,7.4,Low,8.8
24,Male,Other,Graduate,LinkedIn,Education,5.1,170,3.1,1.7,6.5,High,6.8
23,Male,India,Graduate,Instagram,Entertainment,3.7,149,4.8,1.8,6.5,Medium,6.9
23,Female,India,Graduate,Snapchat,Entertainment,1.5,74,5.7,2.7,7.2,Low,7.7
18,Female,UK,High School,Facebook,Networking,3.5,134,3.7,2.3,7.9,Medium,8.5
23,Male,Other,Graduate,Facebook,Networking,3.8,131,5.1,1.7,6.5,Medium,6.4
21,Female,Other,Undergraduate,YouTube,Education,4.1,150,3.6,1.9,6.2,High,6.6
21,Female,Other,Undergraduate,Snapchat,Entertainment,5.4,165,1.5,1.3,6.3,High,6.5
21,Female,Other,Undergraduate,YouTube,Education,6.7,211,1.7,2.5,5.5,Very High,4.9
21,Male,Other,Undergraduate,Facebook,Networking,7.4,231,1.0,1.1,5.3,Very High,5.5
24,Male,India,Graduate,Facebook,Networking,3.8,142,3.0,2.8,6.3,Medium,6.8
19,Male,Other,Undergraduate,LinkedIn,Education,7.4,227,1.0,1.1,5.7,Very High,5.7
22,Female,Other,Undergraduate,LinkedIn,Education,2.0,100,6.6,2.6,7.5,Low,8.3
22,Male,Other,Undergraduate,Facebook,Networking,7.3,227,1.0,0.5,5.8,Very High,5.3
24,Female,Canada,Graduate,Facebook,Networking,5.8,181,2.7,1.3,5.5,High,4.1
22,Female,Canada,Undergraduate,Snapchat,Entertainment,7.2,213,1.0,1.3,5.1,High,4.6
24,Female,Other,Graduate,LinkedIn,Education,3.6,140,4.7,2.9,8.4,Low,7.6
21,Female,Other,Undergraduate,TikTok,Entertainment,7.6,252,1.0,1.2,5.2,Very High,4.1
22,Female,Other,Undergraduate,TikTok,Entertainment,3.8,150,3.8,2.7,7.4,Medium,6.8
21,Male,Other,Undergraduate,Twitter,News,6.1,202,2.6,1.8,5.8,Very High,4.4
20,Female,UK,Undergraduate,TikTok,Entertainment,2.9,133,6.3,3.1,7.5,Low,7.9
24,Female,Other,Graduate,Instagram,Entertainment,3.7,152,5.7,2.0,8.8,Medium,9.0
21,Female,Australia,Undergraduate,Facebook,Networking,7.0,220,2.1,2.4,5.9,Very High,4.1
22,Female,Other,Undergraduate,Instagram,Entertainment,3.9,126,4.0,1.8,7.7,Medium,8.3
19,Male,Other,Undergraduate,YouTube,Education,6.0,200,2.3,1.1,5.6,Very High,4.2
18,Male,Other,High School,TikTok,Entertainment,2.3,106,6.3,1.8,8.0,Low,7.2
22,Female,Other,Undergraduate,TikTok,Entertainment,2.3,93,5.8,3.6,8.0,Low,8.5
19,Male,India,Undergraduate,Twitter,News,3.5,145,4.6,2.5,6.0,Medium,7.0
22,Male,Other,Undergraduate,Instagram,Entertainment,7.8,254,1.0,0.9,6.0,Very High,5.3
19,Male,UK,Undergraduate,Instagram,Entertainment,7.4,223,1.0,1.8,5.2,Very High,4.7
20,Female,Germany,Undergraduate,LinkedIn,Education,3.2,124,4.2,2.5,8.9,Low,7.5
23,Male,Australia,Graduate,Twitter,News,5.8,177,1.9,2.5,4.8,Very High,5.0
21,Female,Other,Undergraduate,Instagram,Entertainment,6.9,204,1.6,0.5,5.7,Very High,4.6
22,Male,Other,Undergraduate,Twitter,News,2.6,100,5.4,2.2,8.2,Medium,7.2
20,Male,Other,Undergraduate,YouTube,Education,2.3,96,6.0,2.2,7.2,Medium,7.4
23,Male,USA,Graduate,Instagram,Entertainment,5.5,172,3.0,0.6,5.9,High,4.3
24,Male,Australia,Graduate,Snapchat,Entertainment,4.0,131,3.7,2.5,8.6,Medium,8.6
19,Male,Other,Undergraduate,LinkedIn,Education,6.2,197,2.4,1.3,4.7,Very High,4.3
18,Male,Other,High School,Snapchat,Entertainment,4.7,166,3.6,2.2,6.1,Medium,6.6
20,Female,UK,Undergraduate,YouTube,Education,3.7,130,3.3,3.3,8.6,Medium,8.4
19,Female,Other,Undergraduate,LinkedIn,Education,6.0,196,3.2,1.3,6.0,Very High,5.8
24,Male,Other,Graduate,TikTok,Entertainment,7.8,230,1.0,0.8,5.0,Very High,4.8
20,Male,USA,Undergraduate,Instagram,Entertainment,3.9,150,2.8,2.1,6.6,Medium,6.8
19,Female,Other,Undergraduate,YouTube,Education,7.2,230,1.0,1.7,5.9,Very High,5.0
21,Female,Other,Undergraduate,Twitter,News,6.2,218,1.0,1.2,5.4,Very High,5.4
21,Female,Canada,Undergraduate,Twitter,News,7.7,219,1.0,0.8,5.6,Very High,4.5
22,Male,USA,Undergraduate,Twitter,News,4.0,159,3.8,2.5,7.6,Medium,8.6
22,Female,USA,Undergraduate,LinkedIn,Education,4.2,143,3.5,2.1,6.8,High,6.5
24,Female,USA,Graduate,LinkedIn,Education,3.9,124,4.6,1.0,7.2,Medium,6.7
21,Male,UK,Undergraduate,TikTok,Entertainment,4.7,169,3.6,1.2,6.2,High,6.3
23,Male,India,Graduate,Snapchat,Entertainment,7.3,213,1.0,1.9,5.0,Very High,5.8
23,Female,India,Graduate,TikTok,Entertainment,6.4,192,1.9,1.6,5.3,Very High,4.9
20,Female,Other,Undergraduate,YouTube,Education,3.3,146,5.2,1.8,7.4,Low,7.1
19,Female,Other,Undergraduate,Twitter,News,6.7,200,1.0,1.2,6.0,Very High,4.6
21,Male,Other,Undergraduate,Facebook,Networking,7.6,236,1.0,1.1,5.1,Very High,4.3
23,Male,Other,Graduate,Instagram,Entertainment,4.5,145,1.8,2.2,6.6,High,6.3
19,Male,Other,Undergraduate,YouTube,Education,3.0,104,5.0,1.6,7.1,Medium,8.3
21,Female,Other,Undergraduate,Facebook,Networking,6.2,180,1.8,1.0,5.1,Very High,4.6
18,Female,Other,High School,Instagram,Entertainment,6.6,190,2.2,1.5,5.4,Very High,5.4
23,Male,Other,Graduate,Twitter,News,8.4,253,1.0,0.9,4.6,Very High,5.6
23,Female,UK,Graduate,Snapchat,Entertainment,7.0,217,1.2,1.5,5.6,High,5.9
23,Female,USA,Graduate,Snapchat,Entertainment,7.9,223,1.0,0.4,5.8,Very High,5.1
24,Female,Other,Graduate,Facebook,Networking,3.6,128,4.8,2.3,8.4,Low,8.9
24,Male,Canada,Graduate,Snapchat,Entertainment,5.5,172,2.1,2.2,4.6,Very High,5.1
21,Male,Other,Undergraduate,Instagram,Entertainment,2.0,97,6.0,2.7,7.1,Low,7.7
19,Male,Australia,Undergraduate,Facebook,Networking,5.8,209,3.0,1.6,7.4,High,6.2
18,Female,Other,High School,YouTube,Education,6.3,209,1.3,1.4,5.5,High,4.2
19,Male,Other,Undergraduate,LinkedIn,Education,3.2,141,5.4,1.8,9.0,Low,8.3
24,Female,Other,Graduate,YouTube,Education,1.7,74,6.8,2.5,8.5,Low,8.8
18,Female,Other,High School,Snapchat,Entertainment,7.0,208,1.0,1.9,4.8,Very High,4.4
22,Male,Other,Undergraduate,Snapchat,Entertainment,4.8,175,4.0,1.7,6.4,High,6.4
24,Female,Other,Graduate,Facebook,Networking,6.4,197,2.2,1.0,5.0,Very High,4.5
23,Male,India,Graduate,TikTok,Entertainment,1.8,103,6.3,2.3,8.7,Low,7.5
18,Male,Other,High School,Twitter,News,7.0,218,1.0,1.4,5.1,Very High,4.8
22,Male,Other,Undergraduate,YouTube,Education,2.6,98,4.7,2.2,7.7,Low,8.4
21,Female,Other,Undergraduate,Twitter,News,1.7,100,5.9,2.8,7.3,Medium,8.0
20,Male,Other,Undergraduate,Instagram,Entertainment,5.0,172,3.4,2.0,7.0,Medium,6.8
23,Male,Other,Graduate,Instagram,Entertainment,6.0,207,1.2,1.9,5.4,Very High,5.1
19,Female,Other,Undergraduate,YouTube,Education,8.3,250,1.0,1.6,5.9,Very High,4.7
21,Male,Other,Undergraduate,LinkedIn,Education,3.7,122,3.3,2.6,7.0,Medium,8.5
18,Female,Other,High School,Snapchat,Entertainment,8.4,262,1.0,0.4,5.5,Very High,5.6
19,Female,Other,Undergraduate,Twitter,News,5.5,166,2.6,1.2,5.1,Very High,5.3
21,Male,Other,Undergraduate,YouTube,Education,8.0,251,2.0,1.0,5.0,Very High,4.6
22,Male,Australia,Undergraduate,YouTube,Education,2.2,96,4.7,2.2,8.6,Low,8.6
22,Female,Other,Undergraduate,Twitter,News,7.2,236,2.0,0.6,5.9,Very High,5.3
18,Male,Other,High School,Instagram,Entertainment,5.9,206,2.2,1.3,5.6,Very High,4.5
24,Male,Other,Graduate,Instagram,Entertainment,7.0,216,1.3,1.0,5.8,Very High,5.1
18,Female,Germany,High School,YouTube,Education,1.9,107,6.2,2.2,7.7,Low,7.8
20,Male,Other,Undergraduate,YouTube,Education,6.0,179,2.4,1.3,5.3,Very High,5.0
18,Male,India,High School,Snapchat,Entertainment,5.3,161,2.6,2.3,6.3,High,6.6
18,Male,Other,High School,Snapchat,Entertainment,7.1,241,2.1,1.3,4.6,Very High,5.2
22,Female,Other,Undergraduate,YouTube,Education,6.2,202,1.4,2.7,5.6,Very High,4.6"""

os.makedirs("data", exist_ok=True)
with open("data/dataset.csv", "w", newline='') as f:
    f.write(data_header + "\n")
    f.write(dataset_rows)

print(f"Dataset created with header: {data_header}")
print("Done")
