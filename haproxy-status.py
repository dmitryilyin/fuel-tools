#!/usr/bin/env python
import sys
import argparse
from color import Color


class Interface:
    """
    Functions related to input, output and formatting of data
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-d", "--debug", help="debug output", type=int, choices=[0, 1, 2, 3], default=0)
        self.parser.add_argument("-u", "--url", help="get stats from url", type=str)
        self.parser.add_argument("-s", "--socket", help="get stats from socket", type=str)
        self.parser.add_argument("-f", "--file", help="get stats from file", type=str)
        self.parser.add_argument("-y", "--yaml", help="output as YAML", action='store_true')
        self.parser.add_argument("-c", "--csv", help="output as CSV", action='store_true')
        self.parser.add_argument("-j", "--json", help="output as JSON", action='store_true')
        self.args = self.parser.parse_args()

        self.color_on = Color(foreground='green')
        self.color_off = Color(foreground='red')
        self.color_title = Color(foreground='blue')

        self.color_table = {
            'UP': self.color_on,
            'OPEN': self.color_on,
            'DOWN': self.color_off,
        }

        if not (self.args.file or self.args.url or self.args.socket):
            self.args.socket = '/var/lib/haproxy/stats'

    def debug(self, msg='', debug=1, offset=None):
        """
        Debug print string
        @param msg: Message to write
        @param debug: Minimum debug level this message should be shown
        @param offset: Number of spaces before the message
        """
        if not offset:
            offset = debug

        if self.args.debug >= debug:
            sys.stderr.write('  ' * offset + str(msg) + "\n")

    def puts(self, msg='', offset=0):
        """
        Print a string
        @param msg: String to print
        @param offset: Number of spaces before the string
        """
        sys.stdout.write('  ' * offset + str(msg) + "\n")

    def output(self, msg=''):
        """
        Print string without newline at the end
        @param msg: String to print
        """
        sys.stdout.write(str(msg))

    def get_from_file(self):
        """
        Read stats csv data from a file
        """
        csv = open(self.args.file)
        data = csv.read()
        csv.close()
        if data:
            return data
        else:
            raise StandardError('Could not get data from file')

    def get_from_url(self):
        """
        Downalod stats csv data from haproxy's status url
        """
        import urllib2
        response = urllib2.urlopen(self.args.url)
        data = response.read()
        if data:
            return data
        else:
            raise StandardError('Could not get data from URL')

    def get_from_socket(self):
        """
        Get status csv data from haproxy's control socket
        """
        import socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.args.socket)
        message = "show stat\n"
        buffer_size = 32
        sock.sendall(message)
        data = ''
        buf = sock.recv(buffer_size)
        while buf:
            data += buf
            buf = sock.recv(buffer_size)
        if data:
            return data
        else:
            raise StandardError('Could not get CSV from socket')

    def get_status(self):
        """
        Get status date using one of methods
        """
        if self.args.file:
            self.csv = self.get_from_file()
        elif self.args.url:
            self.csv = self.get_from_url()
        else:
            self.csv = self.get_from_socket()

        if not self.csv:
            raise StandardError('There is no CSV')
        else:
            self.status = Status(self, self.csv)

    def status_color(self, status, string=None):
        """
        Colorize a string according to status
        @param status: Strtun string
        @param string: Message string
        @return: Colored string
        """
        if not string:
            string = status
        if status in self.color_table:
            return self.color_table[status](string)
        else:
            return string

    def print_csv(self):
        """
        Returns raw csv
        @return: CSV string
        """
        self.puts(self.csv)

    def print_yaml(self):
        """
        Print YAML formated data
        @return: YAML string
        """
        from yaml import dump
        self.puts(dump(self.status.data))

    def print_json(self):
        """
        Print JSON formated data
        @return: JSON string
        """
        from json import dumps
        self.puts(dumps(self.status.data))

    def print_service_title(self, service_name, service_element):
        """
        Print a line description of a service
        @param service_name: String name of the service
        @param service_element: Service structure
        """
        backend_element = service_element.get('BACKEND', {})
        frontend_element = service_element.get('FRONTEND', {})
        service_status = backend_element.get('status', None)
        if not service_status:
            service_status = frontend_element.get('status', '?')
        service_name = self.status_color(service_status, service_name)
        scur = frontend_element.get('scur', 0)
        rate = frontend_element.get('rate', 0)
        service_title = "* %s %s (%s:%s)" % (service_name, service_status, scur, rate)
        self.puts(service_title)

    def print_servers_line(self, service_element):
        """
        Print servers description block
        @param service_element: Service data structure
        """
        for server in sorted(service_element):
            if server in ['FRONTEND', 'BACKEND']:
                continue
            server_element = service_element.get(server)
            status = server_element.get('status')
            check_status = server_element.get('check_status')
            scur = server_element.get('scur', 0)
            rate = server_element.get('rate', 0)
            svname = self.status_color(status, server_element['svname'])
            server_block = "  %s %s %s (%s:%s)" % (svname, status, check_status, scur, rate)
            self.output(server_block)
        self.puts('')

    def result(self):
        """
        Output human-readable results
        """
        if self.args.yaml:
            self.print_yaml()
        elif self.args.csv:
            self.print_csv()
        elif self.args.json:
            self.print_json()
        else:
            for service in sorted(self.status.data):
                service_element = self.status.data[service]
                self.print_service_title(service, service_element)
                self.print_servers_line(service_element)


class Status:
    """
    HAproxy status structure
    """

    def __init__(self, interface, csv):
        self.csv = csv
        self.interface = interface

        self.status_fields = {
            'pxname': {
                'number': 0,
                'title': 'pxname',
            },
            'svname': {
                'number': 1,
                'title': 'svname',
            },
            'qcur': {
                'number': 2,
                'title': 'qcur',
            },
            'qmax': {
                'number': 3,
                'title': 'qmax',
            },
            'scur': {
                'number': 4,
                'title': 'scur',
            },
            'smax': {
                'number': 5,
                'title': 'smax',
            },
            'slim': {
                'number': 6,
                'title': 'slim',
            },
            'stot': {
                'number': 7,
                'title': 'stot',
            },
            'bin': {
                'number': 8,
                'title': 'bin',
            },
            'bout': {
                'number': 9,
                'title': 'bout',
            },
            'dreq': {
                'number': 10,
                'title': 'dreq',
            },
            'dresp': {
                'number': 11,
                'title': 'dresp',
            },
            'ereq': {
                'number': 12,
                'title': 'ereq',
            },
            'econ': {
                'number': 13,
                'title': 'econ',
            },
            'eresp': {
                'number': 14,
                'title': 'eresp',
            },
            'wretr': {
                'number': 15,
                'title': 'wretr',
            },
            'wredis': {
                'number': 16,
                'title': 'wredis',
            },
            'status': {
                'number': 17,
                'title': 'status',
            },
            'weight': {
                'number': 18,
                'title': 'weight',
            },
            'act': {
                'number': 19,
                'title': 'act',
            },
            'bck': {
                'number': 20,
                'title': 'bck',
            },
            'chkfail': {
                'number': 21,
                'title': 'chkfail',
            },
            'chkdown': {
                'number': 22,
                'title': 'chkdown',
            },
            'lastchg': {
                'number': 23,
                'title': 'lastchg',
            },
            'downtime': {
                'number': 24,
                'title': 'downtime',
            },
            'qlimit': {
                'number': 25,
                'title': 'qlimit',
            },
            'pid': {
                'number': 26,
                'title': 'pid',
            },
            'iid': {
                'number': 27,
                'title': 'iid',
            },
            'sid': {
                'number': 28,
                'title': 'sid',
            },
            'throttle': {
                'number': 29,
                'title': 'throttle',
            },
            'lbtot': {
                'number': 30,
                'title': 'lbtot',
            },
            'tracked': {
                'number': 31,
                'title': 'tracked',
            },
            'type': {
                'number': 32,
                'title': 'type',
            },
            'rate': {
                'number': 33,
                'title': 'rate',
            },
            'rate_lim': {
                'number': 34,
                'title': 'rate_lim',
            },
            'rate_max': {
                'number': 35,
                'title': 'rate_max',
            },
            'check_status': {
                'number': 36,
                'title': 'check_status',
            },
            'check_code': {
                'number': 37,
                'title': 'check_code',
            },
            'check_duration': {
                'number': 38,
                'title': 'check_duration',
            },
            'hrsp_1xx': {
                'number': 39,
                'title': 'hrsp_1xx',
            },
            'hrsp_2xx': {
                'number': 40,
                'title': 'hrsp_2xx',
            },
            'hrsp_3xx': {
                'number': 41,
                'title': 'hrsp_3xx',
            },
            'hrsp_4xx': {
                'number': 42,
                'title': 'hrsp_4xx',
            },
            'hrsp_5xx': {
                'number': 43,
                'title': 'hrsp_5xx',
            },
            'hrsp_other': {
                'number': 44,
                'title': 'hrsp_other',
            },
            'hanafail': {
                'number': 45,
                'title': 'hanafail',
            },
            'req_rate': {
                'number': 46,
                'title': 'req_rate',
            },
            'req_rate_max': {
                'number': 47,
                'title': 'req_rate_max',
            },
            'req_tot': {
                'number': 48,
                'title': 'req_tot',
            },
            'cli_abrt': {
                'number': 49,
                'title': 'cli_abrt',
            },
            'srv_abrt': {
                'number': 50,
                'title': 'srv_abrt',
            },
        }
        self.parse_csv()

    def parse_csv(self):
        """
        Parse CSV data into status structure
        """
        self.data = {}
        csv_lines = self.csv.split("\n")

        for csv_line in csv_lines:
            if csv_line.startswith('#'):
                continue
            if csv_line.startswith('pxname'):
                continue

            csv_fields = csv_line.split(',')

            if len(csv_fields) < len(self.status_fields):
                continue

            service_field = self.status_fields['pxname']
            server_field = self.status_fields['svname']

            for status_field_name in self.status_fields:
                status_field = self.status_fields[status_field_name]
                status_field_number = status_field['number']

                service_field_value = csv_fields[service_field['number']]
                server_field_value = csv_fields[server_field['number']]

                if service_field_value not in self.data:
                    self.data[service_field_value] = {}

                if server_field_value not in self.data[service_field_value]:
                    self.data[service_field_value][server_field_value] = {}

                csv_field_value = csv_fields[status_field_number]

                server = self.data[service_field_value][server_field_value]
                server[status_field_name] = csv_field_value


##############################################################################

if __name__ == '__main__':
    interface = Interface()
    interface.get_status()
    interface.result()
