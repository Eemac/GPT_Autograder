import requests
import os
import base64

import time
import json
from secret_constants import CANVAS_API_TOKEN, CANVAS_API_URL, GPT_API_TOKEN, GPT_API_URL

import urllib.request
import shutil

from pdf2image import convert_from_path
# from PIL import Image

COURSE_ID = ""
ASSIGNMENT_ID = ""

#Output data from canvas
#name, id
students = dict()
#id
gradingIds = []
#rubric (text)
assignmentRubric = ""

waitBarChars = 30

# Headers for authentication
headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
jsonOptions = "?per_page=200&enrollment_type=student"


##########################################################################################################################
##################################################    Init Functions    ##################################################
##########################################################################################################################
#Get dict of course info
def getCourses():
    id_url = (f"{CANVAS_API_URL}/courses/")
    id_url += "?per_page=200&enrollment_type=teacher"

    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        names, courseIds = [], []
        for element in jsonObj:
            names.append(element['name'])
            courseIds.append(element['id'])
        output = dict(names = names, courseIds = courseIds)
        return output
    else:
        print(f"Failed to fetch ids: {response.status_code}")
        return -1

def getCourseAssignments(course_id):
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments")
    id_url += jsonOptions

    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        assignments, assignmentIds = [], []
        for element in jsonObj:
            assignments.append(element['name'])
            assignmentIds.append(element['id'])
        output = dict(assignments = assignments, assignmentIds = assignmentIds)
        return output
    else:
        print(f"Failed to fetch assignment: {response.status_code}")
        return -1

def getStudentIds(course_id):
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/users")
    id_url += jsonOptions

    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        students, studentIds = [], []
        for element in jsonObj:
            students.append(element['name'])
            studentIds.append(element['id'])
        output = dict(students = students, studentIds = studentIds)
        return output
    else:
        print(f"Failed to fetch student ids: {response.status_code}")
        return -1

def getStudentSubmissionLinks(course_id, assignment_id, students, totalPoints):
    print("Gathering Student Submissions:    0% |" + " "*(waitBarChars) + "|", end="\r")
    studentIds, assignmentLinks = [], []

    # Clear previous files
    resetAssignmentDirectory()

    # download and prep assignments that need to get graded
    for i, student in enumerate(students):
        id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/")
        id_url += str(student)
        id_url += jsonOptions

        response = requests.get(id_url, headers=headers)

        print("\rGathering Student Submissions:  " + str(round(100 * (i+1) / len(students))).rjust(3, " ") + "% |" + "="*int(round(waitBarChars * (i+1) / len(students))) + " "*int(round(waitBarChars - (waitBarChars * (i+1) / len(students)))) + "|", end="\r")
    
        if response.status_code == 200:
            jsonObj = response.json()
            if(jsonObj["attempt"] != None and ((jsonObj["grade_matches_current_submission"] == False and jsonObj["score"] != None) or jsonObj["score"] == None)):
                studentIds.append(student)
                downloadAndFormatPDF(str(student), jsonObj["attachments"][0]["url"])

        else:
            print(f"Failed to fetch links: {response.status_code}")
            return -1

    return studentIds

def getAssignmentRubric(course_id, assignment_id):
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}")
    id_url += jsonOptions

    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()

        output = dict(rubric = jsonObj["rubric"], totalPoints = str(jsonObj["rubric_settings"]["points_possible"]), name = jsonObj["rubric_settings"]["title"])
        return output
        #may want to inlcude total points
    else:
        print(f"Rubric missing or unreachable: {response.status_code}")
        return -1

def resetAssignmentDirectory():
    # Reset directory and remove files
    dirpath = os.path.join('assignmentData')
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.mkdir('assignmentData')

def downloadAndFormatPDF(id, link):
    # Create student ID directory
    os.mkdir('assignmentData/' + id)
    urllib.request.urlretrieve(link, "assignmentData/" + id + "/"+ id + ".pdf")

    pages = convert_from_path("assignmentData/" + id + "/"+ id + ".pdf", 100)
    for count, page in enumerate(pages):
        page.save("assignmentData/" + id + "/" + f'out{count}.jpg', 'JPEG')

    os.remove("assignmentData/" + id + "/"+ id + ".pdf")

def init():
    try:
        print("\x1b[2J\x1b[H")
        print("\x1b[2J\x1b[H" + "\r-------------------------------------------------------------------------------------\n")
        output = getCourses()
        print("Select Class by Number")
        # print(output)
        for i, name in enumerate(output["names"]):
            print(str(i) + "\t" + name)

        try:
            classNumUserInput = int(input("\nInput Class by Number: "))
            if(classNumUserInput > len(output["names"]) - 1):
                print("Input higher than number of availaible classes. Exiting...")
                return -1
        except:
            print("Not a number. Exiting...")
            return -1

        global COURSE_ID
        COURSE_ID = output["courseIds"][classNumUserInput]
        print("\nSelected Course: " + output["names"][classNumUserInput])
        print("-------------------------------------------------------------------------------------\n")



        output = getCourseAssignments(COURSE_ID)
        print("Select Assignment to Grade")
        # print(output)
        for i, assignment in enumerate(output["assignments"]):
            print(str(i) + "\t" + assignment)

        try:
            assignmentNumUserInput = int(input("\nInput Assignment by Number: "))
            if(assignmentNumUserInput > len(output["assignments"]) - 1):
                print("Input higher than number of availaible assignments. Exiting...")
                return -1
        except:
            print("Not a number. Exiting...")
            return -1

        global ASSIGNMENT_ID
        ASSIGNMENT_ID = output["assignmentIds"][assignmentNumUserInput]

        print("\nSelected Assignment: " + output["assignments"][assignmentNumUserInput])
        print("-------------------------------------------------------------------------------------\n")




        print("Fetching Assignment Rubric...")

        global assignmentRubric
        assignmentRubric = getAssignmentRubric(COURSE_ID, ASSIGNMENT_ID)

        if(float(assignmentRubric["totalPoints"]) > 0):
            print("Found Rubric: \'" + assignmentRubric["name"] + "\' with maximum score of: " + assignmentRubric["totalPoints"])
        print("-------------------------------------------------------------------------------------\n")




        global students
        students = getStudentIds(COURSE_ID)

        global gradingIds
        gradingIds = getStudentSubmissionLinks(COURSE_ID, ASSIGNMENT_ID, students["studentIds"], assignmentRubric["totalPoints"])
        
        print("\n\nThe Assignments of the Following Students will be Graded:")
        for i, studentId in enumerate(students["studentIds"]):
            if(studentId in gradingIds):
                print(students["students"][i]);

        print("\nTotal Submissions to be Graded: " + str(len(gradingIds)))
        print("-------------------------------------------------------------------------------------\n")



        print("Autograder will grade all new submissions and replace the old grades. Continue? (Y/N)")
        if input().upper() != "Y":
            print("Check failed. Exiting...")
            return -1


    except Exception as error:
        print("Canvas Initialization Error Occured. Exiting...")
        print(error)
        return -1
    finally:
         print("-------------------------------------------------------------------------------------\n")

##########################################################################################################################
##################################################    AI Integration    ##################################################
##########################################################################################################################
def getGPTResponses(gradingIds):
    # Configuration
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT_API_TOKEN,
    }

    payloads = []

    # Payload for the request
    initialPayload = {
      "messages": [
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": "You are an electrical engieering college professor. Using the following rubric image, grade the attached introductory lab"
            },
            {
              "type": "text",
              "text": json.dumps(assignmentRubric)
            },
          ]
        }
      ],
      "temperature": 0.7,
      "top_p": 0.95,
      "max_tokens": 4000
    }

    base64_image = ""

    for i, id in enumerate(gradingIds):
        fileNames = os.listdir("assignmentData/" + str(id) + "/")
        payloads.append(initialPayload)

        for file in fileNames:
            with open("assignmentData/" + str(id) + "/" + file, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            imageText = {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            
            payloads[i]['messages'][0]['content'].append(imageText)

        # print(json.dumps(payloads[i], indent=4))
        
        # Send request
        try:
            response = requests.post(GPT_API_URL, headers=headers, json=payloads[i])
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        except requests.RequestException as e:
            raise SystemExit(f"Failed to make the request. Error: {e}")

        # Handle the response as needed (e.g., print or process)
        
        # print(json.dumps(response.json(), indent=4))

##########################################################################################################################
##################################################    ISIM AUTOGRADER    #################################################
##########################################################################################################################

if __name__ == "__main__":
    # Fetch resources (COURSE_ID, ASSIGNMENT_ID, students, assignmentLinks, assignmentRubric)
    if(init() == -1):
        exit()

    responses = getGPTResponses(gradingIds)


    # else:
    #     print(assignmentLinks["assignmentLinks"][0])
    # testGPT()



