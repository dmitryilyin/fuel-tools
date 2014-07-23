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
        self.parser.add_argument("-d", "--debug", help="debug output",
                                 type=int, choices=[0, 1, 2, 3], default=0)
        self.parser.add_argument("-u", "--url", help="get stats from url",
                                 type=str)
        self.parser.add_argument("-s", "--socket",
                                 help="get stats from socket", type=str)
        self.parser.add_argument("-f", "--file", help="get stats from file",
                                 type=str)
        self.parser.add_argument("-y", "--yaml", help="output as YAML",
                                 action='store_true')
        self.args = self.parser.parse_args()

        self.color_on = Color(fgcode='green')
        self.color_off = Color(fgcode='red')
        self.color_title = Color(fgcode='blue')

        self.color_table = {
            'UP': self.color_on,
            'OPEN': self.color_on,
            'DOWN': self.color_off,
        }

    def debug(self, msg='', debug=1, offset=None):
        """
        Debug print string
        @param msg:
        @param debug:
        @param offset:
        """
        if not offset:
            offset = debug

        if self.args.debug >= debug:
            sys.stderr.write('  ' * offset + str(msg) + "\n")

    def puts(self, msg='', offset=0):
        """
        Print string
        @param msg:
        @param offset:
        """
        sys.stdout.write('  ' * offset + str(msg) + "\n")

    def output(self, msg=''):
        """
        Print string without newline
        @param msg:
        """
        sys.stdout.write(str(msg))

    def get_from_file(self, file):
        csv = open(file)
        data = csv.read()
        csv.close()
        return data

    def get_from_url(self, url):
        pass

    def get_from_socket(self, socket):
        pass

    def get_status(self):
        if self.args.file:
            self.csv = self.get_from_file(self.args.file)
        elif self.args.url:
            self.csv = self.get_from_url(self.args.url)
        else:
            self.csv = self.get_from_socket(self.args.socket)

        self.status = Status(self, self.csv)

    def color_string(self, string):
        if string in self.color_table:
            return self.color_table[string](string)
        else:
            return string

    def print_csv(self):
        self.puts(self.csv)

    def print_yaml(self):
        from yaml import dump
        self.puts(dump(self.status.data))

    def print_service_title(self, service_name, service_element):
        backend_element = service_element.get('BACKEND', {})
        backend_status = backend_element.get('status', '?')
        backend_status = self.color_string(backend_status)
        service_name = self.color_title(service_name)
        service_title = "%s (%s)" % (service_name, backend_status)
        self.puts(service_title)

    def print_servers_line(self, service_element):
        for server in sorted(service_element):
            if server in ['FRONTEND', 'BACKEND']:
                continue
            server_element = service_element[server]
            status = self.color_string(server_element['status'])
            check_status = self.color_string(server_element['check_status'])
            svname = server_element['svname']
            server_block = "%s (%s/%s) " % (svname, status, check_status)
            self.output(server_block)
        self.puts('')

    def result(self):
        if self.args.yaml:
            self.print_yaml()
            return
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
