
from azure.storage.blob import BlobServiceClient
import requests
import os
import logging 

GIS_USERNAME = "Developer1"
GIS_PASSWORD = "qweRTY77**"

def portal_token_request_api():
    url = "https://maps.earlyalert.com/portal/sharing/rest/generateToken"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "username": GIS_USERNAME,
        "password": GIS_PASSWORD,
        "client": "referer",
        "referer": "https://maps.earlyalert.com/portal",
        "expiration": 20,
        "f": "json"
    }
    response = requests.post(url, headers=headers, data=params)
    token = response.json()["token"]
    return token

def get_file_from_cloud(filename):
    blob_service_client = BlobServiceClient(account_url="https://eapytoolsstorage.blob.core.windows.net/", credential= "lOj9oe2csu0p7Mxky7rdZOMlTLYqLA0pRPZNSU+4Ux93Ph1ui76kyDngxrNS1qv3FhT1t+MTP3oFwnJ8PMV7Xw==")
    blob_client = blob_service_client.get_blob_client(container="static/teammate_files", blob=filename)
    with open(file=os.path.join('/tmp', filename), mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())
        return True

def get_employees_from_portal(token):
    # url = "https://maps.earlyalert.com/server/rest/services/Hosted/Truist_Confirmed_Tornado/FeatureServer/0/query?where=ClientId%3D430&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&gdbVersion=&historicMoment=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=true&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&multipatchOption=xyFootprint&resultOffset=&resultRecordCount=&returnTrueCurves=false&returnCentroid=false&sqlFormat=none&resultType=&datumTransformation=&f=pjson"
    url = "https://maps.earlyalert.com/server/rest/services/Hosted/Truist_Confirmed_Tornado/FeatureServer/0/query?where=ClientId%3D430&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=clientid%2C+objectid%2C+name%2C+code&returnGeometry=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&gdbVersion=&historicMoment=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&multipatchOption=xyFootprint&resultOffset=&resultRecordCount=&returnTrueCurves=false&returnCentroid=false&sqlFormat=none&resultType=&datumTransformation=&f=pjson"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "f": "json",
        "token": token
    }
    query_params = {
        "f": "json",
        "clientid": 430,
        "token": token
    }
    response = requests.get(url, headers=headers, params=query_params).json()
    return response["features"]

def send_details_email(len_of_list_of_file_employees, len_of_list_of_portal_employees, matched_employees, unmatched_employees, len_of_list_of_ex_employees):
    send_email = requests.post("https://api.mailgun.net/v3/earlyalert.com/messages",
    auth=("api", "key-abc3ac7030c2113b91c27b6733ebe510"),
        data={"from": "ykhan@earlyalert.com",
            "to": "yasir.khan@cooperativecomputing.com",
            "bcc" : [],
            "subject": "Teammate Deletion Analytics",
            "text": f"Number Of records from File --> {len_of_list_of_file_employees} \nNumber Of records from Portal --> {len_of_list_of_portal_employees} \nRecords Matched --> {matched_employees} \nRecords Not Matched --> {unmatched_employees} \nCount Of Un-Matched Records --> {len_of_list_of_ex_employees}",
            })
    logging.info("********** Email Sent **********")
    return send_email