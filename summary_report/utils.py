import requests
import json
from datetime import datetime, timedelta
import pytz
from django.template.loader import get_template


GIS_USERNAME = "Developer1"
GIS_PASSWORD = "qweRTY77**"

def generate_esri_token():
    url = "https://maps.earlyalert.com/portal/sharing/rest/generateToken"
    params = {
        "f": "json",
        "username": 'Developer1',
        "password": GIS_PASSWORD,
        "client": "referer",
        "referer": "https://maps.earlyalert.com/portal"
    }
    r = requests.post(url, data=params)
    token = r.json()["token"]
    # cache.set("esri_token", token, timeout=55 * 60)
    return token

def cf_subtypes(token):
    subtypes = []
    # date = '{}%'.format(datetime.now().strftime('%Y-%m-%d'))
    date = '2022-04-30%'
    url = 'https://maps.earlyalert.com/server/rest/services/Hosted/EarlyAlert_Reports/FeatureServer/2/query?'
    params = {
        'where': "cid=209 and CAST(created_date as varchar(13)) like '{}' and sub_type NOT IN ('SALT', 'SHR')".format(date),
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'relationParam': '',
        'outFields': 'sub_type',
        'returnGeometry': 'false',
        'geometryPrecision': '',
        'outSR': '',
        'returnIdsOnly': 'false',
        'returnCountOnly': 'false',
        'orderByFields': '',
        'groupByFieldsForStatistics': '',
        'returnZ': 'false',
        'returnM': 'false',
        'returnDistinctValues': 'true',
        'f': 'pjson',
        'token': token
    }
    r = requests.get(url, params=params)
    output_data = r.json()
    for i in output_data.get('features'):
        subtypes.append(i.get('attributes').get('sub_type'))
    return subtypes

def one_day_hazard_data(token, category_type, date):
    # date = "2023-04-01"
    formatted_date = date.date()
    # formatted_date = "2023-04-27"
    data = []
    query = "'{}'".format(category_type)
    where = "cid = 209 and CAST(created_date as varchar(13)) like '{}%' and sub_type = {}".format(formatted_date, query)
    # where = "cid = 209 and CAST(created_date as varchar(13)) like '2023-04-17%' and sub_type = 'SEVERE THUNDERSTORM WARNING'"
    print(where)
    url = 'https://maps.earlyalert.com/server/rest/services/Hosted/EarlyAlert_Reports/FeatureServer/2/query?'
    params = {
        'where': "{}".format(where),
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'relationParam': '',
        'outFields': '*',
        'returnGeometry': 'false',
        'geometryPrecision': '',
        'outSR': '',
        'returnIdsOnly': 'false',
        'returnCountOnly': 'false',
        'orderByFields': '',
        'groupByFieldsForStatistics': '',
        'returnZ': 'false',
        'returnM': 'false',
        'returnDistinctValues': 'false',
        'f': 'pjson',
        'token': token
    }
    r = requests.get(url, params=params)
    output_data = r.json()
    length = len(output_data.get('features'))

    start_datetime = f"{formatted_date} 09:30:00"
    end_datetime = f"{formatted_date} 14:30:00"
    
    start_time_object = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
    end_time_object = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
    tz = pytz.timezone('America/New_York')
    for i in range(length):

        locations_affected = []
        sent_to = []
        attributes = output_data.get('features')[i].get('attributes')
        ranged_data = datetime.fromtimestamp(attributes["created_date"]/1000)
        
        """
        unix_timestamp = attributes["created_date"] / 1000  # Convert to Unix timestamp
        ssdt_object = datetime.fromtimestamp(unix_timestamp)
        dt = datetime.fromtimestamp(unix_timestamp, tz)
        """
        
        unix_timestamp = attributes['created_date']/1000
        utc_datetime = datetime.utcfromtimestamp(unix_timestamp)
        # create a timezone object for PKT
        pkt_timezone = pytz.timezone('Asia/Karachi')
        # convert the UTC datetime to PKT datetime
        pkt_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(pkt_timezone) 
        datetime_object_str = datetime.strftime(pkt_datetime, "%Y-%m-%d %H:%M:%S")
        datetime_object = datetime.strptime(datetime_object_str, '%Y-%m-%d %H:%M:%S')
        
        # print(f"NAME --> {attributes.get('title')}")
        # print(f"DATE --> {attributes['created_date']}")
        # print(f"INTERNAL-DATETIME --> {datetime_object}")
        # print("-----")


        # print("Converted Time is --> ", ranged_data)
        # if ranged_data >= start_time_object and ranged_data <= end_time_object:
        if datetime_object >= start_time_object and datetime_object <= end_time_object:
            # print("********** Condition Satisfied **********")
            # print(f"DATE --> {attributes['created_date']}")
            # print(f"INTERNAL-DATETIME --> {datetime_object}")

        # if ranged_data.hour >= 10 and ranged_data.hour < 16:
            if attributes['locations_affected'] != None:
                created_date = attributes.get('created_date')
                # print("created_date ", created_date)
                timestamp = created_date/1000.0
                dt_object = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y, %I:%M %p')
                # print("dt_object  ", dt_object)

                # dd = convert_date(created_date)
                # print("dd ", dd)

                data_locations_affected = json.loads(attributes.get('locations_affected'))
                for j in data_locations_affected:
                    locations_affected.append(j.get('attributes'))
                data_sent_to = json.loads(attributes.get('sent_to'))
                # print("data_sent_to -- ", data_sent_to)
                for k in data_sent_to:
                    sent_to.append(k)
                    # if type(k) == str:
                    # else:
                    #     sent_to.append(k.get('email'))

                context = {
                    'title': attributes.get('title'),
                    'location': attributes.get('location'),
                    'created_at': datetime_object,
                    'sent_to': sent_to,
                    'locations_affected' : locations_affected
                }
                data.append(context)
        else:
            pass
            # print("-------------------- Un Matched Record ", ranged_data)
    report = {
        'type': category_type,
        'data': data
    }
    # print(report)
    return report

def two_days_with_time_range(token, sub_type, date):
    day_earlier = (date- timedelta(days=1)).date()
    # print(date.date())
    # print(day_earlier)
    list_of_two_dates = [[date.date(), "today"], [day_earlier, "yesterday"]]
    # list_of_two_dates = [["2023-04-01", "today"], ["2023-03-31", "yesterday"]]

    # date = "2023-04-04%"
    data = []
    for each_date in list_of_two_dates:
        query = "'{}'".format(sub_type)
        where = "cid = 209 and CAST(created_date as varchar(13)) like '{}%' and sub_type = {}".format(each_date[0], query)
        print(where)
        url = 'https://maps.earlyalert.com/server/rest/services/Hosted/EarlyAlert_Reports/FeatureServer/2/query?'
        params = {
            'where': "{}".format(where),
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'relationParam': '',
            'outFields': '*',
            'returnGeometry': 'false',
            'geometryPrecision': '',
            'outSR': '',
            'returnIdsOnly': 'false',
            'returnCountOnly': 'false',
            'orderByFields': '',
            'groupByFieldsForStatistics': '',
            'returnZ': 'false',
            'returnM': 'false',
            'returnDistinctValues': 'false',
            'f': 'pjson',
            'token': token
        }
        r = requests.get(url, params=params)
        output_data = r.json()
        # print("Output --> ", output_data)
        length = len(output_data.get('features'))
        for i in range(length):
            locations_affected = []
            sent_to = []
            attributes = output_data.get('features')[i].get('attributes')
            ranged_data = datetime.fromtimestamp(attributes["created_date"]/1000).strftime('%Y-%m-%d %H:%M:%S')
            ranged_data = datetime.strptime(ranged_data, '%Y-%m-%d %H:%M:%S')
            eval_date = attributes['created_date']/1000
            response_date = datetime.fromtimestamp(eval_date)
            print(f"{response_date}  ----------  {attributes['created_date']} RD --> ", ranged_data )
            
            # timestamp = attributes['created_date']
            # unix_timestamp = timestamp / 1000
            # tz = pytz.timezone('US/Eastern')  # or whatever time zone you need
            # dt_object_str = datetime.fromtimestamp(unix_timestamp, tz)
            # print(f"----------  {dt_object_str} ")

            # if ranged_data >

            unix_timestamp = attributes['created_date']/1000
            utc_datetime = datetime.utcfromtimestamp(unix_timestamp)
            # create a timezone object for PKT
            pkt_timezone = pytz.timezone('Asia/Karachi')
            # convert the UTC datetime to PKT datetime
            pkt_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(pkt_timezone) 
            datetime_object_str = datetime.strftime(pkt_datetime, "%Y-%m-%d %H:%M:%S")
            datetime_object = datetime.strptime(datetime_object_str, '%Y-%m-%d %H:%M:%S')


            if each_date[1] == "today":
                # print("If Condition Satisfied ", ranged_data)
                start_time_string = f"{each_date[0]} 00:00:00"
                end_time_string = f"{each_date[0]} 09:30:00"
                start_time_object = datetime.strptime(start_time_string, '%Y-%m-%d %H:%M:%S')
                end_time_object = datetime.strptime(end_time_string, '%Y-%m-%d %H:%M:%S')
                # print(f"Objects \n{start_time_object} -- {end_time_object}")
                # print(f"Objects \n{type(start_time_object)} -- {type(end_time_object)}")
                
                # if (ranged_data > start_time_object and ranged_data < end_time_object) and ranged_data.day == each_date[0].day:
                # if (ranged_data >= start_time_object and ranged_data <= end_time_object):


                # if (ranged_data >= start_time_object and ranged_data <= end_time_object):
                if datetime_object >= start_time_object and datetime_object <= end_time_object:
                
                
                    # print("------------------------------ If condition satisfied")
                    if attributes['locations_affected'] != None:
                        # print("Locations Affected not None")
                        created_date = attributes.get('created_date')
                        # print("created_date ", created_date)
                        timestamp = created_date/1000.0
                        dt_object = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y, %I:%M %p')
                        # print("dt_object  ", dt_object)

                        data_locations_affected = json.loads(attributes.get('locations_affected'))
                        for j in data_locations_affected:
                            locations_affected.append(j.get('attributes'))
                        data_sent_to = json.loads(attributes.get('sent_to'))
                        for k in data_sent_to:
                            sent_to.append(k)
                        attributes_time = output_data.get('features')[i].get('attributes')
                        timestamp = attributes_time["created_date"]
                        unix_timestamp = timestamp / 1000  # Convert to Unix timestamp
                        dt_object_updated = datetime.fromtimestamp(unix_timestamp)
                        context = {
                            'title': attributes.get('title'),
                            'location': attributes.get('location'),
                            'created_at': datetime_object,
                            'sent_to': sent_to,
                            'locations_affected' : locations_affected
                        }
                        attributes = output_data.get('features')[i].get('attributes')
                        print(f"**************** Timestamp added -- {dt_object} -- {attributes_time['created_date']}")

                        data.append(context)

            elif each_date[1] == "yesterday":
                print("Elif Condition Satisfied ", ranged_data)
                start_time_string = f"{each_date[0]} 14:30:00"
                end_time_string = f"{each_date[0]} 23:59:59"
                start_time_object = datetime.strptime(start_time_string, '%Y-%m-%d %H:%M:%S')
                end_time_object = datetime.strptime(end_time_string, '%Y-%m-%d %H:%M:%S')
                
                # if (ranged_data >= start_time_object and ranged_data <= end_time_object):
                if datetime_object >= start_time_object and datetime_object <= end_time_object:
                
                    if attributes['locations_affected'] != None:
                        # print("Locations Affected not None")
                        created_date = attributes.get('created_date')
                        # print("created_date ", created_date)
                        timestamp = created_date/1000.0
                        dt_object = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y, %I:%M %p')
                        # print("dt_object  ", dt_object)

                        data_locations_affected = json.loads(attributes.get('locations_affected'))
                        for j in data_locations_affected:
                            locations_affected.append(j.get('attributes'))
                        data_sent_to = json.loads(attributes.get('sent_to'))
                        for k in data_sent_to:
                            sent_to.append(k)
                        
                        attributes_time = output_data.get('features')[i].get('attributes')
                        timestamp = attributes_time["created_date"]
                        unix_timestamp = timestamp / 1000  # Convert to Unix timestamp
                        dt_object_updated = datetime.fromtimestamp(int(unix_timestamp))
                        
                        print(f"------------------- Time i got {timestamp} and converted {dt_object_updated}")
                        context = {
                            'title': attributes.get('title'),
                            'location': attributes.get('location'),
                            'created_at': datetime_object,
                            'sent_to': sent_to,
                            'locations_affected' : locations_affected
                        }
                        print(f"**************** Timestamp added -- {dt_object} -- {attributes_time['created_date']}")
                        data.append(context)
    report = {
        'type':sub_type,
        'data': data
        }
    return report


def send_email(context, subject, to_list):
        """Sends daily email with spreadsheet to clients."""

        api_key = 'key-abc3ac7030c2113b91c27b6733ebe510'
        api_url = 'https://api.mailgun.net/v3/earlyalert.com/messages'

        # Define the email message
        from_email = 'reports@earlyalert.com'

        # to_email = ['ykhan@earlyalert.com']
        to_email = to_list
        subject = subject
        html_content = get_template('summary_report.html').render(context)
        message = {
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'html': html_content
        }

        # Send the email using Mailgun API
        response = requests.post(
            api_url,
            auth=('api', api_key),
            data=message
        )
        # Check if the email was sent successfully
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False


