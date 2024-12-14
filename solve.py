import requests


def login(username, password):
    login_url = "https://lms.mob-edu.ru/lms-api/user-api/login"
    login_req = requests.post(login_url, json={"email" : username, "password" : password})
    if (login_req.status_code != 200):
        login_req = requests.post(login_url, json={"login" : username, "password" : password})


    if (login_req.status_code != 200):
        return (1, "login error\nMake sure that your login and password are correct")

    headers={"Authorization": "Bearer " + login_req.json()["jwt"]}
    return (0, headers)


def get_test(headers, test_id):
    base_url = "https://lms.mob-edu.ru/lms-api/schedule-api/v1/student/quizzes/" + test_id
    test = requests.get(base_url, headers=headers)
    if (test.status_code != 200):
        return (1, "get_test error\nMake sure that test id is correct")

    return (0, test)


def type_201(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)

    quest_list = var_list[0]["answers"]
    assert(len(quest_list) == 1)

    ans_options = quest_list[0]["answers_options"]

    answers = []
    for i in ans_options:
        if (i["is_correct"]):
            answers.append({"answerOptionId" : i["id"], "value" : i["id"]})

    response = {"answerResponses" : [{"answerId" : quest_list[0]["id"], "answerOptionResponses" : answers}], "answerAttachments" : []}
    return response



def type_203(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)

    quest_list = var_list[0]["answers"]

    answers = []
    for i in quest_list:
        ans_options = i["answers_options"]
        if (ans_options[0]["is_correct"]):
            answers.append({"answerId" : i["id"], "answerOptionResponses" : [{"answerOptionId" : ans_options[0]["id"], "value" : ans_options[0]["value"]["content"]["text"]}]})
        else:
            assert(0)

    response = {"answerResponses" : answers, "answerAttachments" : []}
    return response



def type_215(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)

    quest_list = var_list[0]["answers"]

    answers = []
    for i in quest_list:
        ans_options = i["answers_options"]
        ans_opt_cor = []
        for j in ans_options:
            if (j["is_correct"]):
                #ans_opt_cor.append({"answerOptionId" : ans_options[i]["id"], "value" : ans_options[0]["value"]["content"]["text"]})
                ans_opt_cor.append({"answerOptionId" : j["id"], "value" : j['id']})

        answers.append({"answerId" : i["id"], "answerOptionResponses" : ans_opt_cor})

    response = {"answerResponses" : answers, "answerAttachments" : []}
    return response



def type_204(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)
    quest_list = var_list[0]["answers"]
    answers = []
    for i in quest_list:
        if (len(i['answers_options']) == 1):
            if (i['answers_options'][0]['is_correct']):
                answers.append({"answerId" : i["id"], "answerOptionResponses" : [{"answerOptionId" : i["answers_options"][0]["id"], "value" : i["answers_options"][0]["value"]["content"]["text"], "number" : i["answers_options"][0]["number"]}]})
        else:
            assert(0)
    response = {"answerResponses" : answers, "answerAttachments" : []}
    return response



def type_206(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)

    quest_list = var_list[0]["answers"]
    assert(len(quest_list) == 1)

    ans_options = quest_list[0]["answers_options"]

    answers = []
    for i in ans_options:
        if ("matching_number" in i.keys()):
            answers.append({"answerOptionId" : i["id"], "matchingNumber" : i["matching_number"]})

    response = {"answerResponses" : [{"answerId" : quest_list[0]["id"], "answerOptionResponses" : answers}], "answerAttachments" : []}
    return response



def type_220(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)
    quest_lsit = var_list[0]["answers"]
    answers = []
    for i in quest_lsit:
        ans_options = []
        for j in i["answers_options"]:
            ans_options.append({"answerOptionId" : j["id"], "value" : j["id"]})
        answers.append({"answerId" : i["id"], "answerOptionResponses" : ans_options})
    response = {"answerResponses" : answers, "answerAttachments" : []}
    return response



def type_208(question):
    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)
    quest_list = var_list[0]["answers"]
    assert(len(quest_list) == 1)
    ans_options = quest_list[0]["answers_options"]
    answers = []
    for i in ans_options:
        answers.append({"answerOptionId" : i["id"], "number" : i["number"]})

    response = {"answerResponses" : [{"answerId" : quest_list[0]["id"], "answerOptionResponses" : answers}], "answerAttachments" : []}
    return response



def get_question_ans(question_id, headers):
    url = "https://lms.mob-edu.ru/cms-api/public-api/v1/questions/variant/" + question_id + "?includeAnswers=true"
    question = requests.get(url, headers=headers)

    var_list = question.json()["variant_list"]
    assert(len(var_list) == 1)
    question_type_id = var_list[0]["question_type_id"]


    if (question_type_id == 201 or question_type_id == 200):
        return type_201(question)
    elif (question_type_id == 203):
        return type_203(question)
    elif (question_type_id == 215):
        return type_215(question)
    elif (question_type_id == 204):
        return type_204(question)
    elif (question_type_id == 206):
        return type_206(question)
    elif (question_type_id == 220 or question_type_id == 238):
        return type_220(question)
    elif (question_type_id == 208):
        return type_208(question)
    else:
        return 0

def send_answer(test_id, var_id, question_id, answer, headers):
    url = "https://lms.mob-edu.ru/lms-api/schedule-api/v1/student/quizzes/" + test_id + "/questions/" + question_id + "/variants/" + var_id + "/answer"
    r = requests.put(url, headers=headers, json=answer)
    return r

def finish(headers, test_id):
    url = "https://lms.mob-edu.ru/lms-api/schedule-api/v1/student/quizzes/" + test_id + "/finish"
    requests.post(url, headers=headers)



def solve(username, password, test_id):
    r, headers = login(username, password)
    if (r):
        return (r, headers)

    r, test = get_test(headers, test_id)
    if (r):
        return (r, test)

    question_list = test.json()["content"]
    question_id_list = []
    question_id_list_2 = []
    for i in question_list:
        question_id_list.append(i["variantId"])
        question_id_list_2.append(i["questionId"])

    ok = True
    for i in range(len(question_id_list)):
        question_num = i
        answer = get_question_ans(question_id_list[question_num], headers)
        if (answer == 0):
            ok = False
            error = f"Undefined type of queston, test_id = {test_id}, question_id = {i}"
            break

        r = send_answer(test_id, question_id_list[question_num], question_id_list_2[question_num], answer, headers)

        if (r.status_code != 200):
            error = r.content
            ok = False

    if (ok):
        finish(headers, test_id)
        return (0, "")
    else:
        return (1, error)
