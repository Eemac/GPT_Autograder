# HTTP GET/PUT requests
import requests

# Dealing with files on local machine
import os

# For converting images to strings that can be sent to Azure
import base64

# Delays
import time

# Parsing requests to/from APIs
import json

# PDF downloads
import urllib.request

# Edit directories
import shutil

# Convert PDF into several images
from pdf2image import convert_from_path

# API tokens and access URLs
from secret_constants import CANVAS_API_TOKEN, CANVAS_API_URL, GPT_API_TOKEN, GPT_API_URL

# Progress bar length
waitBarChars = 30

# Headers for authentication
headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}


################################################################################################################################################
#############################################################    Init Functions    #############################################################
################################################################################################################################################
#Get list of courses that the user is teaching
def getCourses():
    # GET request for all courses
    id_url = (f"{CANVAS_API_URL}/courses/")
    # Only list 'teacher' enrollments, prevent issues with pagination by setting per_page=200 (default is 10)
    id_url += "?per_page=200&enrollment_type=teacher"

    # Send request + receive json object
    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        courseNames, courseIds = [], []
        for element in jsonObj:
            courseNames.append(element['name'])
            courseIds.append(element['id'])

        return courseNames, courseIds
    else:
        print(f"Failed to fetch ids: {response.status_code}")
        print("Canvas API key likely missing or invalid")
        print("To add or update an API key, check the autograder documentation")
        exit()

# Get list of assignments for the selected class
def getCourseAssignments(course_id):
    # GET request for all course assignements
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments")
    # Only list 'student' enrollments, prevent issues with pagination by setting per_page=200 (default is 10)
    id_url += "?per_page=200&enrollment_type=student"

    # Send request + receive json object
    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        assignments, assignmentIds, assignmentMaxScore= [], [], []
        for element in jsonObj:
            assignments.append(element['name'])
            assignmentIds.append(str(element['id']))
            assignmentMaxScore.append(element['points_possible'])
        return assignments, assignmentIds, assignmentMaxScore
    else:
        print(f"Failed to fetch assignment: {response.status_code}")
        exit()

# get rubric for selected assignment
def getAssignmentRubric(course_id, assignment_id):
    # GET request for all course assignements
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}")
    # Only list 'student' enrollments, prevent issues with pagination by setting per_page=200 (default is 10)
    id_url += "?per_page=200&enrollment_type=student"

    # Send request + receive json object
    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()

        rubric = jsonObj["rubric"]
        rubricMaxPoints = str(jsonObj["rubric_settings"]["points_possible"])
        rubricName = str(jsonObj["rubric_settings"]["title"])

        return rubric, rubricName, rubricMaxPoints
    else:
        print(f"Rubric missing or unreachable: {response.status_code}")
        exit()

# Get list of students enrolled in the class
def getStudentIds(course_id):
    id_url = (f"{CANVAS_API_URL}/courses/{course_id}/users")
    id_url += "?per_page=200&enrollment_type=student"

    response = requests.get(id_url, headers=headers)

    if response.status_code == 200:
        jsonObj = response.json()
        
        studentNames, studentIds = [], []
        for element in jsonObj:
            studentNames.append(element['name'])
            studentIds.append(element['id'])
        return studentNames, studentIds
    else:
        print(f"Failed to fetch student ids: {response.status_code}")
        exit()

# Get PDF links for each student that needs a grade, download the PDF, and convert to JPEG images
def getStudentSubmissionLinks(course_id, assignment_id, studentIds):
    print("Gathering Student Submissions:    0% |" + " "*(waitBarChars) + "|", end="\r")
    gradingIds, assignmentLinks = [], []

    # Clear previous files
    resetAssignmentDirectory()

    # download and prep assignments that need to get graded
    for i, student in enumerate(studentIds):
        id_url = (f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/")
        id_url += str(student)
        id_url += "?per_page=200&enrollment_type=student"

        response = requests.get(id_url, headers=headers)

        # Progress bar
        print("\rGathering Student Submissions:  " + str(round(100 * (i+1) / len(studentIds))).rjust(3, " ") + "% |" + "="*int(round(waitBarChars * (i+1) / len(studentIds))) + " "*int(round(waitBarChars - (waitBarChars * (i+1) / len(studentIds)))) + "|", end="\r")
    
        if response.status_code == 200:
            jsonObj = response.json()
            if(jsonObj["attempt"] != None and ((jsonObj["grade_matches_current_submission"] == False and jsonObj["score"] != None) or jsonObj["score"] == None)):
                gradingIds.append(student)
                downloadAndFormatPDF(str(student), jsonObj["attachments"][0]["url"])

        else:
            print(f"Failed to fetch links: {response.status_code}")
            exit()

    return gradingIds

# Clear (or create) files directory before starting downloads
def resetAssignmentDirectory():
    # Reset directory and remove files
    dirpath = os.path.join('assignmentData')
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    os.mkdir('assignmentData')

# Convert student PDFs to series of JPEG images and store them in a folder
def downloadAndFormatPDF(id, link):
    # Create student ID directory
    os.mkdir('assignmentData/' + id)
    urllib.request.urlretrieve(link, "assignmentData/" + id + "/"+ id + ".pdf")

    pages = convert_from_path("assignmentData/" + id + "/"+ id + ".pdf", 80)
    for count, page in enumerate(pages):
        page.save("assignmentData/" + id + "/" + f'out{count}.jpg', 'JPEG')

    os.remove("assignmentData/" + id + "/"+ id + ".pdf")

# Get data from Canvas API
def init():
    try:
        # Reset the screen
        print("\x1b[2J\x1b[H" + "\r-------------------------------------------------------------------------------------\n")

        ########################################################################################################################################
        # Get a list of courses, print them out, and prompt the user to select one
        courseNames, courseIds = getCourses()

        print("Select Class by Number")
        for i, name in enumerate(courseNames):
            print(str(i) + "\t" + name)

        try:
            classNumUserInput = int(input("\nInput Class by Number: "))

            if(classNumUserInput > len(courseNames) - 1):
                print("Input higher than number of availaible classes. Exiting...")
                exit()
        except:
            print("Not a number. Exiting...")
            exit()

        selectedCourseId = courseIds[classNumUserInput]
        print("\nSelected Course: " + courseNames[classNumUserInput])
        print("-------------------------------------------------------------------------------------\n")


        ########################################################################################################################################
        # Get a list of assignments for that course, list them, and prompt the user to select one
        assignments, assignmentIds, assignmentMaxScores = getCourseAssignments(selectedCourseId)
        print("Select Assignment to Grade")

        for i, assignment in enumerate(assignments):
            print(str(i) + "\t" + assignment)

        try:
            assignmentNumUserInput = int(input("\nInput Assignment by Number: "))
            if(assignmentNumUserInput > len(assignments) - 1):
                print("Input higher than number of availaible assignments. Exiting...")
                exit()
        except:
            print("Not a number. Exiting...")
            exit()

        selectedAssignmentId = assignmentIds[assignmentNumUserInput]
        selectedAssignmentMaxScore = assignmentMaxScores[assignmentNumUserInput]

        print("\nSelected Assignment: " + assignments[assignmentNumUserInput])
        print("-------------------------------------------------------------------------------------\n")


        ########################################################################################################################################
        # Get rubric to grade against
        print("Fetching Assignment Rubric...")

        rubric, rubricName, rubricMaxPoints = getAssignmentRubric(selectedCourseId, selectedAssignmentId)

        if(float(rubricMaxPoints) > 0):
            print("Found valid rubric: \'" + rubricName + "\' with maximum score of: " + rubricMaxPoints)
        print("-------------------------------------------------------------------------------------\n")


        ########################################################################################################################################
        # Get list of students enrolled in the class (names and canvas IDs)
        studentNames, studentIds = getStudentIds(selectedCourseId)

        # Get list of students (Ids) that need graded reports and pull their canvas PDFs
        gradingIds = getStudentSubmissionLinks(selectedCourseId, selectedAssignmentId, studentIds)

        print("\n\nThe Assignments of the Following Students will be Graded:")
        for i, studentId in enumerate(studentIds):
            if(studentId in gradingIds):
                print(studentNames[i]);

        print("\nTotal Submissions to be Graded: " + str(len(gradingIds)))
        print("-------------------------------------------------------------------------------------\n")

        print("Autograder will grade all new submissions and replace the old grades. Continue? (Y/N)")
        if input().upper() != "Y":
            print("Check failed. Exiting...")
            exit()

        print("-------------------------------------------------------------------------------------\n")

        return selectedCourseId, selectedAssignmentId, studentNames, studentIds, gradingIds, rubric, rubricMaxPoints, selectedAssignmentMaxScore

    except Exception as error:
        print("Canvas Initialization Error Occured. Exiting...")
        print(error)
        print("-------------------------------------------------------------------------------------\n")
        exit()


################################################################################################################################################
#############################################################    AI Integration    #############################################################
################################################################################################################################################
# Format request to Azure
def getGPTResponses(gradingIds, studentNames, studentIds, rubric):
    responses = []
    # Configuration
    headers = {
        "Content-Type": "application/json",
        "api-key": GPT_API_TOKEN,
    }

    print("Gathering AI Submission Responses:    0% |" + " "*(waitBarChars) + "|", end="\r")

    for i, id in enumerate(gradingIds):  
        payload = generateAzurePayload(id, rubric)

        # Send request
        try:
            response = requests.post(GPT_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            resp = response.json()
        except requests.RequestException as e:
            raise SystemExit(f"Failed to make the request. Error: {e}")

        # Handle the response as needed (e.g., print or process)
        output = json.loads(resp["choices"][0]["message"]["content"])
        bb = 0
        responses.append(output)

        print("\rGathering AI Submission Responses:  " + str(round(100 * (i+1) / len(gradingIds))).rjust(3, " ") + "% |" + "="*int(round(waitBarChars * (i+1) / len(gradingIds))) + " "*int(round(waitBarChars - (waitBarChars * (i+1) / len(gradingIds)))) + "|", end="\r")

    if len(responses) > 1:
        print("\n\nRecieved " + str(len(responses)) + " Valid Responses. The scores are listed below:")
    else:
        print("\n\nRecieved one valid response. The score is listed below:")

    for i, studentId in enumerate(gradingIds):
        totalScore = 0
        for element in responses[i]:
            totalScore += float(element["score"])

        print(str(studentNames[(studentIds.index(studentId))] + "\'s Score:").ljust(50) + str(totalScore))



    print("-------------------------------------------------------------------------------------\n")
    return responses

# Create text-based payload (includes prompt, rubric, and base64-encoded submission images)
def generateAzurePayload(id, rubric):
    base64_image = ""

    # Payload for the request
    initialPayload = {
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "You are an electrical engieering college professor. Students are completing a class about intraductory analog electronics for use in sensing applicaitons. All power sources are assumed to come from an oscilloscope-like device called the O-scope. All components should be labeled with values in schematics. Using the following rubric file, grade the attached introductory lab and give helpful feedback to the student. Also, don't repeat the rubric word-for-word in your response. Format your response as a json array, with a \'score\' key and \'comments\' key for each, and no further json structure. No formatting, and no newlines/whitespace"
            },
            {
              "type": "text",
              "text": json.dumps(rubric)
            },
          ]
        }
      ],
      "temperature": .8,
      "top_p": 0.85,
      "max_tokens": 4000
    }

    fileNames = os.listdir("assignmentData/" + str(id) + "/")
    payload = dict(initialPayload)

    for file in fileNames:
        with open("assignmentData/" + str(id) + "/" + file, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        imageText = {
            "type": "image_url",
            "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"
            }
        }
        
        payload['messages'][0]['content'].append(imageText)

    return payload


################################################################################################################################################
##########################################################    Canvas Rubric Grading    #########################################################
################################################################################################################################################
# Push the rubrics to canvas
def uploadRubrics(responses, course_id, assignment_id, gradingIds, rubric, rubricMaxPoints, selectedAssignmentMaxScore):
    print("Uploading grades and comments to Canvas...")
    for i, response in enumerate(responses):
        url = f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/" + str(gradingIds[i])

        gradedResponse = dict()
        
        totalPoints = 0
        for elementOrder, element in enumerate(rubric):
            gradedResponse["rubric_assessment[" + element["id"] + "][points]"] = str(response[elementOrder]["score"])
            totalPoints += float(response[elementOrder]["score"])
            gradedResponse["rubric_assessment[" + element["id"] + "][comments]"] = str(response[elementOrder]["comments"])

        gradedResponse["submission[posted_grade]"] = str(round(totalPoints / float(rubricMaxPoints) * float(selectedAssignmentMaxScore), 2))

        requests.put(url, params=gradedResponse, headers=headers)

# Remove information stored in the rubrics for all students
def resetRubrics(course_id, assignment_id, studentIds, rubric):
    print("Resetting grades and comments in Canvas...")
    for id in studentIds:
        url = f"{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/" + str(id)

        gradedResponse = dict()
        
        for elementOrder, element in enumerate(rubric):
            gradedResponse["rubric_assessment[" + element["id"] + "][points]"] = ""
            gradedResponse["rubric_assessment[" + element["id"] + "][comments]"] = ""

        gradedResponse["submission[posted_grade]"] = ""

        requests.put(url, params=gradedResponse, headers=headers)


################################################################################################################################################
#############################################################    ISIM AUTOGRADER    ############################################################
################################################################################################################################################
resetCanvas = False

if __name__ == "__main__":
    # Fetch resources (COURSE_ID, ASSIGNMENT_ID, students, assignmentLinks, assignmentRubric)
    selectedCourseId, selectedAssignmentId, studentNames, studentIds, gradingIds, rubric, rubricMaxPoints, selectedAssignmentMaxScore = init()
    
    # Reset canvas assignement for everyone (testing)
    if resetCanvas:
        resetRubrics(selectedCourseId, selectedAssignmentId, studentIds, rubric)
    else:
        # Send query to Azure GPT-4o instance, and convert image data to grade json file
        responses = getGPTResponses(gradingIds, studentNames, studentIds, rubric)
        #Upload grades to Canvas
        uploadRubrics(responses, selectedCourseId, selectedAssignmentId, gradingIds, rubric, rubricMaxPoints, selectedAssignmentMaxScore)
        
    





