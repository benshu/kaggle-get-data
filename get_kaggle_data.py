import urllib2
import requests
import re
import json

login_url = 'https://www.kaggle.com/account/login'

def get_page_source(url, session):
    source = session.get(url).text
    return source

def get_download_links(html_source):
    pattern = re.compile(ur'href="(.*download.*)" name.*\n')
    results = pattern.findall(html_source)
    for res in results:
        yield res

def filename_from_url(url):
    p = re.compile(ur'([^/\\&\?]+\.\w{2,3}(?=([\?&].*$|$)))')
    return re.search(p, url).group()

def download_files(links, session):
    for link in links:
        try:
            print 'Working on: ', link
            filename = filename_from_url(link)
            with open(filename, 'w') as f:
                f.write(get_page_source(link, session))
        except Exception as e:
            print "Exception trying to create files"
            print e

def login(username, password, session):
    session.get(login_url)
    payload = {'UserName': username,
            'Password': password,
            'JavaScriptEnabled': True}
    result = session.post(login_url,
            data = payload,
            headers = dict(referer=login_url))
    if result.status_code != 200:
        print "Login Failed"
    if result.text.contains('incorrect'):
        print "Login Failed, check credentials"
        exit(1)

def get_credentials():
    print 'Trying to load credentials from file...'
    import os
    if os.path.isfile('login.json'):
        creds = json.loads(open('login.json','r').read())
        return creds['username'], creds['password']
    else:
        print 'No login.json file found, please enter credentials'
        print 'kaggle.com username: '
        username = raw_input()
        from getpass import getpass
        password = getpass( 'kaggle.com password: ') 
        if query_yes_no('Would you like to store credentials for next use(will be store in plain text in login.json file):'):
            f = open('login.json','w')
            f.write(json.dumps({'username': username, 'password':password}))
            f.close()
        return username, password

def main():
    print "This script will download all the data links in a kaggle.com project data page"
    HOST = "https://www.kaggle.com"
    username , password = get_credentials()
    print "Enter the project name (example: titanic):"
    project = raw_input()
    URL = "https://www.kaggle.com/c/" + project + "/data"

    session = requests.session()
    login(username, password, session)
    source = get_page_source(URL, session)
    links = [ HOST + x for x in get_download_links(source) ]
    download_files(links, session)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    import sys
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
if __name__ == "__main__":
    main()