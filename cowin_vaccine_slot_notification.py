import requests
import json
import pandas as pd
import datetime
import time
from datetime import timedelta
import smtplib
from email.message import EmailMessage
from math import sin, cos, sqrt, atan2, radians
import sys
import subprocess
import winsound


# sound setting
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 10000  # Set Duration To 1000 ms == 1 second

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import pgeocode
except ModuleNotFoundError:
    print("Installing package")
    packagesToInstallList = ["pgeocode"]
    for package in packagesToInstallList:
        install(package)


#####################################################################################################
# Input Parameters

dist = pgeocode.GeoDistance('IN')

EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ''
TO_EMAIL_ADDRESS = [EMAIL_ADDRESS]

vaccine_type = "Free" # Paid or Free
vaccine_dose = "available_capacity_dose1"
list_of_district = [141,145,140,146,147,143,148,149,144,150,142,651,652]
unwanted_pincodes = [245304,232329,110010]

current_pin = "110092"

# End of Input Parameters
###################################################################################################

print("Developer: Himanshu Malhotra")

today_date = (datetime.datetime.utcnow()+timedelta(minutes = 330)).date().strftime("%d-%m-%Y")
print("Checking from the date ->",today_date)


def sendEmailFx(html_code):
    print("Sending Email")


    msg = EmailMessage()
    msg['Subject'] = 'Vaccine Slot Available - By HM'
    msg['From'] = EMAIL_ADDRESS 
    msg['To'] = TO_EMAIL_ADDRESS
    msg.set_content(html_code, subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    # creating a sound
    winsound.Beep(frequency, duration)
def fetchVaccineSlot(list_of_district,dose_type,vaccine_type):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district}&date={today_date}"

    final_vaccine_list = []

    for district in list_of_district:
        print("Running for District ->",district)
        final_url = url.format(district = district,today_date = today_date)
        resp = requests.get(final_url).json()
        temp_district_list = []
        for center in resp["centers"]:
            temp_center_list = []

            if(center["fee_type"]!= vaccine_type):
                continue

            flag_18 = False
            flag_dose_available = False

            for session in center["sessions"]:
                if((session["min_age_limit"]==18)):
                    flag_18 = True
                if(session[dose_type]>0):
                    flag_dose_available = True

            if((flag_18 == True) & (flag_dose_available == True)):
                for session in center["sessions"]:
                    temp_dict = {}
                    if((session["min_age_limit"]!=18)):
                        continue
                    if(center["pincode"] in unwanted_pincodes):
                        continue
                    if(session["available_capacity_dose1"]<=1):
                        continue
                    temp_dict["district_id"] = district
                    temp_dict["center_id"] = center["center_id"]
                    temp_dict["fee_type"] = center["fee_type"]
                    temp_dict["name"] = center["name"]
                    temp_dict["address"] = center["address"]
                    temp_dict["distance"] = dist.query_postal_code(current_pin, center["pincode"])
                    temp_dict["state_name"] = center["state_name"]
                    temp_dict["district_name"] = center["district_name"]
                    temp_dict["pincode"] = center["pincode"]
                    temp_dict["from"] = center["from"]
                    temp_dict["to"] = center["to"]
                    temp_dict["date"] = session["date"]
                    temp_dict["available_capacity"] = session["available_capacity"]
                    temp_dict["vaccine"] = session["vaccine"]
                    temp_dict["slots"] = session["slots"]
                    temp_dict["available_capacity_dose1"] = session["available_capacity_dose1"]
                    temp_dict["available_capacity_dose2"] = session["available_capacity_dose2"]

                    if(len(temp_dict)==0):
                        continue
                    else:
                        temp_district_list.append(temp_dict)
            if(len(temp_district_list)==0):
                continue
            else:
                for temp_district_value in temp_district_list:
                    temp_center_list.append(temp_district_value)
        if(len(temp_center_list)==0):
            continue
        else:
            for temp_center_value in temp_center_list:
                final_vaccine_list.append(temp_center_value)

    if(len(final_vaccine_list)==0):
        print("No Slot Available")
        return(True)
    else:
        pdf = pd.DataFrame(final_vaccine_list).sort_values(by = ["distance",dose_type],ascending = [True,False])
        sendEmailFx(pdf.to_html(index=False,justify = "center"))
        return(False)




print("Checking for {vaccine_type} - {vaccine_dose}".format(vaccine_type = vaccine_type,vaccine_dose =vaccine_dose))


print("Total Count of Districts -> ",len(list_of_district))

counter = 1
while(1):
    print("\n\nIteration Number ->",counter)
    counter += 1
    flag = fetchVaccineSlot(list_of_district,vaccine_dose,vaccine_type)
    if(flag == False):
        if(counter >=1000):
            break
        time.sleep(60)
        continue
    else:
        time.sleep(10)
        continue


print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
print("------------END of the Code----------------")
print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
