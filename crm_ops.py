#!/usr/bin/env python
import sys
import argparse
import time
from cib import CIB
from color import Color


class Interface:
    """
    Funcions related to input, output and formattiong of data
    """

    def __init__(self):
        self.error_color = Color(foreground='red')
        self.running_color = Color(foreground='green', bright_foreground=True)
        self.not_running_color = Color(foreground=5, attribute=0, enabled=True, bright_foreground=True, bright_background=False)
        self.debug_color = Color(foreground=6, background=5, attribute=1, enabled=True, bright_foreground=False, bright_background=False)
        self.title_color = Color(foreground='blue')

        self.ocf_rc_codes = {
            '0': self.running_color('Success'),
            '1': self.error_color('Error: Generic'),
            '2': self.error_color('Error: Arguments'),
            '3': self.error_color('Error: Unimplemented'),
            '4': self.error_color('Error: Permissions'),
            '5': self.error_color('Error: Installation'),
            '6': self.error_color('Error: Configuration'),
            '7': self.not_running_color('Not Running'),
            '8': self.running_color('Master Running'),
            '9': self.error_color('Master Failed'),
        }

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-d", "--debug", help="debug output", type=int, choices=[0, 1, 2, 3], default=0)
        self.parser.add_argument("-v", "--verbose", help="show more information (timings)", action='store_true')
        self.parser.add_argument("-n", "--node", help="filter by node name", type=str)
        self.parser.add_argument("-p", "--primitive", help="filter by primitive name", type=str)
        self.parser.add_argument("-f", "--file", help="read CIB from file instead of Pacemaker", type=str)
        self.parser.add_argument("-y", "--yaml", help="output as YAML", action='store_true')
        self.parser.add_argument("-j", "--json", help="output as JSON", action='store_true')
        self.args = self.parser.parse_args()

    def create_cib(self):
        """
        Creates a CIB instance either from file or from Pacemaker
        """
        self.cib = CIB(self)
        if self.args.file:
            self.cib.get_cib_from_file(self.args.file)
        else:
            self.cib.get_cib_from_pacemaker()

    def show_cib_nodes(self):
        """
        Print out parsed CIB nodes data
        """
        self.puts(self.cib.show_nodes())

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

    def rc_code_to_string(self, rc_code):
        """
        Convert rc_code number to human-readable string
        @param rc_code: Return code (one digit)
        @return: Colored operation status string
        """
        rc_code = str(rc_code)
        if rc_code in self.ocf_rc_codes:
            return self.ocf_rc_codes[rc_code]
        else:
            return self.error_color('Unknown!')

    def status_color(self, status, line):
        """
        Colorize a line according to the resource status
        @param status: Resource status string
        @param line: A line to be colorized
        @return: Colorized line
        """
        status = str(status)
        line = str(line)
        if status in ['promote', 'start']:
            return self.running_color(line)
        if status in ['stop']:
            return self.not_running_color(line)
        else:
            return self.title_color(line)

    def print_resource(self, resource, offset=4):
        """
        Print resource description block
        @param resource: Resource structure
        @param offset: Number of spaces before the block
        """
        resource = resource.copy()
        resource['id'] = self.status_color(resource['status'], resource['id'])
        resource['status-string'] = self.status_color(resource['status'], resource['status'].title())
        line = "> %(id)s (%(class)s::%(provider)s::%(type)s) %(status-string)s" % resource
        self.puts(line, offset)

    def seconds_to_time(self, seconds_from, seconds_to=None, msec=False):
        """
        Convert two timestampt to human-readable time delta between them
        @param seconds_from: timestamp to count from
        @param seconds_to: timestamp to coumt to (default: now)
        @param msec: input is in miliseconds instead of seconds
        @return: String of time delta
        """
        seconds_in_day = 86400
        seconds_in_hour = 3600
        seconds_in_minute = 60
        miliseconds_in_second = 1000

        try:
            if seconds_to is None:
                seconds_to = time.time()
            elif msec:
                seconds_to = float(seconds_to) / miliseconds_in_second
            else:
                seconds_to = float(seconds_to)

            if msec:
                seconds_from = float(seconds_from) / miliseconds_in_second
            else:
                seconds_from = float(seconds_from)

        except TypeError:
            return '?'

        seconds = abs(seconds_to - seconds_from)

        if seconds > seconds_in_day:
            days = int(seconds / seconds_in_day)
            seconds -= seconds_in_day * days
        else:
            days = 0

        if seconds > seconds_in_hour:
            hours = int(seconds / seconds_in_hour)
            seconds -= seconds_in_hour * hours
        else:
            hours = 0

        if seconds > seconds_in_minute:
            minutes = int(seconds / seconds_in_minute)
            seconds -= seconds_in_minute * minutes
        else:
            minutes = 0

        seconds, miliseconds = int(seconds), int((seconds - int(seconds)) * miliseconds_in_second)

        return_string = []

        if days > 0:
            return_string.append(str(days) + 'd')

        if hours > 0:
            return_string.append(str(hours) + 'h')

        if minutes > 0:
            return_string.append(str(minutes) + 'm')

        # show at least seconds even if all is zero
        if seconds > 0 or miliseconds == 0:
            return_string.append(str(seconds) + 's')

        # who cares about miliseconds when we are talking about minutes
        if miliseconds > 0 and minutes == 0:
            return_string.append(str(miliseconds) + 'ms')

        return ':'.join(return_string)

    def print_op(self, op, offset=8):
        """
        Print operation description block
        @param op: Operation structure
        @param offset: Number of spaces before the string
        """
        op = op.copy()
        self.debug(str(op), 3)
        op['rc-code-string'] = self.rc_code_to_string(op.get('rc-code', None))

        if 'interval' in op:
            op['interval-string'] = self.seconds_to_time(op['interval'], 0, msec=True)

        if ('interval' in op) and (op['interval'] != '0'):
            op['operation-string'] = '%s (%s)' % (op['operation'], op['interval-string'])
        else:
            op['operation-string'] = op['operation']

        line = '* %(operation-string)s %(rc-code-string)s' % op
        self.puts(line, offset)

        if self.args.verbose:
            # calculate and show timings
            if 'exec-time' in op:
                op['exec-time-sec'] = self.seconds_to_time(op['exec-time'], 0, msec=True)

            if 'last-run' in op:
                op['last-run-sec'] = self.seconds_to_time(op['last-run'])

            if 'last-rc-change' in op:
                op['last-rc-change-sec'] = self.seconds_to_time(op['last-rc-change'])

            line = ''
            #
            # if 'crm-debug-origin' in op:
            #     line += 'Origin: %(crm-debug-origin)s' % op

            if 'last-run-sec' in op:
                line += ' LastRun: %(last-run-sec)s' % op

            if 'last-rc-change-sec' in op:
                line += ' LastChange: %(last-rc-change-sec)s' % op

            if 'exec-time-sec' in op:
                line += ' ExecTime: %(exec-time-sec)s' % op
            #
            # if 'interval-string' in op:
            #     line += ' Interval: %(interval-string)s' % op

            self.puts(line, offset + 2)

    def print_node(self, node):
        """
        Print node description block
        @param node: Node structure
        """
        line = '%s\n%s\n%s' % (40 * '=', node['id'], 40 * '=')
        self.puts(line)

    def print_yaml(self):
        """
        Print YAML formated data
        @return: YAML string
        """
        from yaml import dump
        self.puts(dump(self.cib.nodes))

    def print_json(self):
        """
        Print JSON formated data
        @return: JSON string
        """
        from json import dumps
        self.puts(dumps(self.cib.nodes))

    def print_table(self):
        """
        Print the entire output table
        """
        if self.args.yaml:
            self.print_yaml()
        elif self.args.json:
            self.print_json()
        else:
            for node_id, node_data in sorted(self.cib.nodes.items()):
                if self.args.node:
                    if node_id != self.args.node:
                        continue
                self.print_node(node_data)
                for resource_id, resource_data in sorted(node_data['resources'].items()):
                    if self.args.primitive:
                        if resource_id != self.args.primitive:
                            continue
                    self.print_resource(resource_data)
                    for op in resource_data['ops']:
                        self.print_op(op)

###########################################################################################################

if __name__ == '__main__':
    interface = Interface()
    interface.create_cib()
    interface.cib.decode_lrm()
    interface.print_table()
