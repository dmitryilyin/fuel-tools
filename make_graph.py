#!/usr/bin/env python

DEPLOYMENT_CURRENT = """
- id: netconfig
  type: puppet
  groups: [primary-controller, controller, cinder, compute, ceph-osd, zabbix-server, primary-mongo, mongo]
  required_for: [deploy]
  requires: [hiera]
  parameters:
    puppet_manifest: /etc/puppet/modules/osnailyfacter/modular/netconfig.pp
    puppet_modules: /etc/puppet/modules
    timeout: 3600

- id: tools
  type: puppet
  groups: [primary-controller, controller, cinder, compute, ceph-osd, zabbix-server, primary-mongo, mongo]
  required_for: [deploy]
  requires: [hiera]
  parameters:
    puppet_manifest: /etc/puppet/modules/osnailyfacter/modular/tools.pp
    puppet_modules: /etc/puppet/modules
    timeout: 3600

- id: hosts
  type: puppet
  groups: [primary-controller, controller, cinder, compute, ceph-osd, zabbix-server, primary-mongo, mongo]
  required_for: [deploy]
  requires: [netconfig]
  parameters:
    puppet_manifest: /etc/puppet/modules/osnailyfacter/modular/hosts.pp
    puppet_modules: /etc/puppet/modules
    timeout: 3600

- id: firewall
  type: puppet
  groups: [primary-controller, controller, cinder, compute, ceph-osd, zabbix-server, primary-mongo, mongo]
  required_for: [deploy]
  requires: [netconfig]
  parameters:
    puppet_manifest: /etc/puppet/modules/osnailyfacter/modular/firewall.pp
    puppet_modules: /etc/puppet/modules
    timeout: 3600

- id: hiera
  type: puppet
  role: [primary-controller, controller, cinder, compute, ceph-osd, zabbix-server, primary-mongo, mongo]
  required_for: [deploy]
  parameters:
    puppet_manifest: /etc/puppet/modules/osnailyfacter/modular/hiera.pp
    puppet_modules: /etc/puppet/modules
    timeout: 3600
"""

import yaml
import pygraphviz as pgv


class MakeGraph:
    def __init__(self):
        self._data = {}
        self._workbook = []
        self._graph = None
        self.new_graph()

    options = {
        'debug': False,
        'prog': 'dot',
        'role_node': {
            'shape': 'rectangle',
            'fillcolor': 'deepskyblue',
        },
        'task_node': {
            'shape': 'ellipse',
            'fillcolor': 'yellow',
        },
        'default_edge': {
        },
        'edge_task_to_role': {
        },
        'edge_role_to_role': {
        },
        'edge_to_stage': {
            'style': 'invis',
            'dir': 'none',
        },
        'global_graph': {
            'overlap': 'false',
            'splines': 'polyline',
            'pack': 'true',
            'sep': '1,1',
            'esep': '0.8,0.8',
        },
        'global_node': {
            'style': 'filled',
        },
        'global_edge': {
            'style': 'solid',
            'arrowhead': 'vee',
        }
    }

    def debug_print(self, msg):
        if self.options.get('debug', False):
            print msg

    def new_graph(self):
        self._graph = pgv.AGraph(strict=False, directed=True)

    # graph functions

    def graph_node(self, id, options=None):
        if not options:
            options = {}
        for option, value in self.node_options(id).iteritems():
            if option not in options:
                options[option] = value
        self.debug_print("Node: %s (%s)" % (id, repr(options)))
        if not self.graph.has_node(id):
            self.graph.add_node(id)
        node = self.graph.get_node(id)
        for attr_name, attr_value in options.iteritems():
            node.attr[attr_name] = attr_value
        return node

    def graph_edge(self, from_node, to_node, options=None):
        if not options:
            options = {}
        for option, value in self.edge_options(from_node, to_node).iteritems():
            if option not in options:
                options[option] = value
        self.debug_print("Edge: %s -> %s (%s)" % (from_node, to_node, repr(options)))
        if not self.graph.has_edge(from_node, to_node):
            self.graph.add_edge(from_node, to_node)
        edge = self.graph.get_edge(from_node, to_node)
        for attr_name in options:
            edge.attr[attr_name] = options[attr_name]
        return edge

    def edge_options(self, from_node, to_node):
        from_type = self.data[from_node]['type']
        to_type = self.data[to_node]['type']
        if to_type == 'stage':
            return self.options['edge_to_stage']
        elif to_type == 'role':
            if from_type == 'role':
                return self.options['edge_role_to_role']
            else:
                return self.options['edge_task_to_role']
        else:
            return self.options['default_edge']

    def node_options(self, node):
        node_type = self.node_type(node)
        if node_type == 'role':
            return self.options['role_node']
        else:
            return self.options['task_node']

    # data functions

    # convert array data to hash data
    def convert_data(self):
        # form the initial data structure
        for node in self.workbook:
            if not type(node) is dict:
                continue
            if not node.get('type', None) and node.get('id', None):
                continue
            id = node.get('id', None)
            node_type = node.get('type', None)
            requires = node.get('requires', [])
            required_for = node.get('required_for', [])
            role = node.get('role', [])
            self._data[id] = {
                'id': id,
                'requires': requires,
                'required_for': required_for + role,
                'type': node_type,
            }

        # clen the data dictionary
        cleaned_data = {}
        for node in self.data.iterkeys():
            # filter out stage nodes
            if self.node_type(node) == 'stage':
                continue

            # node structure
            id = self.data[node].get('id', None)
            node_type = self.data[node].get('type', None)
            cleaned_data[node] = {
                'id': id,
                'type': node_type,
                'links': [],
            }

        # convert links
        for node in cleaned_data:
            required_for = self.data[node]['required_for']
            requires = self.data[node]['requires']

            # cross-join requires and requires_for
            for reqf in required_for:
                if reqf in cleaned_data:
                    cleaned_data[node]['links'].append(reqf)
            for req in requires:
                if req in cleaned_data:
                    cleaned_data[req]['links'].append(node)

        # clean links
        for node in cleaned_data:
            links = cleaned_data[node]['links']
            filtered_links = []

            # find if there are some links to tasks
            has_task_links = False
            for link in links:
                if self.node_type(link) != 'role':
                    has_task_links = True

            # keep links to roles only if there are no links to tasks
            for link in links:
                if has_task_links and self.node_type(link) == 'role':
                    continue
                filtered_links.append(link)

            cleaned_data[node]['links'] = filtered_links

        # save cleaned data to the object
        self._data = cleaned_data
        return self._data

    # build graph structure using data
    def build_graph(self):
        self.convert_data()
        for id, node in self.data.iteritems():
            self.graph_node(id)
            for link in node['links']:
                self.graph_edge(id, link)

    def node_exists(self, node):
        return node in self.data

    def node_type(self, node):
        if not self.node_exists(node):
            return None
        return self.data[node]['type']

    # IO functions

    def load_data(self, workbook):
        self._workbook = workbook

    def load_yaml(self, yaml_workbook):
        self._workbook = yaml.load(yaml_workbook)

    def write_dot(self, dot_file):
        self.graph.write(dot_file)

    def write_image(self, img_file):
        for attr_name in self.options['global_graph']:
            self.graph.graph_attr[attr_name] = self.options['global_graph'][attr_name]
        for attr_name in self.options['global_node']:
            self.graph.node_attr[attr_name] = self.options['global_node'][attr_name]
        for attr_name in self.options['global_edge']:
            self.graph.edge_attr[attr_name] = self.options['global_edge'][attr_name]
        self.graph.layout(prog=self.options['prog'])
        self.graph.draw(img_file)

    @property
    def workbook(self):
        return self._workbook

    @property
    def data(self):
        return self._data

    @property
    def graph(self):
        return self._graph


mg = MakeGraph()
mg.options['debug'] = True
mg.load_yaml(DEPLOYMENT_CURRENT)
mg.build_graph()
mg.write_dot('graph.dot')
mg.write_image('graph.png')


