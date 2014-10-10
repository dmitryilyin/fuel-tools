import yaml
import pprint


class PuppetReport:
    __report = None

    def __init__(self, report_file):
        self.load_file(report_file)

    def construct_ruby_object(self, loader, suffix, node):
        return loader.construct_yaml_map(node)

    def construct_ruby_sym(self, loader, node):
        return loader.construct_yaml_str(node)

    def extend_yaml(self):
        yaml.add_multi_constructor(u"!ruby/object:", self.construct_ruby_object)
        yaml.add_constructor(u"!ruby/sym", self.construct_ruby_sym)

    def load_file(self, report_file):
        try:
            f = open(report_file, 'r')
            raw_report = f.read()
            f.close()
        except IOError:
            raw_report = None

        if raw_report:
            self.extend_yaml()
            self.__report = yaml.load(raw_report)

    def filter_useless_resources(self, resource_title):
        if resource_title.startswith('Schedule'):
            return False
        if resource_title.startswith('Filebucket'):
            return False
        return True

    def report(self):
        return self.__report

    def resource_statuses(self):
        resource_statuses = self.report().get('resource_statuses', {})
        filtered_statuses = {}
        for title, params in resource_statuses.iteritems():
            if self.filter_useless_resources(title):
                filtered_statuses[title] = params
        return filtered_statuses

    def show_resources(self):
        for title, params in self.resource_statuses().iteritems():
            eval_time = params.get('evaluation_time', 0)
            failed = params.get('failed')
            print '%s -> %s sec, failed: %s' % (title, eval_time, failed)

    def show_deployment_status(self):
        status = self.report().get('status', None)
        events = self.report().get('metrics', {}).get('events', {}).get('values', {})
        print "Deployment: " + str(status)
        for event in events:
            print event[1], event[2]


pr = PuppetReport('samples/puppet_report.yaml')
pr.show_deployment_status()
pr.show_resources()

