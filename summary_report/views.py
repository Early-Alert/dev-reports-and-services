from django.shortcuts import render
import datetime
import pytz
from .utils import generate_esri_token, cf_subtypes, one_day_hazard_data, two_days_with_time_range, send_email

def cfa_one_day_report(request):
    now = datetime.datetime.now()
    date = '{}'.format(now.strftime('%A, %b %d'))
    token = generate_esri_token()
    reports = []
    respone_subtypes = cf_subtypes(token)

    tz = pytz.timezone('EST')
    current_eastern_time = datetime.datetime.now(tz)

    for type in respone_subtypes:
        data = one_day_hazard_data(token, type, current_eastern_time)
        reports.append(data)
        subject = "One Day Report"

    context = {'data': reports, 'issue_date': date}
    send_email(context, f"4.0 Chick Fillet Summary {current_eastern_time} ||| {subject}", ["ykhan@earlyalert.com", "daldret@earlyalert.com"])

    return render(request, "summary_report.html", context)

def cfa_two_day_report(request):
    now = datetime.datetime.now()
    date = '{}'.format(now.strftime('%A, %b %d'))
    token = generate_esri_token()
    reports = []
    respone_subtypes = cf_subtypes(token)

    tz = pytz.timezone('EST')
    current_eastern_time = datetime.datetime.now(tz)

    for type in respone_subtypes:
        data = two_days_with_time_range(token, type, current_eastern_time)
        reports.append(data)
        subject = "One Day Report"

    context = {'data': reports, 'issue_date': date}
    # print("-----------------")
    # print(context["data"])
    send_email(context, f"3.0 Chick Fillet Summary {current_eastern_time} ||| {subject}", ["ykhan@earlyalert.com", "daldret@earlyalert.com"])

    return render(request, "summary_report.html", context)
