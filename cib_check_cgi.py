#!/usr/bin/env python
import cgi
import cgitb
import sys
import platform
from cib import CIB
cgitb.enable()


class CGI_interface:
    def __init__(self):
        self.request = cgi.FieldStorage()
        self.hostname = self.request.getfirst('hostname', None)
        self.resource = self.request.getfirst('resource', None)

        if self.request.getfirst('xml', False):
            self.use_xml = True
        else:
            self.use_xml = False

        if not self.hostname:
            self.hostname = platform.node()

        if not self.hostname:
            self.send_cgi(400, 'No hostname sent')

        if not self.resource:
            self.send_cgi(400, 'No resource sent')

        self.create_cib()
        self.cib.decode_lrm()

        if not self.hostname in self.cib.nodes:
            self.send_cgi(404, 'Node "%s" was not found' % self.hostname)
        node = self.cib.nodes[self.hostname]

        if not self.resource in node['resources']:
            self.send_cgi(404, 'Resource "%s" was not found on node "%s"' % (self.resource, self.hostname))

        resource = node['resources'][self.resource]
        ops = resource['ops']

        status = self.cib.determine_resource_status(ops)

        if status in ['start', 'promote']:
            code = 200
        else:
            code = 503

        self.send_cgi(code, 'Resource "%s" on node "%s" has status "%s"' % (self.resource, self.hostname, status))

    def send_cgi(self, code='200', msg='OK', body=None):
        if not body:
            body = msg
        data = ''
        data += "Status: %d %s\r\n" % (code, msg)
        data += "Content-type:text/html\r\n\r\n"
        data += "<html>%s</html>\r\n" % body
        sys.stdout.write(data)
        sys.exit(0)

    def create_cib(self):
        try:
            self.cib = CIB(self)
            if self.use_xml:
                self.cib.get_cib_from_file('samples/cib.xml')
            else:
                self.cib.get_cib_from_pacemaker()
        except Exception as e:
            self.send_cgi(500, 'Could not get CIB', str(e))

    def debug(self, msg='', debug=1, offset=None):
        pass

###########################################################################################################

if __name__ == '__main__':
    interface = CGI_interface()
