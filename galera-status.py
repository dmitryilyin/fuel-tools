#!/usr/bin/env python

import MySQLdb
import os


class Galera:
    def __init__(self):
        self.cursor = None
        self.db = None
        self.data = {}
        self.auth_files = ['/etc/mysql/conf.d/password.cnf', '/root/.my.cnf']

    def connect(self):
        for possible_file in self.auth_files:
            if os.path.isfile(possible_file):
                self.db = MySQLdb.connect(host="localhost", db="mysql",read_default_file="/etc/mysql/conf.d/password.cnf")
                self.cursor = self.db.cursor()
                break

    def get_variables(self, query):
        if not self.cursor:
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

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

#data = {'wsrep_slave_threads': '2', 'wsrep_OSU_method': 'TOI', 'wsrep_node_address': '192.168.0.2', 'wsrep_provider_name': 'Galera', 'wsrep_connected': 'ON', 'wsrep_cert_deps_distance': '14.188782', 'wsrep_commit_oooe': '0.000000', 'wsrep_start_position': '00000000-0000-0000-0000-000000000000:-1', 'wsrep_local_cached_downto': '1', 'wsrep_local_state': '4', 'wsrep_sst_auth': '********', 'wsrep_cluster_conf_id': '3', 'wsrep_provider_version': '3.5(rXXXX)', 'wsrep_sst_receive_address': 'AUTO', 'wsrep_provider_options': 'base_host = 192.168.0.2; base_port = 4567; cert.log_conflicts = no; debug = no; evs.causal_keepalive_period = PT1S; evs.debug_log_mask = 0x1; evs.inactive_check_period = PT0.5S; evs.inactive_timeout = PT15S; evs.info_log_mask = 0; evs.install_timeout = PT15S; evs.join_retrans_period = PT1S; evs.keepalive_period = PT1S; evs.max_install_timeouts = 1; evs.send_window = 4; evs.stats_report_period = PT1M; evs.suspect_timeout = PT5S; evs.use_aggregate = true; evs.user_send_window = 2; evs.version = 0; evs.view_forget_timeout = P1D; gcache.dir = /var/lib/mysql/; gcache.keep_pages_size = 0; gcache.mem_size = 0; gcache.name = /var/lib/mysql//galera.cache; gcache.page_size = 128M; gcache.size = 128M; gcs.fc_debug = 0; gcs.fc_factor = 1.0; gcs.fc_limit = 16; gcs.fc_master_slave = no; gcs.max_packet_size = 64500; gcs.max_throttle = 0.25; gcs.recv_q_hard_limit = 9223372036854775807; gcs.recv_q_soft_limit = 0.25; gcs.sync_donor = no; gmcast.listen_addr = tcp://0.0.0.0:4567; gmcast.mcast_addr = ; gmcast.mcast_ttl = 1; gmcast.peer_timeout = PT3S; gmcast.segment = 0; gmcast.time_wait = PT5S; gmcast.version = 0; ist.recv_addr = 192.168.0.2; pc.announce_timeout = PT3S; pc.checksum = false; pc.ignore_quorum = false; pc.ignore_sb = false; pc.linger = PT20S; pc.npvo = false; pc.version = 0; pc.wait_prim = true; pc.wait_prim_timeout = P30S; pc.weight = 1; protonet.backend = asio; protonet.version = 0; repl.causal_read_timeout = PT30S; repl.commit_order = 3; repl.key_format = FLAT8; repl.max_ws_size = 2147483647; repl.proto_max = 5; socket.checksum = 2; ', 'wsrep_last_committed': '157552', 'wsrep_causal_reads': '0', 'wsrep_local_state_uuid': '040e8708-18a1-11e4-a9e1-474318f54076', 'wsrep_certify_nonPK': 'ON', 'wsrep_received_bytes': '176784', 'wsrep_repl_keys_bytes': '9387555', 'wsrep_flow_control_recv': '0', 'wsrep_protocol_version': '5', 'wsrep_local_state_comment': 'Synced', 'wsrep_node_incoming_address': 'AUTO', 'wsrep_cluster_address': 'gcomm://', 'wsrep_on': 'ON', 'wsrep_local_index': '0', 'wsrep_local_send_queue_avg': '0.000095', 'wsrep_repl_data_bytes': '54606418', 'wsrep_node_name': 'node-1.domain.tld', 'wsrep_local_recv_queue': '0', 'wsrep_auto_increment_control': 'ON', 'wsrep_cluster_status': 'Primary', 'wsrep_replicate_myisam': 'OFF', 'wsrep_cluster_size': '3', 'wsrep_replicated': '157178', 'wsrep_debug': 'OFF', 'wsrep_local_replays': '0', 'wsrep_convert_LOCK_to_trx': 'OFF', 'wsrep_local_recv_queue_avg': '0.001833', 'wsrep_incoming_addresses': '192.168.0.2:3307,192.168.0.3:3307,192.168.0.7:3307', 'wsrep_sst_method': 'mysqldump', 'wsrep_forced_binlog_format': 'NONE', 'wsrep_max_ws_size': '1073741824', 'wsrep_repl_keys': '721557', 'wsrep_ready': 'ON', 'wsrep_sst_donor_rejects_queries': 'OFF', 'wsrep_data_home_dir': '/var/lib/mysql/', 'wsrep_commit_window': '1.000413', 'wsrep_local_cert_failures': '0', 'wsrep_flow_control_paused_ns': '0', 'wsrep_cluster_state_uuid': '040e8708-18a1-11e4-a9e1-474318f54076', 'wsrep_received': '1637', 'wsrep_local_send_queue': '0', 'wsrep_replicated_bytes': '74053365', 'wsrep_cert_interval': '0.003980', 'wsrep_flow_control_paused': '0.000000', 'wsrep_local_commits': '156624', 'wsrep_cert_index_size': '43', 'wsrep_apply_oool': '0.000000', 'wsrep_cluster_name': 'openstack', 'wsrep_log_conflicts': 'OFF', 'wsrep_apply_window': '1.002221', 'wsrep_apply_oooe': '0.001847', 'wsrep_provider_vendor': 'Codership Oy <info@codership.com>', 'wsrep_repl_other_bytes': '0', 'wsrep_flow_control_sent': '0', 'wsrep_retry_autocommit': '1', 'wsrep_mysql_replication_bundle': '0', 'wsrep_drupal_282555_workaround': 'OFF', 'wsrep_max_ws_rows': '131072', 'wsrep_preordered': 'OFF', 'wsrep_load_data_splitting': 'ON', 'wsrep_recover': 'OFF', 'wsrep_local_bf_aborts': '0', 'wsrep_commit_oool': '0.000000', 'wsrep_desync': 'OFF', 'wsrep_provider': '/usr/lib64/galera/libgalera_smm.so'}


##############################################################################

if __name__ == '__main__':
    galera = Galera()
    galera.get_galera_data()
    data = galera.data
    print data
    print len(data)