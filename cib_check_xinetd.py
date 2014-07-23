#!/usr/bin/env python
import sys
import platform
from cib import CIB

resource = 'p_haproxy'
hostname = 'node-1.domain.tld'
use_xml = True


class Xinetd_interface:
    def __init__(self, resource, hostname=None, use_xml=False):
        self.hostname = hostname
        self.resource = resource
        self.use_xml = use_xml

        if not self.hostname:
            self.hostname = platform.node()

        if not self.hostname:
            self.send_data(400, 'No hostname set')

        if not self.resource:
            self.send_data(400, 'No resource set')

        self.create_cib()
        self.cib.decode_lrm()

        if not self.hostname in self.cib.nodes:
            self.send_data(404, 'Node "%s" was not found' % self.hostname)
        node = self.cib.nodes[self.hostname]

        if not self.resource in node['resources']:
            self.send_data(404, 'Resource "%s" was not found on node "%s"' % (self.resource, self.hostname))

        resource = node['resources'][self.resource]
        ops = resource['ops']

        status = self.cib.determine_resource_status(ops)

        if status in ['start', 'promote']:
            code = 200
        else:
            code = 503

        self.send_data(code, 'Resource "%s" on node "%s" has status "%s"' % (self.resource, self.hostname, status))

    def send_data(self, code='200', msg='OK', body=None):
        if not body:
            body = msg
        data = ''
        data += "HTTP/1.1 %d %s\r\n" % (code, msg)
        data += "Content-type: text/html\r\n"
        data += "Connection: close\r\n"
        data += "\r\n"
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
            self.send_data(500, 'Could not get CIB', str(e))

    def debug(self, msg='', debug=1, offset=None):
        pass

###########################################################################################################

if __name__ == '__main__':
    interface = Xinetd_interface(hostname=hostname, resource=resource, use_xml=use_xml)
