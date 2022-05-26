from difflib import get_close_matches
from pprint import pprint
import pandas as pd


mapper = {
    "name": ["name", "first_name", "firstname", "last_name", "user_name", "from", "usersname", "studentname"],
    "email": ["email", "user_email", "mail"],
    "phonenumber": ["phonenumber", "phno", "fatherscontactnumber", "motherscontactnumber", "mobile", "phone_number", "phone", "contact", "contact_number", "studentmobile"],
    "city": ["user_city", "city", "selectedcity"],
    "course": ["course", "course_name", "course_code", "course_title", "responsetocourse"],
    "program": ["program", "program_name", "program_code", "program_title"],
}
courseMapper = {
    "BBA": ["BBA/BBM", "Bachelor of Business Administration (BBA)", "Student interested in BBA courses"],
    "MBA": ["MBA/PGDM", "Master of Business Administration (MBA)", "Student interested in MBA/PGDM courses", "Master of Business Administration(MBA)"],
    "MCA": ["MCA/PGPM", "Master of Computer Applications (MCA)", "Student interested in MCA courses", "Master of Computer Applications(MCA)"],
    "CSE": ["B.E. in Computer Science and Engineering", "Computer Science & Engineering (CSE)"],
    "CSE in Data Science": ["B. E in Computer Science & Engineering (Data Science)", "Computer Science & Engineering (Data Science)"],
    "AI/ML": ["AIML", "B.E. in Artificial Intelligence and Machine Learning", "Artificial Intelligence and Machine Learning(AIML)", ],
    "CIVIL": ["B.E. in Civil Engineering", "Civil Engineering (CIV)"],
    "ECE": ["B.E. in Electronics and Communication Engineering", "Electronics & Communication Engineering (ECE)"],
    "MECH": ["B.E. in Mechanical Engineering", "Mechanical Engineering (ME)", "Mechanical Engineering (MECH)"],
    "ISE": ["B.E. in Information Science and Engineering", "B.E. in Information Technology", "Information Science & Engineering (ISE)"],
    "B.Com": ["Bachelor of Commerce (B.Com.)", "Student interested in B.Com courses"],
    "BCA": ["Bachelor of Computer Application (BCA)", "Student interested in BCA courses"],
    "BE/B.Tech Courses": ["Student interested in B.E. / B.Tech courses"],
    "ME/M.Tech": ["Student interested in M.E./M.Tech courses", "MTech- Computer Science & Engg"],
    "EEE": ["Electrical & Electronics Engineering (EEE)"],
    "CE": ["Computer Engineering(CO)", "B.E. in Computer Engineering"],
}


def sanitize(filename, source):
    df = pd.read_csv("uploads/"+filename)
    # sanitizing column names
    sanitizedCols = []
    for col in list(df.columns.values):
        sanitizedCols.append(sanitizeString(col))
    df.columns = sanitizedCols

    # converting to string
    for colname in df.columns:
        try:
            df[colname] = df[colname].astype('str')
            print(f"{colname} converted")
        except ValueError:
            print(f"{colname} failed")
    # specific transformations
    if source == "cd":
        print(df.columns)
        df = df.rename(columns={"course": "program",
                                "branch": "course"})
    if source == "sk":
        print(df.columns)
        df = df.drop(['locality', 'lastname'], axis=1)

    # print(list(df.columns.values))
    k = {}  # cols
    kk = {}  # courses
    alteredCols = []
    for i in list(df.columns.values):
        if checkSim(i):
            k[i] = checkSim(i)
            alteredCols.append(k[i])
        else:
            k[i] = i
    df = df.rename(columns=k)
    # print(alteredCols)
    # pprint(k)
    if "course" in list(df.columns.values):
        print("Course column found")
        df['course'] = df['course'].fillna("")
        for i in list(df['course'].values):
            if checkSimCourse(i):
                kk[i] = checkSimCourse(i)
            else:
                kk[i] = i
        pprint(kk)
        for old, new in kk.items():
            df["course"].replace([old.strip()], new.strip(), inplace=True)
    df = df[alteredCols]
    print(df)
    return df.to_json(orient='records'), alteredCols


def sanitizeString(string):
    string = string.lower()
    for i in string:
        if i not in "abcdefghijklmnopqrstuvwxyz":
            string = string.replace(i, "")
    return string


def reverseMapper():
    reverse = {}
    for key, value in mapper.items():
        for v in value:
            reverse[v] = key
    return reverse


def reverseCourseMapper():
    reverse = {}
    for key, value in courseMapper.items():
        for v in value:
            reverse[v] = key
    return reverse


def checkSim(word):
    reverse = reverseMapper()
    if word in reverse:
        return reverse[word]
    else:
        simi = get_close_matches(word, reverse.keys())
        if len(simi) > 0:
            for i in simi:
                if i in mapper.keys():
                    return i
        return None


def checkSimCourse(word):
    reverse = reverseCourseMapper()
    if word in reverse:
        return reverse[word]
    else:
        simi = get_close_matches(word, reverse.keys())
        if len(simi) > 0:
            for i in simi:
                if i in mapper.keys():
                    return i
        return None


# print(checkSim("user_phone_number"))
