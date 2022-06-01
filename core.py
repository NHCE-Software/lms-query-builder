from difflib import get_close_matches
from pprint import pprint

import numpy as np
import pandas as pd


mapper = {
    "name": ["name", "first_name", "firstname", "last_name", "nameofthestudent",  "username", "user_name", "usersname", "studentname"],
    "email": ["email", "user_email", "mail"],
    "phonenumber": ["phonenumber", "phno", "fatherscontactnumber", "mobile", "phone_number", "phone", "contact", "contact_number", "studentmobile"],
    "phonenumber2": ["motherscontactnumber", "secondarycontactnumber", "secondarycontact", "secondarycontactnumber", "studentsecondarycontact"],
    "city": ["user_city", "city", "selectedcity"],
    "state": ["state", "user_state", "State",  "selectedstate", "Student State", "studentstate"],
    "course": ["course", "course_name", "course_code", "course_title", "responsetocourse"],
    "program": ["program", "program_name", "program_code", "program_title"],
}
courseMapper = {
    "BBA": ["bba", "BBA/BBM", "Bachelor of Business Administration (BBA)", "Student interested in BBA courses"],
    "MBA": ["MBA/PGDM", "mba", "Master of Business Administration (MBA)", "Student interested in MBA/PGDM courses", "Master of Business Administration(MBA)"],
    "MCA": ["mca", "MCA/PGPM", "Master of Computer Applications (MCA)", "Student interested in MCA courses", "Master of Computer Applications(MCA)"],
    "CSE": ["KCET (CSE)", "cse", "B.E. in Computer Science and Engineering", "Computer Science & Engineering (CSE)"],
    "CSE in Data Science": ["B. E in Computer Science & Engineering (Data Science)", "Computer Science & Engineering (Data Science)"],
    "AI/ML": ["AIML", "B.E. in Artificial Intelligence and Machine Learning", "Artificial Intelligence and Machine Learning(AIML)", ],
    "CIVIL": ["civil", "B.E. in Civil Engineering", "Civil Engineering (CIV)"],
    "ECE": ["ece", "B.E. in Electronics and Communication Engineering", "Electronics & Communication Engineering (ECE)"],
    "MECH": ["mech", "B.E. in Mechanical Engineering", "Mechanical Engineering (ME)", "Mechanical Engineering (MECH)"],
    "ISE": ["ise", "B.E. in Information Science and Engineering", "B.E. in Information Technology", "Information Science & Engineering (ISE)"],
    "B.Com": ["bcom", "Bachelor of Commerce (B.Com.)", "Student interested in B.Com courses"],
    "BCA": ["bca", "Bachelor of Computer Application (BCA)", "Student interested in BCA courses"],
    "BE/B.Tech Courses": ["Student interested in B.E. / B.Tech courses"],
    "ME/M.Tech": ["Student interested in M.E./M.Tech courses", "MTech- Computer Science & Engg"],
    "EEE": ["eee", "Electrical & Electronics Engineering (EEE)"],
    "CE": ["ce", "Computer Engineering(CO)", "B.E. in Computer Engineering"],
}

customSource = ["name", "email", "phonenumber",
                "city", "state", "program", "course", "calls", "createdAt"]


def sanitize(filename, source):
    df = pd.read_csv("uploads/"+filename)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(how='all')

    # sanitizing column names
    sanitizedCols = []
    for col in list(df.columns.values):
        sanitizedCols.append(sanitizeString(col))
    df.columns = sanitizedCols

    # converting to string
    for colname in df.columns:
        try:
            df[colname] = df[colname].astype('str')
            # print(f"{colname} converted")
        except ValueError:
            print(f"{colname} failed")
    # generic drops
    df = df.drop("unnamed", axis=1, errors='ignore')
    # specific transformations
    if source == "cd":
        print("Applying CD transform", df.columns)
        df = df.rename(columns={"course": "program",
                                "branch": "course"})
        print("Applying CD transform", df.columns)
    if source == "sk":
        print(df.columns)
        df = df.drop(['locality'], axis=1, errors='ignore')
        df['firstname'] = df['firstname'].replace("nan", "")
        df['lastname'] = df["lastname"].replace("nan", "")
        df['name'] = df[['firstname', 'lastname']].agg(" ".join, axis=1)
        df = df.drop(["firstname", "lastname"], axis=1, errors='ignore')

    if source == "wa":
        df = df.drop(['date', "createdat"], axis=1, errors='ignore')
        try:
            df['phonenumber'] = df[['fatherscontactnumber', "motherscontactnumber" , "studentmobile"]].agg(" ".join, axis=1)
            df = df.drop(['fatherscontactnumber', "motherscontactnumber" , "studentmobile"], axis=1, errors='ignore')
        except KeyError:
            print("no phones")


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
    pprint(k)
    print(alteredCols)
    if "course" in list(df.columns.values):
        print("Course column found")
        df['course'] = df['course'].fillna("")
        df['course'] = df['course'].str.strip()
        df['course'] = df['course'].replace("nan", "")
        for i in list(df['course'].values):
            if checkSimCourse(i):
                kk[i] = checkSimCourse(i)
            else:
                kk[i] = i
        # pprint(kk)
        for old, new in kk.items():
            df["course"].replace([old.strip()], new.strip(), inplace=True)
    df = df[alteredCols]
    df = df.replace("nan", "")
    df = df.replace("nan nan", "")
    return df.to_json(orient='records'), alteredCols


def csanitize(filename):
    df = pd.read_csv("uploads/"+filename, skip_blank_lines=True)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(how='all')
    #print(df)
    df = df.fillna("")
    df = df.astype(str)

    # mapping columns
    res = []
    for i in range(len(df)):
        obj = {}
        for j in range(len(customSource)):
            if(df.iat[i, j] == "nan"):
                obj[customSource[j]] = ""
            else:
                obj[customSource[j]] = df.iat[i, j]
        res.append(obj)
    print(res)

    for i in res:
        i["phonenumber"] = str(i["phonenumber"]).split(".")[0]
    print(df)
    return res, customSource


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
