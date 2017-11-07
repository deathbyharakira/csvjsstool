#################################################
# CSV JSS Tool
# Copyright (c) 2017 Kira Albers
# All rights reserved.
#
# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation,
# advertising materials, and other materials related to such
# distribution and use acknowledge that the software was developed
# by the creator.
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##################################################

import sys
import csv
import requests

# Set your JSS server
JSS_SERVER = "https://myjsswebsite.com:8443"
# Set your JSS API Username and Password.  IMPORTANT: Make sure the user has the appropriate permissions
JSS_USERNAME = "username"
JSS_PASSWORD = "password"

# Change next line to True to allow insecure SSL connections to the server
INSECURE_MODE = False
# Uncomment next line to disable warnings about using an insecure connection
#requests.packages.urllib3.disable_warnings()


##########################################################################
# Edit below this line at your own risk
##########################################################################



# xmldata should be the xml string that you are sending to the JSS
# resource_category is the string for the resource you want to access such as mobiledevices, computers, or users
# resource_field is the lookup on the resource such as serial, name, id, or udid
# entity should be the objector for the lookup: device's serial number, username, device udid string, etc
def updateRecord(xmldata, resource_category, resource_field, entity):
    if(resource_field != ""):
        resource_field = "/"+resource_field+"/"
    try:
        if(INSECURE_MODE):
            response = requests.put(JSS_SERVER + "/JSSResource/" + resource_category + resource_field + entity,auth=(JSS_USERNAME, JSS_PASSWORD), verify=False, data=xmldata)
        else:
            response = requests.put(JSS_SERVER + "/JSSResource/" + resource_category + resource_field + entity,auth=(JSS_USERNAME, JSS_PASSWORD), data=xmldata)
        if(response.status_code != 200 and response.status_code != 201):
            print("\tFailed to update " + resource_category + resource_field + entity + ". Server response code: " + str(response.status_code))
    except requests.exceptions.HTTPError as error:
        print("\tError for "+resource_category+"/"+resource_field+"/"+entity+": "+error)

def createRecord(xmldata, resource_category, resource_field, entity):
    if(resource_field != ""):
        resource_field = "/"+resource_field+"/"
    try:
        if(INSECURE_MODE):
            response = requests.post(JSS_SERVER + "/JSSResource/" + resource_category + resource_field + entity,auth=(JSS_USERNAME, JSS_PASSWORD), verify=False, data=xmldata)
        else:
            response = requests.post(JSS_SERVER + "/JSSResource/" + resource_category + resource_field + entity,auth=(JSS_USERNAME, JSS_PASSWORD), data=xmldata)
        if(response.status_code != 200 and response.status_code != 201):
            print("\tFailed to update " + resource_category + resource_field + entity + ". Server response code: " + str(response.status_code))
    except requests.exceptions.HTTPError as error:
        print("\tError for "+resource_category+"/"+resource_field+"/"+entity+": "+error)

# Updates the full name and roster name fields of a user
def updateNameOfUser(username,firstname,lastname):
    fullname = lastname + ", " + firstname
    rostername = firstname + " " + lastname
    xmldata = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><user><full_name>"+fullname+"</full_name><roster_managed_apple_id/><roster_name>"+rostername+"</roster_name><roster_source/><roster_source_system_identifier/><roster_unique_identifier/></user>"
    updateRecord(xmldata,"users","name",username)

def createStaticUserGroup(groupname,userlist):
    userlist = validateList(userlist,"users","name")
    print("\nAssembling xml...")

    xmldata = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
    "<user_group><name>"+groupname+"</name>" \
    "<is_smart>false</is_smart><is_notify_on_change>false</is_notify_on_change>" \
    "<site><id>0</id><name></name></site>" \
    "<criteria><size>0</size></criteria>" \
    "\n<users>"
    for username in userlist:
        xmldata += "\n<user><username>"+username+"</username></user>"
    xmldata += "\n</users></user_group>"

    print("Contacting JSS and creating static user group...")
    print("Be patient, this will take a while if the list is big.")
    createRecord(xmldata,"usergroups","name",groupname)

# Validates a list of users or devices.
# Useful if your JSS is divided into sites and
# you don't have access to certain users or something.
#
# Performs validation by checking if you can GET request the object successfully.
def validateList(resourcelist,resource_category,resource_field):
    print("\nPlease wait, validating supplied list...")
    validlist = []
    for item in resourcelist:
        response = requests.get(JSS_SERVER + "/JSSResource/"+resource_category+"/"+resource_field+"/"+item ,headers={'Accept': 'application/json'},auth=(JSS_USERNAME, JSS_PASSWORD), verify=False)
        if(response.status_code == 200 or response.status_code == 201):
            validlist.append(username)
        else:
            print("\tIgnoring invalid list item: "+item)
    return validlist

# Asset tag xml
# "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device><general><asset_tag>%s</asset_tag></general></mobile_device>" % assettag

# Device user xml
# "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device><location><username>%s</username></location></mobile_device>" % user

with open(sys.argv[1]) as csvfile:
    userlist = []
    filereader = csv.reader(csvfile)
    for row in filereader:
        userlist.append(row[3])
    createUserGroup("0232 - Q1 Privileged Students",userlist)
