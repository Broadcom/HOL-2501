# prelim.py version 1.13 18-April 2024
import sys
import os
import glob
import json
import logging
import datetime
import lsfunctions as lsf
from pathlib import Path

#####################################################
# 2501: Import Module & set Global variables
#####################################################

sys.path.append('/vpodrepo/2025-Labs/2501')
import hol2501 as hol

# default logging level is WARNING (other levels are DEBUG, INFO, ERROR and CRITICAL)
logging.basicConfig(level=logging.DEBUG)

# Record whether this is a first run or a LabCheck execution
lsf.test_labcheck()

color = 'red'
if len(sys.argv) > 1:
    lsf.start_time = datetime.datetime.now() - datetime.timedelta(seconds=int(sys.argv[1]))
    if sys.argv[2] == "True":
        lsf.labcheck = True
        color = 'green'
        lsf.write_output(f'{sys.argv[0]}: labcheck is {lsf.labcheck}', logfile=lsf.logfile)   
    else:
        lsf.labcheck = False

# read the /hol/config.ini
lsf.init(router=False)

lsf.write_output(f'Running {sys.argv[0]}', logfile=lsf.logfile)
lsf.write_vpodprogress('PRELIM', 'GOOD-2', color=color)

#
# Copy this file to the /vpodrepo/202?-Labs/2??? folder for your vPod_SKU
# Make your changes after the Core Team code section
# 

#
## Begin Core Team code (please do not edit)
#

# prevent the annoying Firefox banner if WMC
if lsf.WMC and lsf.labtype == 'HOL':
    appdata = f'{lsf.mc}/Users/Administrator/AppData'
    ffroamprofiles = f'{appdata}/Roaming/Mozilla/Firefox/Profiles/*.default-release'
    fflocalprofiles = f'{appdata}/Local/Mozilla/Firefox/Profiles/*.default-release'
    os.system(f'rm {ffroamprofiles}/parent.lock > /dev/null 2>&1')
    os.system(f'rm -rf {ffroamprofiles}/storage > /dev/null 2>&1')
    os.system(f'rm -rf {fflocalprofiles}/cache2 > /dev/null 2>&1')
    # and apparently all this is not enough. must also create user.js with disableResetPrompt option
    releasedir = glob.glob(ffroamprofiles)
    resetprompt = 'user_pref("browser.disableResetPrompt", true);'
    userpref = f'{releasedir[0]}/user.js'
    prefneeded = True
    if not os.path.isfile(userpref):
        Path(userpref).touch()
    with open(userpref, 'r') as fp:
        prefs = fp.read()
        for pref in prefs:
            if pref.find('disableResetPrompt'):
                prefneeded = False
                break
    fp.close()
    if prefneeded:
        lsf.write_output(f'need to add {resetprompt} in {userpref}')
        with open(userpref, 'a') as fp:
            fp.write(f'{resetprompt}\n')
        fp.close()

# verify the router firewall is active
checkfw = True
# test an external url to be certain the connection is blocked. The last argument is the timeout.
if lsf.labtype != 'HOL':
    lsf.write_output(f'NOT checking firewall for labtype {lsf.labtype}')
    checkfw = False

# check the firewall from the Main Console
fwok = False
if lsf.labcheck == False and checkfw == True:
    lsf.write_output('Checking firewall from the Main Console...')
    ctr = 0
    # guessing the Mara DNS instance in VCF labs takes a little time to initialize
    if lsf.config.has_section('VCF') == True:
        maxctr = 20
        lsf.write_output("Sleeping 60 seconds for VCF lab to stabilize...")
        lsf.labstartup_sleep(60)
    else:
        maxctr = 10
    lsf.run_command(f'cp {lsf.holroot}/Tools/checkfw.py {lsf.mctemp}')
    output = []
    if lsf.LMC:
        try:
            fwout = lsf.ssh('/usr/bin/python3 /tmp/checkfw.py', 'holuser@mainconsole', lsf.password)
            output = fwout.stdout
        except Exception as e:
            lsf.write-output(f'Error running checkfw.py: {e}')
    elif lsf.WMC:
        try:
            output = lsf.runwincmd('python C:\\Temp\\checkfw.py', 'mainconsole', 'Administrator', lsf.password, logfile=lsf.logfile)
        except Exception as e:
            lsf.write-output(f'Error running checkfw.py: {e}')
    while 'Good' not in output and ctr < maxctr:
        if lsf.LMC:
            fwout = lsf.ssh('/usr/bin/python3 /tmp/checkfw.py', 'holuser@mainconsole', lsf.password)
            output = fwout.stdout
        elif lsf.WMC:
            output = lsf.runwincmd('python C:\\Temp\\checkfw.py', 'mainconsole', 'Administrator', lsf.password, logfile=lsf.logfile)        
        for line in output:
            if 'Good' in line:
                fwok = True
                break
        ctr += 1
        if ctr == 10:
            lsf.write_output('Firewall is OFF for the Main Console. ing lab.')
            lsf.labfail('OPEN FIREWALL')        
        lsf.write_output(f'Checking firewall on Main Console. Attempt: {ctr}')
        lsf.write_output(f'firewall output: {output} {ctr}')
        lsf.labstartup_sleep(lsf.sleep_seconds)
    
    if fwok:
        lsf.write_output('Firewall is on for the Main Console.', logfile=lsf.logfile)
    #lsf.test_firewall('https://vmware.com', '<title>', 2)
    lsf.run_command(f'rm {lsf.mctemp}/checkfw.py')

if lsf.WMC and lsf.labcheck == False:   
    # execute the WMCstart script on the WMC to address startup issues
    # Windows console locking and DesktopInfo startup issue on Windows 2019
    admindir = 'Users/Administrator'
    os.system(f'cp {lsf.holroot}/Tools/WMCstartup.ps1 {lsf.mc}/{admindir}/')
    # C:\Program Files\PowerShell\7\pwsh.exe
    command = 'pwsh C:\\Users\\Administrator\\WMCstartup.ps1 > C:\\Users\\Administrator\\WMCstartup.log'
    lsf.write_output('Running WMCstartup.ps1 on mainconsole. Please stand by...', logfile=lsf.logfile)
    lsf.runwincmd(command, 'mainconsole', 'Administrator', lsf.password, logfile=lsf.logfile)
    with open(f'{lsf.mc}/{admindir}/WMCstartup.log', 'r') as ologfile:
        olog = ologfile.readlines()
    ologfile.close()
    for line in olog:
        lsf.write_output(line.strip(), logfile=lsf.logfile)
    os.system(f'rm {lsf.mc}/{admindir}/WMCstartup.ps1')
    os.system(f'mv {lsf.mc}/{admindir}/WMCstartup.log /tmp')

# BEGIN ODYSSEY RESET CODE
#
# Odyssey Variables
#

# LMC or WMC
if lsf.WMC:
    desktop = '/Users/Administrator/Desktop'
    ody_shortcut = 'Play VMware Odyssey.lnk'
    odyssey_app = 'odyssey-launcher.exe'
    # legacy most likely not needed
    # odysseyEXE = 'odyssey-launcher.exe'
    odyssey_dst = '/Users/Administrator'
elif lsf.LMC:
    desktop = '/home/holuser/Desktop'
    ody_shortcut = 'launch_odyssey.desktop'
    odyssey_app = 'odyssey-client-linux.AppImage'
    odyssey_launcher = 'odyssey-launch.sh'
    odyssey_dst = f'desktop-hol'
    lmcuser = f'holuser@mainconsole.{lsf.dom}'

# on initial boot remove the Odyssey files if present
if not lsf.labcheck:
    if os.path.isfile(f'{lsf.mc}/{desktop}/{ody_shortcut}'):
        lsf.write_output('Removing existing Odyssey desktop shortcut.', logfile=lsf.logfile)
        os.remove(f'{lsf.mc}/{desktop}/{ody_shortcut}')

    if os.path.isfile(f'{lsf.mc}/{odyssey_dst}/{odyssey_app}'):
        lsf.write_output(f'Removing existing Odyssey application. {lsf.mc}/{odyssey_dst}/{odyssey_app}', logfile=lsf.logfile)
        os.remove(f'{lsf.mc}/{odyssey_dst}/{odyssey_app}')

    # remove the file locally (shouldn't be here since /tmp gets deleted with each boot)
    if os.path.isfile(f'/tmp/{odyssey_app}'):
        lsf.write_output('Removing existing Odyssey application.', logfile=lsf.logfile)
        os.remove(f'/tmp/{odyssey_app}')

    # doubt this is needed but will include
    # we won't be able to do this. we can check but will need to run a command to remove (permissions)
    legacy_odyssey_client = '/wmchol/Users/Administrator/VMware_Odyssey.exe'
    if os.path.isfile(legacy_odyssey_client):
        lsf.write_output('Removing legacy Odyssey application.', logfile=lsf.logfile)
        os.remove(legacy_odyssey_client)

#
## End Core Team code
#

#        
# Insert your code here using the file in your vPod_repo
#

########################################################
#  Copy Labfiles folder to WMC
########################################################

labfilesSource = "/vpodrepo/2025-labs/2501/labfiles"
labfilesDestination = f"{lsf.mc}"

if lsf.WMC and os.path.exists(labfilesDestination) and os.path.exists(labfilesSource):
    try:
        hol.createFolder(f'{lsf.mc}', 'labfiles')
        
        lsf.write_output(f'2501: Copying lab files from {labfilesSource} to {labfilesDestination} folder.', logfile=lsf.logfile)
        print(f'2501: Copying lab files from {labfilesSource} to {labfilesDestination} folder.')
        os.system(f'cp -rfu {labfilesSource} {labfilesDestination}')
        lsf.write_output(f'2501: Copying lab files complete.', logfile=lsf.logfile)
        print(f'2501: Copying lab files complete.')
    except Exception as e:
        lsf.labfail(f'2501: {e}')
        exit(1)
else:
    lsf.labfail(f'2501: Cannot copy labfiles folder')
    exit(1)

########################################################
#  2501 - LabFiles Clean Up Script
########################################################

if lsf.WMC:
    try:
        if os.path.isfile(f'{labfilesDestination}/labfiles/cleanup.ps1'):
            lsf.write_output(f'2501: Running Labfiles cleanup.ps1 on WMC.', logfile=lsf.logfile)
            print(f'2501: Running C:\labfiles\cleanup.ps1 on WMC.')
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File c:\labfiles\cleanup.ps1"
            lsf.runwincmd(command,'mainconsole','Administrator', '{REPLACE_WITH_PASSWORD}')
        else:
            lsf.labfail(f'2501: File: c:\gitlab\cleanup.ps1 not found')
            print(f'2501: File: c:\gitlab\cleanup.ps1 not found')
            exit(1)

    except Exception as e:
        lsf.labfail(f'2501: {e}')
        print(f'2501: {e}')
        exit(1)


########################################################
#  2501 - Copy GitLab Projects files to WMC
########################################################
gitFqdn = "gitlab.vcf.sddc.lab"
gitlabRepoSource = "/vpodrepo/2025-labs/2501/gitlab"
gitlabRepoDestination = f"{lsf.mc}"
sslVerify = False

while True:
    if hol.isGitlabReady(gitFqdn, sslVerify) and hol.isGitlabLive(gitFqdn, sslVerify) and hol.isGitlabHealthy(gitFqdn, sslVerify):
        lsf.write_output(f'2501: Gitlab {gitFqdn} is in a Ready state!', logfile=lsf.logfile)
        print(f'2501: Gitlab {gitFqdn} is in a Ready state!')
        break
    else:
        print(f'2501: Gitlab {gitFqdn} is not Ready!')
        lsf.write_output(f'2501: Gitlab {gitFqdn} is not Ready!', logfile=lsf.logfile)
        lsf.labstartup_sleep(30)

if lsf.WMC and os.path.exists(gitlabRepoDestination) and os.path.exists(gitlabRepoSource):
    try:
        
        hol.createFolder(f'{lsf.mc}', 'gitlab')
        
        lsf.write_output(f'2501: Copying repo files from {gitlabRepoSource} to {gitlabRepoDestination} folder.', logfile=lsf.logfile)
        print(f'2501: Copying repo files from {gitlabRepoSource} to {gitlabRepoDestination} folder.')
        os.system(f'cp -rfu {gitlabRepoSource} {gitlabRepoDestination}')
        lsf.write_output(f'2501: Copying repo files complete.', logfile=lsf.logfile)
        print(f'2501: Copying repo files complete.')
    except Exception as e:
        lsf.labfail(f'2501: {e}')
        print(f'2501: {e}')
        exit(1)

########################################################
#  2501 - GitLab Clean Up Script
########################################################

if lsf.WMC:
    try:
        if os.path.isfile(f'{labfilesDestination}/gitlab/cleanup.ps1'):
            lsf.write_output(f'2501: Running Gitlab cleanup.ps1 on WMC.', logfile=lsf.logfile)
            print(f'2501: Running Gitlab cleanup.ps1 on WMC.')
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File c:\gitlab\cleanup.ps1"
            lsf.runwincmd(command,'mainconsole','Administrator', '{REPLACE_WITH_PASSWORD}')
        else:
            lsf.labfail(f'2501: File: c:\gitlab\cleanup.ps1 not found')
            print(f'2501: File: c:\gitlab\cleanup.ps1 not found')
            exit(1)

    except Exception as e:
        lsf.labfail(f'2501: {e}')
        print(f'2501: {e}')
        exit(1)

########################################################
#  2501 - Commit Gitlab Projects files to Gitlab
########################################################

if lsf.WMC:
    try:
        if os.path.isfile(f'{labfilesDestination}/gitlab/sync.ps1'):
            lsf.write_output(f'2501: Committing Repos to Gitlab.', logfile=lsf.logfile)
            print(f'2501: Committing Repos to Gitlab.')
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File c:\gitlab\sync.ps1"
            lsf.runwincmd(command,'mainconsole','Administrator', '{REPLACE_WITH_PASSWORD}')
        else:
            lsf.labfail(f'2501: Failed to commit Repos to Gitlab')
            print(f'2501: Failed to commit Repos to Gitlab')
            exit(1)

    except Exception as e:
        lsf.labfail(f'2501: {e}')
        print(f'2501: {e}')
        exit(1)
else:
    lsf.labfail(f'2501: Error committing repository files to Gitlab.')
    print(f'2501: Error committing repository files to Gitlab.')
    exit(1)



lsf.write_output(f'{sys.argv[0]} finished.', logfile=lsf.logfile) 
exit(0)

