#!/usr/bin/env python3

import datetime
import json
import os
import pathlib
import requests


def log(message):
    t = datetime.datetime.utcnow().replace(microsecond=0)
    print('{} {}'.format(t, message))


def swag_code_box(user, code):
    url = 'http://www.swagbucks.com/'
    params = {'cmd': 'sb-gimme-jx'}
    data = {'hdnCmd': 'sb-gimme', 'pcode': code}
    cookies = {'__urqm': user.get('urqm')}
    r = requests.post(url, params=params, data=data, cookies=cookies)
    return r.json()[0]


def mobile_app(user, code):
    url = 'http://swagbucks.com/'
    params = {'cmd': 'apm-11'}
    data = {'appid': '6', 'pcode': code, 'sig': user.get('sig')}
    cookies = {'__urqm': user.get('urqm')}
    r = requests.post(url, params=params, data=data, cookies=cookies)
    return r.json()['message']


def main():
    log('Starting up.')
    conf = {}
    home = pathlib.Path(os.environ.get('HOME')).resolve()
    conf_file = home / '.config/swagbucks/sbcodes.json'
    if not conf_file.parent.exists():
        conf_file.parent.mkdir(parents=True)
    if conf_file.exists():
        with conf_file.open() as f:
            conf = json.load(f)

    c = requests.get('http://sbcodez.com/')
    _, _, code = c.text.partition('<span class="code">')
    code, _, _ = code.partition('</span>')
    code = code.strip()

    if code == conf.get('last_code'):
        log('I already submitted the code {!r}.'.format(code))
    else:
        for name, user in conf.get('users', {}).items():
            response = swag_code_box(user, code)
            log('{}: {!r}: {}'.format(name, code, response))
            if 'Mobile App' in response:
                response = mobile_app(user, code)
                log('{}: {!r}: {}'.format(name, code, response))
        conf['last_code'] = code

    with conf_file.open('w') as f:
        json.dump(conf, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
