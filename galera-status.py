#!/usr/bin/env python

import MySQLdb
import os
import sys
import argparse
from color import Color


class Galera:
    def __init__(self):
        self.cursor = None
        self.db = None
        self.data = {}
        self.auth_files = ['/etc/mysql/conf.d/password.cnf', '/root/.my.cnf']
        self.connect_host = 'localhost'
        self.connect_db = 'mysql'

    def connect(self):
        for possible_file in self.auth_files:
            if os.path.isfile(possible_file):
                self.db = MySQLdb.connect(
                    host=self.connect_host,
                    db=self.connect_db,
                    read_default_file=possible_file,
                )
                self.cursor = self.db.cursor()
                break
        if not (self.db and self.cursor):
            raise StandardError('Could not connect to the database!')

    def get_variables(self, query):
        if not (self.db and self.cursor):
            self.connect()
        self.cursor.execute(query)
        for row in self.cursor:
            key, value = row
            if key and value:
                self.data[key] = value

    def get_galera_data(self):
        self.connect()
        self.get_variables("show variables like 'wsrep_%'")
        self.get_variables("show status like 'wsrep_%'")
        self.close()
        if len(self.data) == 0:
            raise StandardError('There is no Galera data!')

    def load_from_yaml(self, yaml_data):
        from yaml import load
        stream = open(yaml_data, 'r')
        self.data = load(stream)
        if (type(self.data) is not dict) or (len(self.data) == 0):
            raise StandardError('There is no Galera data!')

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()


class Interface:
    """
    Functions related to input, output and formatting of data
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-d", "--debug", help="debug output", type=int, choices=[0, 1, 2, 3], default=0)
        self.parser.add_argument("-f", "--file", help="get data from YAML file", type=str)
        self.parser.add_argument("-y", "--yaml", help="output as YAML", action='store_true')
        self.parser.add_argument("-j", "--json", help="output as JSON", action='store_true')
        self.args = self.parser.parse_args()

        self.color_good = Color(foreground='green')
        self.color_progress = Color(foreground='yellow')
        self.color_bad = Color(foreground='red')
        self.color_info = Color(foreground='blue')
        self.align = Color(align='right')

        self.galera = Galera()
        if self.args.file:
            self.galera.load_from_yaml(self.args.file)
        else:
            self.galera.get_galera_data()

        self.result()

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

    def print_yaml(self):
        """
        Print YAML formated data
        @return: YAML string
        """
        from yaml import dump
        self.puts(dump(self.galera.data))

    def print_json(self):
        """
        Print JSON formated data
        @return: JSON string
        """
        from json import dumps
        self.puts(dumps(self.galera.data))

    def result(self):
        if self.args.yaml:
            self.print_yaml()
        elif self.args.json:
            self.print_json()
        else:
            self.print_report()

    def print_report(self):
        from jinja2 import Environment
        env = Environment()
        env.filters['color_info'] = self.color_info
        env.filters['color_bad'] = self.color_bad
        env.filters['color_good'] = self.color_good
        env.filters['color_progress'] = self.color_progress
        env.filters['align'] = self.align

        report = """
Cluster: {{ wsrep_cluster_name|default('?')|color_info }} Size: {{ wsrep_cluster_size|default('?')|color_info }} Status: {{ wsrep_cluster_status }}

Replication: {{ wsrep_on|align(3) }} Debug: {{ wsrep_debug|align(3) }}
Connected:   {{ wsrep_connected|align(3) }}
Ready:       {{ wsrep_ready|align(3) }}

        """.strip()

        template = env.from_string(report)
        self.puts(template.render(self.galera.data))


##############################################################################

if __name__ == '__main__':
    interface = Interface()
