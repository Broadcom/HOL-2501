# Tanzu.py version 0.1 13-February 2024
import datetime
import os
import sys
from pyVim import connect
from pyVmomi import vim
import logging
import lsfunctions as lsf


#####################################################
# 2501: Import Module & set Global variables
#####################################################

sys.path.append('/vpodrepo/2025-Labs/2501')
import hol2501 as hol
import time
sslVerify = False
lcmFqdn = "lcm.vcf.sddc.lab"

def verify_nic_connected (vm_obj, simple):
    """
    Loop rhrough the NICs and verify connection
    :param vm: the VM to check
    :param simple: true just connect do not disconnect then reconnect
    """
    nics = lsf.get_network_adatper(vm_obj)
    for nic in nics:
        if simple:
            lsf.write_output(f'Connecting {nic.deviceInfo.label} on {vm.name} .')
            lsf.set_network_adapter_connection(vm, nic, True)
            lsf.labstartup_sleep(lsf.sleep_seconds)
        elif nic.connectable.connected == True:
            lsf.write_output(f'{vm.name} {nic.deviceInfo.label} is connected.')
        else:
            lsf.write_output(f'{vm.name} {nic.deviceInfo.label} is NOT connected.')
            lsf.set_network_adapter_connection(vm, nic, False)
            lsf.labstartup_sleep(lsf.sleep_seconds)
            lsf.write_output(f'Connecting {nic.deviceInfo.label} on {vm.name} .')
            lsf.set_network_adapter_connection(vm, nic, True)

# read the /hol/config.ini
lsf.init(router=False)

# verify a VCFfinal section exists
if lsf.config.has_section('VCFFINAL') == False:
    lsf.write_output('Skipping VCF final startup')
    exit(0)

color = 'red'
if len(sys.argv) > 1:
    lsf.start_time = datetime.datetime.now() - datetime.timedelta(seconds=int(sys.argv[1]))
    if sys.argv[2] == "True":
        lsf.labcheck = True
        color = 'green'
        lsf.write_output(f'{sys.argv[0]}: labcheck is {lsf.labcheck}')   
    else:
        lsf.labcheck = False
 
lsf.write_output(f'Running {sys.argv[0]}')


lsf.write_vpodprogress('Tanzu Start', 'GOOD-8', color=color)

### Start SupervisorControlPlaneVMs
vcfmgmtcluster = []
if 'vcfmgmtcluster' in lsf.config['VCF'].keys():
    vcfmgmtcluster = lsf.config.get('VCF', 'vcfmgmtcluster').split('\n')
    lsf.write_vpodprogress('VCF Hosts Connect', 'GOOD-3', color=color)
    lsf.connect_vcenters(vcfmgmtcluster)

lsf.write_vpodprogress('Tanzu Control Plane', 'GOOD-8', color=color)
supvms = lsf.get_vm_match('Supervisor*')
for vm in supvms:
   lsf.write_output(f'{vm.name} is {vm.runtime.powerState}')
   try:
        if vm.runtime.powerState != "poweredOn":
            lsf.start_nested([f'{vm.name}:{vm.runtime.host.name}'])
   except Exception as e:
        lsf.write_output(f'exception: {e}')

### Reconnect SupervisorControlPlaneVM NICs
for vm in supvms:
    verify_nic_connected (vm, False) # if not connected, disconnet then reconnect
                
# Wizardry to deploy Tanzu

tanzucreate = []
if 'tanzucreate' in lsf.config['VCFFINAL'].keys():
    lsf.write_vpodprogress('Deploy Tanzu (25 Minutes)', 'GOOD-8', color=color)
    lsf.write_output('Deploy Tanzu (25 Minutes)')
    tanzucreate = lsf.config.get('VCFFINAL', 'tanzucreate').split('\n')
    lsf.write_vpodprogress('Waiting for Tanzu img to populate', 'GOOD-8', color=color)
    lsf.write_output('Waiting for Tanzu Images (10 minutes)...')
    # DEBUG skip this for dev testing - is there a test we can do?
    lsf.labstartup_sleep(600)

    # centos machine is 10.0.0.3 /root/TanzuCreate script. recommend DNS entry
    (tchost, tcaccount, tcpassword, tcscript) = tanzucreate[0].split(':')
    lsf.write_output(f'Running {tcscript} as {tcaccount}@{tchost} with password {tcpassword}')
    # DEBUG comment out
    result = lsf.ssh(tcscript, f'{tcaccount}@{tchost}', tcpassword, logfile=lsf.logfile)
    lsf.write_output(result.stdout)

#####################################################
# 2501 - Aria Operations Status Check
#####################################################
# opsMasterNode = 'ops.vcf.sddc.lab'
# opsNodes = [ opsMasterNode, 'ops-cp.vcf.sddc.lab']

# token = hol.getOpsToken(opsMasterNode,'admin',lsf.password,'LOCAL', sslVerify)

# print(f"2501: Aria Operations Status Check - CHECKING")
# lsf.write_output(f"2501: Aria Operations Status Check - CHECKING", logfile=lsf.logfile)

# while not hol.isOpsReady(opsNodes, token, sslVerify):
#     print(f"2501: Aria Operations Status Check - WAITING")
#     lsf.write_output(f"2501: Aria Operations Status Check - WAITING", logfile=lsf.logfile)
#     lsf.labstartup_sleep(60)

# if hol.isOpsReady(opsNodes, token, sslVerify):
#     print(f"2501: Aria Operations Status Check - READY")
#     lsf.write_output(f"2501: Aria Operations Status Check - READY", logfile=lsf.logfile)    

#####################################################
# 2501 - Get Encrypted Token
#####################################################

token = hol.getEncodedToken('vcfadmin@local',lsf.password)

#####################################################
# 2501 - WorkspaceONE Access Power On and Status Check
#####################################################

idmFqdn = 'idm.vcf.sddc.lab'

lsf.write_vpodprogress('Bringing Workspace ONE Access Online', 'GOOD-8', color=color)
lsf.write_output(f'2501: Bringing Workspace ONE Access Online', logfile=lsf.logfile)

if not hol.isIdmReady(idmFqdn, sslVerify):
    
    environments = ['globalenvironment']
    productIds = ['vidm']

    try:
        for env in environments:
            print(f'2501: Checking {lcmFqdn} for {env} environment.')
            lsf.write_output(f'2501: Checking {lcmFqdn} for {env} environment.', logfile=lsf.logfile)
            envId = hol.getEnvironmentVmidByName(lcmFqdn, token, sslVerify, env)
            if (envId):
                print(f'2501: Environment {env} has an ID of {envId}')
                lsf.write_output(f'2501: Environment {env} has an ID of {envId}.', logfile=lsf.logfile)
                for productId in productIds:
                    for state in ["INPROGRESS", "FAILED", "COMPLETED"]:
                        requestId = hol.getRequestIdFromActiveRequests(lcmFqdn, token, sslVerify, envId, productId, state)
                        if not requestId == None:
                            hol.checkRequestStatus(lcmFqdn, token, sslVerify, requestId)
                            break
                        continue
            else:
                print(f'2501: Environment {env} does not exist.')
                lsf.write_output(f'2501: Environment {env} does not exist.', logfile=lsf.logfile)
    except Exception as e:
        lsf.write_output(f'2501: {e}', logfile=lsf.logfile)
        print(f'2501: Error: {e}')
else:
    lsf.write_output(f'VMware Workspace ONE Access - Ready Check: READY', logfile=lsf.logfile)
    print(f'2501: VMware Workspace ONE Access - Ready Check: READY')

#####################################################
# 2501 - Aria Automation Power On and Status Check
#####################################################

# environments = ['Production']
# productIds = ['vra']
autoFqdn = 'auto.vcf.sddc.lab'

if hol.isAutoReady(autoFqdn, sslVerify):
    lsf.write_output(f'2501: Aria Automation Ready Check - READY', logfile=lsf.logfile)
    print(f'2501: Aria Automation Ready Check - READY')

# if not lsf.labcheck:
#     lsf.write_vpodprogress('Bringing Aria Automation Online', 'GOOD-8', color=color)
#     lsf.write_output(f'2501: Bringing Aria Automation Online', logfile=lsf.logfile)
# #     try:
# #         for env in environments:
# #             print(f'2501: Checking {lcmFqdn} for {env} environment.')
# #             lsf.write_output(f'2501: Checking {lcmFqdn} for {env} environment.', logfile=lsf.logfile)
# #             envId = hol.getEnvironmentVmidByName(lcmFqdn, token, sslVerify, env)
# #             if (envId):
# #                 print(f'2501: Environment {env} has an ID of {envId}')
# #                 lsf.write_output(f'2501: Environment {env} has an ID of {envId}.', logfile=lsf.logfile)
# #                 for productId in productIds:
# #                     for state in ["INPROGRESS", "FAILED", "COMPLETED"]:
# #                         requestId = hol.getRequestIdFromActiveRequests(lcmFqdn, token, sslVerify, envId, productId, state)
# #                         if not requestId == None:
# #                             hol.checkRequestStatus(lcmFqdn, token, sslVerify, requestId)
# #                             break
# #                         continue
# #             else:
# #                 print(f'2501: Environment {env} does not exist.')
# #                 lsf.write_output(f'2501: Environment {env} does not exist.', logfile=lsf.logfile)
# #     except Exception as e:
# #         lsf.write_output(f'2501: {e}', logfile=lsf.logfile)
# #         print(f'2501: Error: {e}')
# #     finally:
# #         productIds = []
# #         environments = []
# # else:
#     if hol.isAutoReady(autoFqdn, sslVerify):
#         lsf.write_output(f'2501: Aria Automation Ready Check - READY', logfile=lsf.logfile)
#         print(f'2501: Aria Automation Ready Check - READY')
#     else:
#         lsf.write_output(f'2501: Aria Automation Ready Check - NOT READY', logfile=lsf.logfile)
#         print(f'2501: Aria Automation Ready Check - NOT READY')    
#         try:
#             environments = ['Production']
#             productIds = ['vra']

#             autoRequestId = hol.triggerPowerEvent(lcmFqdn, token, sslVerify, environments, productIds, "power-on")

#         except Exception as e:
#             lsf.write_output(f'2501: Exception: {e}', logfile=lsf.logfile)
#             print(f'2501: Exception: {e}')
#         finally:
#             productIds = []
#             environments = []

######Start Aria Automation VMs
# Could we start this during the 10 minutes we're waiting for Tanzu?

vravms = []

if 'vravms' in lsf.config['VCFFINAL'].keys():
    vravms = lsf.config.get('VCFFINAL', 'vravms').split('\n')
    lsf.write_output('Starting Workspace Access...')
    lsf.write_vpodprogress('Starting Workspace Access', 'GOOD-8', color=color)
    # before starting verify NICs are set to start connected
    for vravm in vravms:
        (vmname, server) = vravm.split(':')
        vm = lsf.get_vm(vmname)
        verify_nic_connected (vm, True) # just make sure connected at start
    lsf.start_nested(vravms)
    # verify that the wsa L2 VM is actually starting
    # after starting verify NIC is actually connected
    for vravm in vravms:
        (vmname, server) = vravm.split(':')
        vm = lsf.get_vm(vmname)
        while vm.runtime.powerState != 'poweredOn':
            vm.PowerOnVM_Task()
            lsf.labstartup_sleep(lsf.sleep_seconds)
        while vm.summary.guest.toolsRunningStatus != 'guestToolsRunning':
            lsf.write_output(f'Waiting for Tools in {vmname}...')
            lsf.labstartup_sleep(lsf.sleep_seconds)
            verify_nic_connected (vm, False) # if not connected, disconnect and reconnect

##### Final URL Checking
vraurls = []
if 'vraurls' in lsf.config['VCFFINAL'].keys():
    vraurls = lsf.config.get('VCFFINAL', 'vraurls').split('\n')
    lsf.write_vpodprogress('Aria Automation URL Checks', 'GOOD-8', color=color)
    lsf.write_output('Aria Automation URL Checks...')
    for entry in vraurls:
        url = entry.split(',')
        lsf.write_output(f'Testing {url[0]} for pattern {url[1]}')
        #  not_ready: optional pattern if present means not ready verbose: display the html
        #  lsf.test_url(url[0], pattern=url[1], not_ready='not yet', verbose=True)
        ctr = 0
        while not lsf.test_url(url[0], pattern=url[1], timeout=2, verbose=False):
            lsf.write_output(f'Sleeping and will try again...')
            lsf.labstartup_sleep(lsf.sleep_seconds)
            ctr += 1

for si in lsf.sis:
    connect.Disconnect(si)

lsf.write_output(f'{sys.argv[0]} finished.')

