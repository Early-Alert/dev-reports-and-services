from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .utils import portal_token_request_api, get_file_from_cloud, get_employees_from_portal, send_details_email
import json
import requests
import logging
import os

@require_POST
@csrf_exempt
def teammate_delete(request):
    response = json.loads(request.body)
    filename = response["filename"]
    token = portal_token_request_api()
    webhook_employees_file = get_file_from_cloud(filename)

    if webhook_employees_file:
        list_of_file_employees = []
        with open(file=os.path.join("/tmp", filename)) as json_file:
            data = json.load(json_file)
            for each in data["features"]:
                list_of_file_employees.append(each["attributes"]["External_ID"])

        list_of_portal_employees = get_employees_from_portal(token)
        list_of_ex_employees = []
        if len(list_of_file_employees) != 0:
            yes_count, no_count = 0, 0
            for each_portal_employee in list_of_portal_employees:
                if each_portal_employee["attributes"]["code"] in list_of_file_employees:
                    yes_count += 1
                else:
                    list_of_ex_employees.append(each_portal_employee["attributes"]["code"])
                    no_count += 1
                    
        length_of_file_employees = len(list_of_file_employees)
        length_of_portal_employees = len(list_of_portal_employees) 
        length_of_ex_employees = len(list_of_ex_employees)

        send_details_email(length_of_file_employees, length_of_portal_employees, yes_count, no_count, length_of_ex_employees)
        emp_codes = {
            "code_list": list_of_ex_employees,
            "length_of_file_employees": length_of_file_employees,
            "length_of_portal_employees": length_of_portal_employees,
            "yes_count": yes_count,
            "no_count": no_count,
            "length_of_ex_employees": length_of_ex_employees

        } 
        return JsonResponse(emp_codes, content_type="application/json")


@require_POST
@csrf_exempt
def send_confirmation_email(request):
    response = json.loads(request.body)
    recipient_list = response["recipient_list"]
    subject = response["subject"]
    body = response["body"]
    bcc = response["bcc"]
    from_email = response["from_email"]
    email_response = requests.post("https://api.mailgun.net/v3/earlyalert.com/messages",
    auth=("api", "key-abc3ac7030c2113b91c27b6733ebe510"),
        data={"from": from_email,
            "to": recipient_list,
            "bcc" : bcc,
            "subject": subject,
            "text": body,
            })
    logging.info("********** Email Sent **********")
    return HttpResponse(email_response.text)
