from datetime import datetime
import os
import base64
import requests
import urllib3
import re
import json
import pexpect
import subprocess
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import lsfunctions as lsf

debug = True
retryCount = 1

#####################################################
# 2501 - Get Encoded Token from LCM
#####################################################

def getEncodedToken(username, password):
    if debug:
        print(f'Function: getEncodedToken')
        print(f"Username: {username}")
        print(f"Password: {password}")
    
    credentials = f'{username}:{password}'
    bytesCredentials = credentials.encode('utf-8')
    base64BytesCredentials = base64.b64encode(bytesCredentials)
    base64Creds = base64BytesCredentials.decode('utf-8')

    if debug:
        print(f'Token: {base64Creds}')

    return base64Creds

#####################################################
# 2501 - Get LCM Request Status
#####################################################

def getRequestStatus(inFqdn, token, verify, requestId):
    
    if debug:
        print(f"Function: getRequestStatus")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"Request Id: {requestId}")

    url = f'https://{inFqdn}/lcm/request/api/v2/requests/{str(requestId)}'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + token,
        'Accept': 'application/json'
    }

    payload = {}

    try:

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()
        jResponse = response.json()

        if not (response.status_code < 200 or response.status_code >= 300):
            return jResponse['state']
        else:
            print(f'2501: Response Code: {str(response.status_code)}')
            if debug:
                print(jResponse)
            return 'FAILED'

    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

#####################################################
# 2501 - GET environment Id
#####################################################

def getEnvironmentVmidByName(inFqdn, token, verify, envName):

    if debug:    
        print(f"Function: getEnvironmentVmidByName")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"Environment: {envName}")

    try:
        url = f'https://{inFqdn}/lcm/lcops/api/v2/environments'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status
        jResponse = response.json()
        
        if not (response.status_code < 200 or response.status_code >= 300):
            for environment in jResponse:
                if environment['environmentName'] == envName:
                    return environment['environmentId']
        else:
            print(f'2501: {str(response.status_code)}')
            if debug:
                print(jResponse)
            return response.status_code
    
    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

#####################################################
# 2501 -  Power Event in LCM
#####################################################

def powerStateProductByEnvironmentId(inFqdn, token, verify, environmentId, productId, powerState):
    
    if debug:    
        print(f"Function: powerStateProductByEnvironmentId")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"EnvironmentId: {environmentId}")
        print(f"ProductId: {productId}")
        print(f"Power State: {powerState}")

    try:
        
        url = f'https://{inFqdn}/lcm/lcops/api/v2/environments/{environmentId}/products/{productId}/{powerState}'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}
        
        session = requests.Session()
        session.trust_env = False
    
        response = session.post(url=url, data=payload, headers=headers, verify=verify )       
        response.raise_for_status()
        jResponse = response.json()

        if response.status_code < 200 or response.status_code >= 300:
            print(f'2501: Response Code: {str(response.status_code)}')
            if debug:
                print(jResponse)

            return response.status_code
        else:
            return jResponse['requestId']

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            jResponse = response.json()
            if jResponse['errorCode'] == "LCM_ENVIRONMENT_API_ERROR0014":
                return 0
        else:
            print(f'2501: HTTP -  {e}')
            lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)

    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

#####################################################
# 2501 -  Trigger for LCM Power Event
#####################################################

def triggerPowerEvent(inFqdn, token, verify, environments, productIds, powerState):

    if debug:    
        print(f"Function: triggerPowerEvent")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"Environments: {environments}")
        print(f"ProductIds: {productIds}")
        print(f"Power State: {powerState}")
    try:
        for environment in environments:
            print(f'2501: Checking {inFqdn} for {environment} environment.')
            lsf.write_output(f'2501: Checking {inFqdn} for {environment} environment.', logfile=lsf.logfile)
            envId = getEnvironmentVmidByName(inFqdn, token, verify, environment)
            lsf.write_output(f'2501: Environment {environment} has an ID of {envId}.', logfile=lsf.logfile)
            print(f'2501: Environment {environment} has an ID of {envId}')
            if (envId):
                for productId in productIds:
                    requestId = powerStateProductByEnvironmentId(inFqdn, token, verify, envId, productId, powerState)
                    if isGuid(requestId):
                        lsf.write_output(f'2501: Triggering Power Event for {productId} - {powerState}', logfile=lsf.logfile)
                        print(f'2501: Triggering Power Event for {productId} - {powerState}')
                        lsf.write_output(f'2501: Power Event Request ID is {requestId}', logfile=lsf.logfile)
                        print(f'2501: Power Event Request ID is {requestId}')
                        return requestId
                    continue
            else:
                print(f'ERROR: Environment {environment} does not exist.')

    except Exception as e:
        lsf.write_output(f'exception: {e}')
        print(f'2501: {e}')

#####################################################
# 2501 -  Get Request Id from Active Requests 
#####################################################

def getRequestIdFromActiveRequests(inFqdn, token, verify, environmentId, productId, state):
 
    if debug:
        print(f"Function: getRequestIdFromActiveRequests")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"EnvironmentId: {environmentId}")
        print(f"ProductId: {productId}")
        print(f"State: {state}")
        

    try:
        url = f"https://{inFqdn}/lcm/request/api/v2/requests"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()  
        allRequests = response.json()

        filteredRequests = []
        if not (response.status_code < 200 or response.status_code >= 300):

            for request in allRequests:
                if request['requestType'] == "PRODUCT_POWER_ON" and request['inputMap']['environmentId'] == environmentId and request['inputMap']['productId'] == productId and request['state'] == state: 
                    jt = {
                            "id": request['vmid'],
                            "lastUpdated" : datetime.fromtimestamp(request['lastUpdatedOn']/1000)
                        }


                    filteredRequests.append(jt)
                
            if len(filteredRequests) > 0:
                return sorted(filteredRequests, key=lambda x: x['lastUpdated'], reverse=True)[0]['id']
        else:           
            return None

    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)



#####################################################
# 2501 -  Check Request Status 
#####################################################

def checkRequestStatus(inFqdn, token, verify, requestId):
    
    global retryCount

    if debug:
        print(f"Function: checkRequestStatus")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"RequestId: {requestId}")

    try:

        requestStatus = getRequestStatus(inFqdn, token, verify, requestId)
        requestName = getRequestNameById(inFqdn, token, verify, requestId)
        
        while not requestStatus == "COMPLETED":

            requestStatus = getRequestStatus(inFqdn, token, verify, requestId)
            
            lsf.write_output(f'2501: {requestName}, Request Status: {requestStatus}')
            print(f'2501: {requestName}, Request Status: {requestStatus}') 

            if requestStatus == "INPROGRESS":
                lsf.labstartup_sleep(60)     
                continue
            
            elif requestStatus == "FAILED":
                print(f'2501: Retry Count: {retryCount}')
                lsf.write_output(f'2501: Retry Count: {retryCount}', logfile=lsf.logfile)
                
                lcmErrorId = getErrorIdByRequestId(inFqdn, token, verify, requestId)

                print(f'2501: Error Id: {lcmErrorId}') 
                lsf.write_output(f'2501: Error Id: {lcmErrorId}', logfile=lsf.logfile)
                
                if (lcmErrorId == "LCMVRAVACONFIG590070"):

                    print(f'2501: Retrying Request {requestName}')
                    lsf.write_output(f'2501: Retry Count: {retryCount}', logfile=lsf.logfile)
                    lsf.write_output(f'2501: Retrying Request {requestName}', logfile=lsf.logfile)
                    
                    errorCause = getErrorCauseByRequestId(inFqdn, token, verify, requestId)
                    if debug:
                        lsf.write_output(f'2501: Retry Count: {retryCount}', logfile=lsf.logfile)
                        lsf.write_output(f'2501: Error Cause: {errorCause}', logfile=lsf.logfile)
                    
                    while retryCount > 0:
                        retry = retryRequest(inFqdn, token, verify, requestId, errorCause)
                        if retry:
                            retryCount = retryCount - 1
                        continue


                if (lcmErrorId == "LCMVIDM74068"):
                    print(f'2501: IDM Root Password has Expired') 
                    lsf.write_output(f'2501: IDM Root Password has Expired')
                    
                lsf.labstartup_sleep(30) 

    except Exception as e:
        print(f'2501: Error - {e}')
        lsf.write_output(f'2501: Error - {e}', logfile=lsf.logfile)
    
    finally:

        retryCount = 1

#####################################################
# 2501 -  Get Request Name 
#####################################################

def getRequestNameById(inFqdn, token, verify, requestId):

    if debug:    
        print(f"Function: getRequestNameById")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"RequestId: {requestId}")

    try:

        if debug:
            print(f"In: getRequestStatus")

        url = f"https://{inFqdn}/lcm/request/api/v2/requests/{str(requestId)}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()   
        jResponse = response.json()

        if not (response.status_code < 200 or response.status_code >= 300):
            return jResponse["requestName"]
        else:
            if debug:
                print(jResponse)
            return None

    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
#  2501 - GitLab Health Check
########################################################

def isGitlabHealthy(inFqdn, verify):

    if debug:    
        print(f"Function: isGitlabHealthy")
        print(f"FQDN: {inFqdn}")
        print(f"sslVerify: {verify}")

    try:

        print(f"2501: Gitlab Health Check '{inFqdn}'")
        lsf.write_output(f'2501: Gitlab Health Check: {inFqdn}', logfile=lsf.logfile)

        url = f"https://{inFqdn}/-/health"
            
        headers = {}
        
        payload = {}
    
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None)
        response.raise_for_status()

        if not (response.status_code < 200 or response.status_code >= 300):
            return True
        else:
            return False
              
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP - {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT - {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
# 2501 - GitLab Readiness Check
########################################################

def isGitlabReady(inFqdn, verify):

    if debug:    
        print(f"Function: isGitlabReady")
        print(f"FQDN: {inFqdn}")
        print(f"sslVerify: {verify}")

    try:
        print(f"2501: Gitlab Readiness Check '{inFqdn}'")
        lsf.write_output(f'2501: Gitlab Readiness Check: {inFqdn}', logfile=lsf.logfile)

        url = f"https://{inFqdn}/-/readiness?all=1"
            
        headers = {}
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()

        if not (response.status_code < 200 or response.status_code >= 300):
            jResponse = response.json()
            if jResponse['status'] == "ok":
                for key, value in jResponse.items():
                    if isinstance(value, list):
                        for item in value:
                            if item['status'] != 'ok':
                                return False
                return True   
        else:
            return False                             
              
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
# 2501 - GitLab Liveness Check
########################################################

def isGitlabLive(inFqdn, verify):

    if debug:    
        print(f"Function: isGitlabLive")
        print(f"FQDN: {inFqdn}")
        print(f"sslVerify: {verify}")

    try:
        print(f"2501: Gitlab Liveness Check '{inFqdn}'")
        lsf.write_output(f'2501: Gitlab Liveness Check: {inFqdn}', logfile=lsf.logfile)

        url = f"https://{inFqdn}/-/liveness"
            
        headers = {}
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()

        if not (response.status_code < 200 or response.status_code >= 300):
            jResponse = response.json()
            if jResponse['status'] != "ok":
                return False  
            return True
              
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
# 2501 - GUID Check
########################################################

def isGuid(testString):

    if debug:    
        print(f"Function: isGuid")
        print(f"String: {testString}")


    guidPattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

    try:
        match = re.search(guidPattern, testString)
        if match:
            return True
        else:
            return False
        
    except Exception as e:
        print(f"2501: Pattern Match Error - Provided string is not a vmid (UUID)")
        lsf.write_output(f'2501: Pattern Match Error - Provided string is not a vmid (UUID)', logfile=lsf.logfile)
    
########################################################
# 2501 - Aria Suite Lifecycle Readiness Check
########################################################

def isLifecycleReady(inFqdn, token, verify):

    if debug:
        print(f"Function: isLifecycleReady")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")

    try:

        url = f"https://{inFqdn}/lcm/health/api/v2/status"
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()
        jResponse = response.json()  

        if not (response.status_code < 200 or response.status_code >= 300):
            
            isReady = True

            for service, status in jResponse.items():
                if status == "UP":
                    print(f'2501: Aria Lifecycle Ready Check - {service} is {status}')
                    lsf.write_output(f'2501: Aria Lifecycle Ready Check - {service} is {status}', logfile=lsf.logfile) 
                else:
                    print(f'2501: Aria Lifecycle Ready Check - {service} is {status}')
                    lsf.write_output(f'2501: Aria Lifecycle Ready Check - {service} is {status}', logfile=lsf.logfile) 
                    isReady = False
            
            return isReady
        
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
        return False
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)
        return False

#####################################################
# 2501 -  Get Error Cause for Request
#####################################################

def getErrorIdByRequestId(inFqdn, token, verify, requestId):

    if debug:
        print(f"In: getErrorIdByRequestId")


    try:
        url = f"https://{inFqdn}/lcm/request/api/v2/requests/{requestId}/error-causes"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()  
        errorCause = response.json()

        if debug:
            print(errorCause)

        if not (response.status_code < 200 or response.status_code >= 300):
            if len(errorCause) > 0:
                return errorCause[0]['messageId']
        
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

#####################################################
# 2501 -  Get Error Cause for Requests 
#####################################################

def getErrorCauseByRequestId(inFqdn, token, verify, requestId):

    if debug:
        print(f"Function: getErrorCauseByRequestId")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"Request Id: {requestId}")

    try:
        url = f"https://{inFqdn}/lcm/request/api/v2/requests/{requestId}/error-causes"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = {}

        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()  
        errorCause = response.json()

        if debug:
            print(errorCause)

        if not (response.status_code < 200 or response.status_code >= 300):
            return errorCause
        
    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

#####################################################
# 2501 -  Retry Request
#####################################################

def retryRequest(inFqdn, token, verify, requestId, errorCause):

    if debug:
        print(f"Function: retryRequest")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")
        print(f"Request Id: {requestId}")
        print(f"Error Cause: {errorCause}")

    try:
        url = f"https://{inFqdn}/lcm/request/api/v2/requests/{requestId}/retry"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + token,
            'Accept': 'application/json'
        }

        payload = json.dumps(errorCause, indent=4)

        session = requests.Session()
        session.trust_env = False

        response = session.patch(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status()  

        if not (response.status_code < 200 or response.status_code >= 300):
            return True
        
    except requests.exceptions.HTTPError as e:
        print(f'2501: HTTP -  {e}')
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f'2501: CONNECT -  {e}')
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f'2501: TIMEOUT - {e}')
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f'2501: REQUEST - {e}')
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
# 2501 - Identity Manager Health Check
########################################################

def isIdmReady(inFqdn, verify):

    if debug:    
        print(f"Function: isIdmReady")
        print(f"FQDN: {inFqdn}")
        print(f"sslVerify: {verify}")

    try:
        print(f"2501: VMware Workspace ONE Access - Ready Check '{inFqdn}'")
        lsf.write_output(f'2501: VMware Workspace ONE Access - Ready Check: {inFqdn}', logfile=lsf.logfile)

        url = f"https://{inFqdn}/SAAS/API/1.0/REST/system/health"
            
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()

        if debug:    
            print(f"{response.text}")

        if not (response.status_code < 200 or response.status_code >= 300):
            jResponse = response.json()

            isReady = True

            healthStatus = {service: jResponse[service] for service in ['MessagingConnectionOk','DatabaseConnectionOk','EncryptionConnectionOk','AnalyticsConnectionOk','FederationBrokerOk','AllOk']}

            for service, status in healthStatus.items():
                if status == "true":
                    print(f'2501: VMware Workspace ONE Access - Ready Check: [{service}] is {status}')
                    lsf.write_output(f'2501: VMware Workspace ONE Access - Ready Check: [{service}] is {status}', logfile=lsf.logfile) 
                else:
                    print(f'2501: VMware Workspace ONE Access - Ready Check: - [{service}] is {status}')
                    lsf.write_output(f'2501: VMware Workspace ONE Access - Ready Check: [{service}] is {status}', logfile=lsf.logfile) 
                    isReady = False
            
            return isReady                          
              
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)


########################################################
# 2501 - Reset Expired Password
########################################################

def resetPassword(hostname, username, password, newPassword):
    
    child = pexpect.spawn(f'ssh -o StrictHostKeyChecking=no {username}@{hostname}')

    prompts = [
        'password: ',
        'Current password: ',
        'New password: ',
        'Retype new password: ',
        pexpect.EOF,
        pexpect.TIMEOUT
    ]

    try:
        
        index = child.expect(prompts)

        if index == 0:
            print(prompts[index])
            child.sendline(password)
            index = child.expect(prompts)
    
        if index == 1:
            print(prompts[index])
            child.sendline(password)
            index = child.expect(prompts)

        if index == 2:
            print(prompts[index])
            child.sendline(newPassword)
            index = child.expect(prompts)

        if index == 3:
            print(prompts[index])
            child.sendline(newPassword)
            index = child.expect(prompts)

       
        child.expect(f'{username}@{hostname} [ ~ ]# ')
        child.sendline('chage -M -1 root; echo "" > /etc/security/opasswd')
        child.sendline('passwd')
        child.expect('New password: ')
        child.sendline(password)       
        child.expect('Retype new password: ')
        child.sendline(password)
        
    except pexpect.exceptions.EOF:
        print('Connection closed unexpectedly.')
    except pexpect.exceptions.TIMEOUT:
        print('Connection timed out.')
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f'An error occurred: {e}.')
    finally:
        child.close()

########################################################
# 2501 - Auto Service Ready Check
########################################################

# def isAutoReady(inFqdn, username, password):
    
#     services = []
#     result = lsf.ssh('kubectl get pods --all-namespaces', f'{username}@{inFqdn}', password)
#     output = result.stdout.strip()
#     output = output.splitlines()

#     try:
#         for line in output[1:]:
#             info = line.split()
#             temp = {
#                     'name': info[1],
#                     'config': {
#                         'namespace':info[0],
#                         'ready': info[2],
#                         'status': info[3],
#                         'restarts': info[4],
#                         'age': info[5]
#                         }
#                 }   
#             services.append(temp)

#             count = 0

#         if len(services) > 0:
#             print(f"2501: Checking {len(services)} Aria Automation Pods for readiness...")
#             lsf.write_output(f"2501: Checking {len(services)} Aria Automation Pods for readiness...", logfile=lsf.logfile)
#             for service in services:
#                 print(f"2501: {service['name']} is {service['config']['status']}")
#                 lsf.write_output(f"2501: {service['name']} is {service['config']['status']}", logfile=lsf.logfile)
#                 if service['config']['status'] == 'Running' or 'Completed':
#                     count = count + 1
#                 else:
#                     print(f"2501: {service['name']} is {service['config']['status']}")
#                     lsf.write_output(f"2501: {service['name']} is {service['config']['status']}", logfile=lsf.logfile)

#             print(f"2501: {count} out of {len(services)} are Completed/Ready")
#             lsf.write_output(f"2501: {count} out of {len(services)} are Completed/Ready", logfile=lsf.logfile)
#         else:
#             raise Exception(f"No Aria Automation Pods found.")
        
#         if count <= len(services): 
#             return True
#         else: 
#             return False

#     except Exception as e:
#         print(f'2501: Error - {e}')
#         lsf.write_output(f'2501: Error - {e}', logfile=lsf.logfile)  

########################################################
# 2501 - Run remote SSH command (ASYNC)
########################################################

# def ssh_async(command, user, inFqdn, password):

#     sshOptions = '-o StrictHostKeyChecking=accept-new'
    
#     rCommand = ['/usr/bin/sshpass', '-p', password, 'ssh', sshOptions, f'{user}@{inFqdn}', command]
    
#     try:
#         print(f"Running {command} on {inFqdn}")
#         run = subprocess.Popen(rCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
#     except Exception as e:
#         lsf.write_output(f'{e}', logfile=lsf.logfile)
#         run.stdout = str(e)      

#     finally:
#         return run
    
# def ssh_async(command, user, inFqdn, password):

#     sshOptions = '-o StrictHostKeyChecking=accept-new'
    
#     rCommand = f"sshpass -p {password} ssh -o {sshOptions} {user}@{inFqdn} 'nohup {command} > /dev/null 2>&1 &'"

#     try:
#         print(f"Running {command} on {inFqdn}")
#         run = subprocess.run(rCommand, shell=True, capture_output=True, text=True)
        
#     except subprocess.CalledProcessError as e:
#         lsf.write_output(f'{e}', logfile=lsf.logfile)
#         run.stdout = str(e)      

#     finally:
#         return run.stdout.strip()
    
########################################################
# 2501 - Folder Exists?
########################################################

def folderExists(path):
    winPath = path
    try:

        if path.startswith('/wmchol'):
            winPath = re.sub(r'/wmchol', r'C:\\', path)
            winPath = winPath.replace('/','\\')
    
        if os.path.exists(f'{path}'):
            lsf.write_output(f'2501: Checking Folder [{winPath}]... EXISTS', logfile=lsf.logfile)
            print(f'2501: Checking Folder [{winPath}]... EXISTS')
            return True
        else:
            lsf.write_output(f'2501: Checking Folder [{winPath}]... MISSING', logfile=lsf.logfile)
            print(f'2501: Checking Folder [{winPath}]... MISSING')
            return False
        
    except Exception as e:
        lsf.write_output(f'{e}', logfile=lsf.logfile)
        print(f'2501: {e}')     
########################################################
# 2501 - Delete Folder
########################################################

def deleteFolder(path):
    winPath = path

    try:
        if path.startswith('/wmchol'):
            winPath = re.sub(r'/wmchol', r'C:\\', path)
            winPath = winPath.replace('/','\\')
    
        command = f"powershell -NoProfile -ExecutionPolicy Bypass -Command Remove-Item {winPath} -Recurse"
        lsf.runwincmd(command,'mainconsole','Administrator', '{REPLACE_WITH_PASSWORD}')
        lsf.write_output(f'2501: Checking Folder [{winPath}]... DELETED', logfile=lsf.logfile)
        print(f'2501: Checking Folder [{winPath}]... DELETED')
    
    except Exception as e:
        lsf.write_output(f'2501: {e}', logfile=lsf.logfile)
        print(f'2501: {e}')

########################################################
# 2501 - Create Folder
########################################################
def createFolder(path, folder):
    winPath = path

    try:
        if path.startswith('/wmchol'):
            winPath = re.sub(r'/wmchol', r'C:\\', path)
            winPath = winPath.replace('/','\\')
        else:
            winPath = path

        if folderExists(f'{path}/{folder}'):
            deleteFolder(f'{path}/{folder}')

        lsf.write_output(f'2501: Checking for Folder [{winPath}\{folder}]... CREATED', logfile=lsf.logfile)
        print(f'2501: Checking for Folder [{winPath}\{folder}]... CREATED')
        command = f"powershell -NoProfile -ExecutionPolicy Bypass -Command New-Item -Path '{winPath}' -Name '{folder}' -ItemType 'Directory'"
        lsf.runwincmd(command,'mainconsole','Administrator', '{REPLACE_WITH_PASSWORD}')

        
    except Exception as e:
        lsf.write_output(f'2501: {e}', logfile=lsf.logfile)
        print(f'2501: {e}')

########################################################
# 2501 - Auto URL Status Check
########################################################

def isAutoReady(inFqdn, verify):

    if debug:    
        print(f"Function: isAutoReady")
        print(f"FQDN: {inFqdn}")
        print(f"sslVerify: {verify}")

    try:
        print(f"2501: Aria Automation URL Check '{inFqdn}'")
        lsf.write_output(f'2501: Aria Automation URL Check: {inFqdn}', logfile=lsf.logfile)

        url = f"http://{inFqdn}:8008/health"
            
        headers = {}
        
        payload = {}
        
        # session = requests.Session()
        # session.trust_env = False

        response = requests.get(url=url, data=payload, headers=headers, verify=False, timeout=10, proxies=None)
        response.raise_for_status()

        if response.status_code == 200:
            return True
        else:
            return False
              
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)

########################################################
# Get Ops Token (Username/Password))
########################################################

def getOpsToken(inFqdn, username, password, authSource, verify):
    
    if debug:
        print(f"Function: getOpsToken")
        print(f"FQDN: {inFqdn}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"authSource: {authSource}")
        print(f"sslVerify: {verify}")


    if authSource == None:
        authSource = "LOCAL"

    url = f"https://{inFqdn}/suite-api/api/auth/token/acquire"
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = json.dumps({
        "username": username,
        "password": password,
        "authSource": authSource
    })


    if debug:
        print(payload)


    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(url=url, data=payload, headers=headers, verify=verify )
        response.raise_for_status

        if not (response.status_code < 200 or response.status_code >= 300):
            jResponse = response.json()
            response.raise_for_status
            return(jResponse["token"])    
              
    except requests.exceptions.HTTPError as e:
        print(f"{Fore.RED}ERROR:{Fore.WHITE} HTTP: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"{Fore.RED}ERROR:{Fore.WHITE} CONNECT: {e}")
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}ERROR:{Fore.WHITE} TIMEOUT: {e}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}ERROR:{Fore.WHITE} REQUEST: {e}")

#######################################################
# 2501 - Operations Service Check
########################################################

def opsServiceCheck(inFqdn, token, verify):

    if debug:
        print(f"Function: opsServiceCheck")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")

    try:

        url = f"https://{inFqdn}/suite-api/api/deployment/node/services/info"
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OpsToken ' + token,
            'Accept': 'application/json'
        }
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()
        jResponse = response.json()  

        if not (response.status_code < 200 or response.status_code >= 300):
            
            isReady = True

            for service in jResponse['service']:
                print(f"2501: Aria Operations Ready Check [{inFqdn}] - [{service['name']}] is {service['health']}")
                lsf.write_output(f"2501: Aria Operations Ready Check [{inFqdn}] - [{service['name']}] is {service['health']}", logfile=lsf.logfile)
                if service['health'] == "OK":
                    isReady = True
                else:
                    isReady = False
            
            return isReady
        
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
        return False
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)
        return False

#######################################################
# 2501 - Operations Node Status Check
########################################################

def opsNodeCheck(inFqdn, token, verify):

    if debug:
        print(f"Function: opsNodeCheck")
        print(f"FQDN: {inFqdn}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")

    try:

        url = f"https://{inFqdn}/suite-api/api/deployment/node/status"
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OpsToken ' + token,
            'Accept': 'application/json'
        }
        
        payload = {}
        
        session = requests.Session()
        session.trust_env = False

        response = session.get(url=url, data=payload, headers=headers, verify=verify, proxies=None )
        response.raise_for_status()
        node = json.loads(response.text) 

        isNodeReady = True

        if not (response.status_code < 200 or response.status_code >= 300):
            print(f"2501: Aria Operations Ready Check - Node [{inFqdn}] - {node['status']}")
            lsf.write_output(f"2501: Aria Operations Ready Check - Node [{inFqdn}] - {node['status']}", logfile=lsf.logfile)
            if node['status'] == "ONLINE":
                isNodeReady = True
            else:
                isNodeReady = False    
        
        return isNodeReady
    
    except requests.exceptions.HTTPError as e:
        print(f"2501: HTTP -  {e}")
        lsf.write_output(f'2501: HTTP Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.ConnectionError as e:
        print(f"2501: CONNECT -  {e}")
        lsf.write_output(f'2501: Connection Error - {e}', logfile=lsf.logfile)
        return False
    except requests.exceptions.Timeout:
        print(f"2501: TIMEOUT - {e}")
        lsf.write_output(f'2501: Timeout Error - {e}', logfile=lsf.logfile)
    except requests.exceptions.RequestException as e:
        print(f"2501: REQUEST - {e}")
        lsf.write_output(f'2501: Request Error - {e}', logfile=lsf.logfile)
        return False

#######################################################
# 2501 - Operations Node Status Check
########################################################

def isOpsReady(opsNodes, token, verify):

    if debug:
        print(f"Function: isOpsReady")
        for node in opsNodes:
            print(f"FQDN: {node}")
        print(f"Token: {token}")
        print(f"sslVerify: {verify}")

    try:

        opsReady = True

        for node in opsNodes:
            print(f"2501: Aria Operations Ready Check [{node}]")
            lsf.write_output(f"2501: Aria Operations Ready Check [{node}]", logfile=lsf.logfile)
            if opsNodeCheck(node, token, verify):
                if opsServiceCheck(node, token, verify):
                    opsReady = True
                else:
                    opsReady = False
            else:
                opsReady = False
        
        return opsReady
    
    except Exception as e:
        lsf.write_output(f'2501: {e}', logfile=lsf.logfile)
        print(f'2501: {e}')


#######################################################
# 2501 - Operations Node Status Check
########################################################

def isSshReady(host, user, password, maxRetries=20, delay=60):

    if debug:
        print(f"Function: isSshReady")
        print(f"Host: {host}")
        print(f"Token: {user}")
        print(f"sslVerify: {password}")

    for attempt in range(maxRetries):

        try:
            
            command = f"sshpass -p {password} ssh -o StrictHostKeyChecking=no {user}@{host} 'exit'"

            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                lsf.write_output(f'2501: SSH is available on [{host}] after {attempt + 1}.', logfile=lsf.logfile)
                print(f'2501: SSH is available on [{host}] after {attempt + 1}.')
                return True
            else:
                lsf.write_output(f'2501: Attempt {attempt + 1} - SSH is not available on [{host}]. Retrying in {delay} seconds.', logfile=lsf.logfile)
                print(f'2501: Attempt {attempt + 1} - SSH is not available on [{host}]. Retrying in {delay} seconds.')

        except subprocess.CalledProcessError as e:
            lsf.write_output(f'2501: Attempt {attempt + 1} - [Error] {e}. Retrying in {delay} seconds.', logfile=lsf.logfile)
            print(f'2501: Attempt {attempt + 1} - [Error] {e}. Retrying in {delay} seconds.')

        time.sleep(delay)

    lsf.write_output(f'2501: Maximum [{maxRetries}] retires reached.', logfile=lsf.logfile)
    print(f'2501: Maximum [{maxRetries}] retires reached.')
    return False