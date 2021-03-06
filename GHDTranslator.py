version_info='2.9.5 beta2'
update_info='20211120'
DEBUG=True

import os, sys, getopt, shutil, re, alive_progress, readchar
from alive_progress.utils.colors import * # MAGIC
# BLUE GREEN YELLOW RED MAGENTA CYAN ORANGE BOLD DIM IT(ALIC) UNDER(LINE)

# Formats
modetxt=lambda x:YELLOW('\n>>> '+x)
mode=lambda x:print(modetxt(x))
error=lambda x:print(RED('[error] '+x))
warning=lambda x:print(ORANGE('[warning] ')+x)
info=lambda x:print(CYAN('[info] ')+x)
ok=lambda x:print(GREEN('[ok] ')+x)
confirm=lambda x:input1(YELLOW('[confirm] ')+x+' [Y/n] ').upper()=='Y'
errorcmd=lambda x:{'':None}[(str(error(x))+str(print('\n'+help_text)))[:0]]
inputo=input
def input1(x=''):
    try:
        print(x,end='',flush=True)
        y=readchar.readchar().decode()
        print(y)
    except:
        y=''
    return y
def input(x=''):
    try:
        y=inputo(x) # Never interrupt this
    except:
        print('')
        y=''
    return y

# Texts
title_text='=== '+ORANGE('[GitHub Desktop Translator zh_CN] ')+ORANGE_IT('(ver '+version_info+')')+' ==='
version_text='\n'+'='*42+BOLD('\n GitHub Desktop translation '+version_info)+'''
   --by Zetaspace '''+update_info+f'''\n
 {CYAN("Link: GitHub.com/ZetaSp/GHDTranslator.py")}\n
 Thank you for using!\n'''+'='*42
help_text=BOLD(os.path.split(sys.argv[0])[1])+f''' {ITALIC("<options>")}
-y                Automatically finish everything
-d --dir {ITALIC("<dir>")}    Specify a target dir, app folder like \'app-'''+version_info.replace(' ','-')+'''\'
-r --restore      Restore from auto-backup file, using with --dir
-u --update       Check for updates from github (mirror fastgit)
-h --help         Show this message
-v --version      Show version info'''

# Check version code
try:
    if len(str(int(update_info)))!=8:raise ValueError
except:
    error("Version '"+update_info+"' is wrong. It should be a proper date.")
    sys.exit(999)

# Print title
print(title_text)

# Function
def check_update():
    try:
        print(YELLOW('>>> Check update'))
        # Not using GitHub API, because I'm always "rate limited"...
        # Using raw version.json instead.
        #api='https://raw.githubusercontent.com/ZetaSp/GHDTranslator.py/main/version.json'    
        # Githubusercontent.com is unreachable in China; using mirror fastgit.org.
        api='https://raw.fastgit.org/ZetaSp/GHDTranslator.py/main/version.json'

        with alive_progress.alive_bar(3, title=CYAN('[info] Connecting'), spinner='dots_waves', bar=None, enrich_print=False, stats=False, elapsed=False) as bar:
            bar()
            info('Current: ver '+version_info+' update '+update_info)
            import requests
            bar()
            try:
                req=requests.get(api,timeout=(2,2))
                bar()
            except:
                # Any connection error.
                bar()
                error('Connection failed. Please check it manually.')
                raise KeyboardInterrupt
            try:
                req=req.json()
                version=req['version']
                update=req['update']
                download=req['download']
                action=req['action']
            except:
                # Any parsing error.
                bar()
                error('Update data error.\nPlease check it manually.')
                sys.exit(1)
            info('Newest:  ver '+version+' update '+update+'\n')
            
        if update_info==update:
            ok('You are using the newest version!')
            sys.exit(0)
        else:
            # Different update
            try:
                diff=int(update)>int(update_info)
            except:
                # Not a number???
                warning(BOLD('LOWER VERSION')+'('+update+') available.')
                if confirm('Update?'):
                    ok('Sure.')
                else:
                    ok('Canceled.')
                    sys.exit(1)
            else:
                if diff:
                    # Larger update
                    ok('New version('+update+') available!')
                else:
                    # Smaller update?
                    warning(BOLD('LOWER VERSION')+'('+update+') available.')
                    if confirm('Update?'):
                        ok('Sure.')
                    else:
                        ok('Canceled.')
                        sys.exit(1)
            if action=='open':
                try:
                    import webbrowser
                    webbrowser.get()
                except:
                    # Web browser not available. Plz open manually.
                    info('Goto: '+BLUE_UNDER(download))
                else:
                    info('Opening: '+download)
                    webbrowser.open(download)
            sys.exit(1)
    except KeyboardInterrupt:
        print('')
        ok('Canceled.')
        sys.exit(1)

'=== Main ==='
# Get cmdline args
#if sys.argv[1:]==[]:sys.argv[1:]=['-h']
if sys.argv[-1]=='-d':sys.argv+=['""']
try:
    opts,args=getopt.getopt(sys.argv[1:],'hvyd:ru',['help','version','dir=','restore','update'])
except getopt.GetoptError:
    errorcmd('Unknown options: '+' '.join(sys.argv[1:])) # Unknown args
    sys.exit(1)

autopatch=False
restore=False
appdir=''
exist=os.path.exists
copy=shutil.copy2
for opt,arg in opts:
    if opt in ('-h','--help'):
        print(modetxt('Help\n')+help_text)
        sys.exit(0)
    elif opt in ('-v','--version'):
        print(modetxt('Version')+version_text)
        sys.exit(0)
    elif opt in ('-u','--update'):
        check_update()
        sys.exit(0)
    elif opt in ('-y'):
        autopatch=True
    elif opt in ('-r','--restore'):
        restore=True
    elif opt in ('-d','--dir'):
        appdir=arg
mode('Locate')
if not type(appdir)is str:
    error('Error dir: '+str(appdir)) # Not str
    sys.exit(0)
if appdir=='-y':
    appdir,autopatch='',True
if appdir!='':
    while(appdir[0]=="'"and appdir[-1]=="'")or(appdir[0]=='"'and appdir[-1]=='"'):
        appdir=appdir[1:-1]
        if appdir=='':break
if appdir=='':
    # Blank target dir
    while True:
        if sys.platform=='win32':PATH=';'
        elif sys.platform=='darwin' or sys.platform=='linux' or sys.platform=='cygwin':PATH=':'
        else:break
        PATH=re.split(PATH,os.getenv('PATH'))
        for i in PATH:
            if i=='':continue
            if(i[0]=="'"and i[-1]=="'")or(i[0]=='"'and i[-1]=='"'):i=i[1:-1]   # Cut ''
            if not exist(i):continue
            p=os.path.abspath(i)
            if 'github'in os.listdir(p):    # ...\GitHubDesktop\bin\github file
                appdir=os.path.abspath(os.path.join(p,'..'))
        if appdir!='':
            if(appdir[0]=="'"and appdir[-1]=="'")or(appdir[0]=='"'and appdir[-1]=='"'):appdir=appdir[1:-1] # Cut ''
            dirs=[]
            for i in os.listdir(appdir):
                if exist(os.path.abspath(os.path.join(appdir,i))+'\\resources\\app'):
                    dirs+=[i]
            appdir=os.path.abspath(os.path.join(appdir,sorted(dirs,reverse=True)[0]))
            del dirs
            info('Found GitHub Desktop in \''+appdir+'\'')
            if autopatch:break
            if confirm('Patch this one?'):
                break
        confirm
        appdir=input('Please type in your GitHub Desktop install path, like \'app-'+version_info.replace(' ','-')+'\' or \'GitHubDesktop\':\n> ')
        if appdir=='':error('Not typing.');sys.exit(0)
        break
if(appdir[0]=="'"and appdir[-1]=="'")or(appdir[0]=='"'and appdir[-1]=='"'):appdir=appdir[1:-1] # Cut ''
if not exist(appdir):
    error('Not exist: '+appdir)  # Target dir not exist
    sys.exit(0)
if not exist(os.path.abspath(appdir)+'\\resources\\app')and exist(appdir):
    dirs=[]
    for i in os.listdir(appdir):
        if exist(os.path.abspath(os.path.join(appdir,i))+'\\resources\\app'):
            dirs+=[i]
    else:
        error('No any GitHub Desktop here :(')  # Not exist target dir
        sys.exit(0)
    appdir=os.path.abspath(os.path.join(appdir,sorted(dirs,reverse=True)[0]))
    del dirs
if not exist(appdir):
    error('Not exist: '+appdir)  # Not exist target dir
    sys.exit(0)

# Basically Verified
appdir=os.path.abspath(appdir+'\\resources\\app')
resdir=os.path.abspath(os.getcwd())
jsdir0=appdir+'\\main.js'
jsdir1=appdir+'\\renderer.js'
jsdir0b=jsdir0+'.bak'
jsdir1b=jsdir1+'.bak'
extra=['\\static\\cherry-pick-intro.png']
if restore: # Restore
    mode('Restore')
    info('Source: '+appdir)
    info('Target: '+appdir)
    if not(exist(jsdir0b)and exist(jsdir1b)):
        print(error("Can't find js files to restore.")) # Not the right target dir
    else:
        # ===Verified, restore it===
        with alive_progress.alive_bar(3,title=CYAN('[info] Restoring'),spinner=None,enrich_print=False) as bar:
            bar()
            ok(os.path.split(jsdir0)[-1])
            copy(jsdir0b,jsdir0)
            bar()
            ok(os.path.split(jsdir1)[-1])
            copy(jsdir1b,jsdir1)
            bar()
            for f in extra:
                ok(f)
                copy(appdir+f+'.bak',appdir+f)
        ok('Restore finished.')
else:   # Patch
    mode('Patch')
    info('Source: '+resdir)
    info('Target: '+appdir)
    if not(exist(jsdir0)and exist(jsdir1)):
        print(error("Can't find js files to patch."))  # Not the right target dir
    else:
        if sum(map(lambda f:int(not exist(resdir+f)),extra))!=0:
            resdir=os.path.abspath(os.path.split(sys.argv[0])[0])   # Can't find in current dir,
        if sum(map(lambda f:int(not exist(resdir+f)),extra))!=0:    # Try py file dir
            error("Can't find extra resources.")    # Can't find resources
        else:
            # ===Verified, patch start===
            
            # Word replacing tool
            w=0
            def sub(mode):
                global w,js
                if mode=='':
                    return None
                elif mode[0]=='#':
                    return None
                elif mode=='mainjs':  # main.js
                    if DEBUG:info('[main.js]')
                    w=0
                elif mode=='renjs': # renderer.js
                    if DEBUG:info('[renderer.js]')
                    w=1
                elif '>'in mode:
                    m=mode.split('>')
                    n='>'.join(m[1:])
                    m=m[0]
                    #m,n=mode.split('>')
                    if'&'in m and m[0]!='!'and'&'not in n and m[0]!='^':
                        n+='(&'+m[m.index('&')+1].upper()+')'
                    if'...'in m and m[0]!='!'and m[0]!='^':
                        n+='...'
                    if'???'in m and m[0]!='!'and m[0]!='^':
                        n+='???'
                    if m[0]!='!'and m[0]!='^':
                        x=''
                        if m[0]=="'":
                            m=m[1:]
                            m="'"+m+"'"
                            n="'"+n+"'"
                        else:
                            m='"'+m+'"'
                            n='"'+n+'"'
                        nword=n
                    elif m[0]=='!':
                        x=m[0]
                        m=m[1:]
                        nword=n
                        n=eval(n)
                    else:
                        x=m[0]
                        m=m[1:]
                        nword=n
                    if x=='^'or(x!='!' and not('\\'in m or'*'in m or'?'in m)):
                        c=js[w].count(m)
                        if not c==0:
                            if DEBUG:info(m+CYAN(' ==> ')+n+CYAN(' ['+str(c)+']'))
                            js[w]=js[w].replace(m,n)
                        else:
                            if DEBUG:error(m+' ==> '+n+' ['+str(c)+']')
                            if DEBUG:error('^'*len('  '+m+' ==> '+n+' ['+str(c)+']'))
                    else:
                        c=len(re.findall(m,js[w]))
                        if not c==0:
                            if DEBUG:info('REGEX: '+m+CYAN(' ==> ')+nword+CYAN(' ['+str(c)+']'))
                            js[w]=re.sub(m,n,js[w])
                        else:
                            if DEBUG:error('REGEX: '+m+' ==> '+nword+' ['+str(c)+']')
                            if DEBUG:error('  '+'^'*len('  REGEX: '+m+' ==> '+nword+' ['+str(c)+']'))
                else:
                    return None

            # Translation
            a='''
mainjs
default branch>????????????

&File>??????
New &repository???>???????????????
Add &local repository???>?????????????????????
Clo&ne repository???>???????????????
&Options???>??????
E&xit>??????

&Edit>??????
&Undo>??????
&Redo>??????
Cu&t>??????
&Copy>??????
&Paste>??????
Select &all>??????
&Find>??????

&View>??????
&Changes>????????????
&History>????????????
Repository &list>???????????????
&Branches list>????????????
Go to &Summary>??????
#???????????????js?????????????????????
Sho&w stashed changes>????????????????????????
H&ide stashed changes>????????????????????????
Toggle &full screen>????????????
Reset zoom>????????????
Zoom in>??????
Zoom out>??????
&Reload>??????
&Toggle developer tools>??????????????????
P&ush>??????
Force P&ush???>????????????
Force P&ush>????????????

&Repository>?????????
Pu&ll>??????
&Remove???>??????
&Remove>??????
&View on GitHub>??? GitHub ?????????
!"O&pen in "(.*)"Command Prompt"\)>lambda x:'"??? "'+x.group(1)+'"???????????????")+" ?????????(&P)"'
renjs
Command Prompt>???????????????
mainjs
Show in E&xplorer>???????????????
!"&Open in "(.*)"external editor"\)>lambda x:'"??? "'+x.group(1)+'"???????????????")+" ?????????(&O)"'
renjs
Visual Studio Code>VS Code
Visual Studio Code (Insiders)>VS Code ?????????
IntelliJ IDEA Community Edition>IntelliJ IDEA ?????????
mainjs
Create &issue on GitHub>??? GitHub ???????????????
Repository &settings???>???????????????

&Branch>??????
New &branch???>??????
&Rename???>?????????
&Delete???>??????
Discard all changes???>??????????????????
&Stash all changes???>??????????????????
&Stash all changes>??????????????????
!"&Update from "[ ]?\+[ ]?p>'"??? " + p + " ??????"'
&Compare to branch>????????????
&Merge into current branch???>?????????????????????
Squas&h and merge into current branch???>???????????????????????????
R&ebase current branch???>???????????????????????????
Compare on &GitHub>??? &GitHub ?????????
Show &pull request>??????????????????
Create &pull request>??????????????????

&Help>??????
Report issue???>????????????
Failed opening issue creation page>??????????????????????????????
&Contact GitHub support???>?????? Github ??????
Failed opening contact support page>??????????????????????????????
Show User Guides>??????????????????
Failed opening user guides page>??????????????????????????????
Show keyboard shortcuts>??????????????????
Failed opening keyboard shortcuts page>?????????????????????????????????
S&how logs in Explorer>?????????????????????
Failed opening logs directory>???????????????????????????
&About GitHub Desktop>?????? GitHub Desktop

renjs
!"Press "(.*)" to exit fullscreen">lambda x:'"??? "'+x.group(1)+'" ????????????"'
^renderButton("minimize">renderButton("?????????"
^renderButton("maximize">renderButton("?????????"
^renderButton("restore">renderButton("??????"
^renderButton("close">renderButton("??????"

Ok>??????
Cancel>??????
Save>??????
Close>??????
Delete>??????
Continue>??????
Yes>???
No>???

Add co-authors>???????????????
Remove co-authors>???????????????

Name>??????
Email>??????
Other>??????
Sign in>??????
Sign out>??????
Learn more>????????????
Learn more.>????????????

Check for Updates>????????????
Quit and Install Update>?????????????????????
Unknown update status >??????????????????
Checking for updates???>??????????????????
Downloading update???>??????????????????
You have the latest version (last checked>?????????????????? (?????????
An update has been downloaded and is ready to be installed.>????????????????????????????????????
Couldn't determine the last time an update check was performed. You may be running an old version. Please try manually checking for updates and contact GitHub Support if the problem persists>??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????? GitHub ??????
release notes>????????????
Version >?????? 
Terms and Conditions>???????????????
License and Open Source Notices>?????????????????????

Options>??????
Accounts>??????
Sign in to your GitHub.com account to access your repositories.>????????? GitHub ?????????????????????????????????
If you have a GitHub Enterprise or AE account at work, sign in to it to get access to your repositories.>??????????????? GitHub ???????????? GitHub AE ??????????????????????????????????????????????????????
Unknown sign in type: >??????????????????:
Sign in using your browser>?????????????????????
Continue with browser>???????????????
To improve the security of your account, GitHub now requires you to sign in through your browser.>????????????????????????????????????????????????????????? GitHub???
Your browser will redirect you back to GitHub Desktop once you've signed in. If your browser asks for your permission to launch GitHub Desktop please allow it to.>???????????????????????????????????? GitHub Desktop??????????????????????????? GitHub Desktop ?????????????????????????????????
Enterprise address>????????????
Unable to authenticate with the GitHub Enterprise instance. Verify that the URL is correct, that your GitHub Enterprise instance is running version 2.8.0 or later, that you have an internet connection and try again.>GitHub ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????? ???2.8.0??????????????????????????????????????????????????????
Integrations>??????
Applications>????????????
External editor>???????????????
No editors found.>??????????????????
Install >?????? 
Shell>?????????
Git
?????? This email address doesn't match >?????? ?????????
, so your commits will be wrongly attributed.>?????????????????????????????????????????????
^`your ${this.props.accounts[0].endpoint===Wt()?"GitHub":"GitHub Enterprise"} account`>`?????? ${this.props.accounts[0].endpoint===Wt()?"GitHub ":"GitHub ?????????"}??????`
either of your GitHub.com nor GitHub Enterprise accounts>????????? GitHub ??????
Default branch name for new repositories>???????????????
Other???>??????
These preferences will edit your global Git config.>??????????????????????????? Git ??????
Appearance>??????
Light>??????
The default theme of GitHub Desktop>???????????????????????????
Dark>??????
GitHub Desktop is for you too, creatures of the night>???????????????????????????
High Contrast>????????????
Customizable High Contrast Theme>???????????????????????????
Customize:>?????????
Reset to High Contrast defaults>?????????????????????
!"background",[ ]?"Background">'"background","??????"'
!"border",[ ]?"Border">'"border","??????"'
!"text",[ ]?"Text">'"text","??????"'
!"activeItem",[ ]?"Active">'"activeItem","?????????"'
!"activeText",[ ]?"Active Text">'"activeText","????????????"'
System>??????
Automatically switch theme to match system theme.>???????????????????????????
Prompts>??????
^"Show a confirmation dialog before...">"?????????????????????"
Removing repositories>???????????????
Discarding changes>????????????
Force pushing>????????????
Advanced>??????
^"If I have changes and I switch branches...">"??????????????????????????????"
Ask me where I want the changes to go>??????????????????
Always bring my changes to my new branch>???????????????????????????
Always stash and leave my changes on the current branch>?????????????????????????????????????????????
Background updates>????????????
Periodically fetch and refresh status of all repositories>?????????????????????????????????????????????
Allows the display of up-to-date status indicators in the repository list. Disabling this may improve performance with many repositories.>?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
SSH
Use system OpenSSH (recommended)>???????????? OpenSSH (??????)
Usage>????????????
!"Help GitHub Desktop improve by submitting"(.*)"usage stats"\)>lambda x:'"????????????"'+x.group(1)+'"????????????????????????")," ??????????????? GitHub Desktop"'

'''.split('\n')
            while''in a:a.remove('')

            # Backup
            print(CYAN_IT('\n--Backup:'))
            x=sum(map(int,([not exist(jsdir0b),not exist(jsdir1b)]+list(map(lambda x:not exist(appdir+x+'.bak'),extra)))))
            with alive_progress.alive_bar(x,title=CYAN('[info] Backuping'),spinner=None,enrich_print=False) as bar:
                if not exist(jsdir0b):
                    copy(jsdir0,jsdir0b)
                    ok('\\main.js ==> bak')
                    bar()
                if not exist(jsdir1b):
                    copy(jsdir1,jsdir1b)
                    ok('\\renderer.js ==> bak')
                    bar()
                for f in extra:
                    if not exist(appdir+f+'.bak'):
                        copy(appdir+f,appdir+f+'.bak')
                        ok(f+' ==> bak')
                        bar()

            # Restore all
            print(CYAN_IT('\n--Restore:'))
            with alive_progress.alive_bar(len(extra)+2,title=CYAN('[info] Restoring'),spinner=None,enrich_print=False) as bar:
                copy(jsdir0b,jsdir0)
                ok('\\main.js <== bak')
                bar()
                copy(jsdir1b,jsdir1)
                ok('\\renderer.js <== bak')
                bar()
                for f in extra:
                    copy(appdir+f+'.bak',appdir+f)
                    ok(f+' <== bak')
                    bar()

            #  Copy extra files
            print(CYAN_IT('\n--Patch extra files:'))
            with alive_progress.alive_bar(len(extra),title=CYAN('[info] Copying  '),spinner=None,enrich_print=False) as bar:
                for f in extra:
                    bar()
                    copy(resdir+f,appdir+f)
                    ok(f+' <== Translated')
                
            #  Patch js
            print(CYAN_IT('\n--Patch js:'))
            with alive_progress.alive_bar(len(a)+2,title=CYAN('[info] Modifying'),spinner=None,enrich_print=False) as bar:
                js=['','']
                with open(jsdir0,'r',encoding='utf-8')as j:js[0]=j.read()
                with open(jsdir1,'r',encoding='utf-8')as j:js[1]=j.read()
                info('File loaded.')
                bar()
                for x in a:
                    sub(x)
                    bar()
                
                with open(jsdir0,'w',encoding='utf-8')as j:j.write(js[0])
                with open(jsdir1,'w',encoding='utf-8')as j:j.write(js[1])
                info('File written.')
                bar()

            print()
            ok('Done.')
            sys.exit(0)

# EOF
sys.exit(0)
