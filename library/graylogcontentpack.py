#!/usr/bin/python
import base64
import httplib
import json

DOCUMENTATION = '''
---
module: graylogcontentpack
short_description: Adds a contentpack to graylog
description:
  - Adds a contentpack to graylog if one with the same name and category does not yet exist
options:
  srcjson:
    description:
      - The conentpack json.
    required: true
  user:
    description:
     - The username for authentication.
    required: true
    default: null
  password:
    description:
      - The password for authentication.
    required: true
    default: null
  host:
    description:
      - the IP of the graylog web server.
    required: false
    default: "127.0.0.1"
  port:
    description:
      - the port of the graylog web server.
    required: false
    default: 12900
  timeout:
    description:
      - the timeout for the api requests.
    required: false
    default: 10
author: "David Zuber (zuber.david@gmx.de)"
'''

EXAMPLES = '''
# Create a contentpack
- graylogcontentpack:
    srcjson: "{{lookup('file', playbook_dir + '/files/contentpacks/nginx.json')}}"
    host: "127.0.0.1"
    port: 12900
    user: 'admin'
    password: 'admin'
'''

RETURN = '''
contentpackid:
    description: Contentpackid of the created package
    returned: success
    type: string
    sample: "124afedec349779a"
name:
    description: The name of the created contentpack
    returned: success
    type: string
    sample: nginx
category:
    description: The category of the created contentpack
    returned: success
    type: string
    sample: Web Servers
status:
    description: the response status code of the rest api request
    returned: failure, when communicating with the rest api
    type: integer
    sample: 404
reason:
    description: The reason for the response
    returned: failure, when communicating with the rest api
    type: string
    sample: "Not found!"
sentbody:
    description: The body sent when creating the contentpack in the post request.
    returned: failure, when failing at creating the contentpack (not checking if it exists).
    type: string
    sample: {"id": null, "name": "nginx", "category": "Web Servers", ...}
body:
    description: The body from the response
    returned: failure, when communicating with the rest api
    type: string
    sample: "No Content"
'''

HEADERS = {'Content-type': 'application/json'}
APIENDPOINT = '/system/bundles'


def load_contentpack(module):
    js = json.loads(module.params['srcjson'])
    return js


def check_exists(module, conn, srcjson):
    srcname = srcjson['name']
    srccategory = srcjson['category']
    conn.request('GET', APIENDPOINT, headers=HEADERS)
    r = conn.getresponse()
    data = r.read()
    if r.status != 200:
        module.fail_json(msg="Failed to check contentpacks", status=r.status,
                         reason=r.reason, body=data)
    js = json.loads(data)
    for cp in js.get(srccategory, []):
        name = cp['name']
        if name == srcname:
            module.exit_json(changed=False, name=name, category=srccategory)


def create_contentpack(module, conn, srcjson):
    js = json.dumps(srcjson)
    conn.request('POST', APIENDPOINT, headers=HEADERS, body=js)
    r = conn.getresponse()
    data = r.read()
    if r.status != 201:
        module.fail_json(msg='Failed to create contentpack', status=r.status,
                         reason=r.reason, sentbody=js, body=data)
    locheader = r.getheader('Location')
    bundleid = locheader.rsplit('/', 1)[1]
    return bundleid


def setup_conentpack(module, conn, bundleid):
    conn.request('POST', APIENDPOINT + '/%s/apply' % bundleid, headers=HEADERS)
    r = conn.getresponse()
    data = r.read()
    if r.status != 204:
        module.fail_json(msg='Failed to apply contentpack', status=r.status, reason=r.reason,
                         body=data)


def main():
    module = AnsibleModule(
    argument_spec = dict(
        srcjson       = dict(required=True),
        user      = dict(required=True),
        password  = dict(required=True),
        host      = dict(default='127.0.0.1'),
        port      = dict(default=12900),
        timeout   = dict(default=10),
    ),
    supports_check_mode=True
    )
    host = module.params['host']
    port = module.params['port']
    authstring = '%s:%s' % (module.params['user'], module.params['password'])
    auth = base64.encodestring(authstring).replace('\n', '')
    HEADERS['Authorization'] = 'Basic %s' % auth

    conn = httplib.HTTPConnection(host, port)
    srcjson = load_contentpack(module)
    check_exists(module, conn, srcjson)
    if module.check_mode:
        module.exit_json(changed=True)
    bundleid = create_contentpack(module, conn, srcjson)
    setup_conentpack(module, conn, bundleid)
    module.exit_json(changed=True, name=srcjson['name'],
                     category=srcjson['category'], contentpackid=bundleid)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
