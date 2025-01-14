import subprocess
import base64
from avrs.cfg import *
from avrs.race_cloud_util import *
from avrs.race_cloud_cfg_util import *
from avrs.util import *
from avrs.requests.request import AvrsApiRequest
from argparse import RawTextHelpFormatter

class AvrsRaceCloud(AvrsApiRequest):
    def __init__(self, parser, cfg):
        self.cfg = cfg
        race_cloud_parser = parser.add_parser(
            'race-cloud', 
            help='cloud racing\n\n')

        sps = race_cloud_parser.add_subparsers(required=True, help='race-cloud options')

        connect_parser = sps.add_parser(
            'connect',
            help='connect to an instance for cloud racing')
        connect_parser.add_argument(
            'sim_index',
            type = int,
            choices = [0, 1, 2, 3, 4, 5],
            help='the index of the simulator instance to connect to')
        connect_parser.add_argument(
            'team_name',
            help='the name of the team to race under')
        connect_parser.add_argument(
            'vehicle_config',
            help='the path the vehicle configuration file to use when racing')
        connect_parser.add_argument(
            '--instance-id',
            default = '',
            help='can be used directly instead of instance name if needed')
        connect_parser.add_argument(
            '--no-check-cans',
            action='store_true',
            help='if set, vcan interfaces will not be checked for validity')
        connect_parser.add_argument(
            '--print-debug',
            action='store_true',
            help='if set, debug information will be printed')
        connect_parser.set_defaults(func=self.race_connect)

        rx_connect_parser = sps.add_parser(
            'rx-connection',
            help='execute steps to receive a connection (only relevant to sim-side)')
        rx_connect_parser.add_argument(
            'team_name',
            help='the name of the connecting team')
        rx_connect_parser.add_argument(
            'ip',
            help='the ip address of the incoming connection')
        rx_connect_parser.add_argument(
            'cfg_data',
            help='the incoming vehicle configuration data')
        rx_connect_parser.set_defaults(func=self.rx_connect)

        sim_ctrl_parser = sps.add_parser(
            'sim-ctrl',
            help='control the sim program (start, stop, restart, reset)')
        sim_ctrl_parser.add_argument(
            'sim_index',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the index of the simulator instance to apply the action')
        sim_ctrl_parser.add_argument(
            'action',
            choices=['start', 'stop', 'restart', 'reset-connection'],
            help='what action to apply to the simulator program')
        sim_ctrl_parser.add_argument(
            '--local',
            action='store_true',
            help='if set, this command will run on this system locally (not for use from dev instances)')
        sim_ctrl_parser.add_argument(
            '--instance-id',
            default = '',
            help='can be used directly instead of sim index if needed')
        sim_ctrl_parser.add_argument(
            '--clear-autospawns',
            action='store_true',
            help='can be used with the reset-connection action to clear sim autospawn config')
        sim_ctrl_parser.set_defaults(func=self.sim_ctrl)

        reset_qos_parser = sps.add_parser(
            'reset-qos',
            help='reset the qos file on this system')
        reset_qos_parser.set_defaults(func=self.reset_qos)

        enable_peer_qos_parser = sps.add_parser(
            'enable-peer-qos',
            help='enable a peer in this systems qos file')
        enable_peer_qos_parser.add_argument(
            'peer_id',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the id of the peer to enable')
        enable_peer_qos_parser.add_argument(
            'ip',
            help='the ip address to add to the qos file')
        enable_peer_qos_parser.set_defaults(func=self.enable_peer_qos)

        disable_peer_qos_parser = sps.add_parser(
            'disable-peer-qos',
            help='disable a peer in this systems qos file')
        disable_peer_qos_parser.add_argument(
            'peer_id',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the id of the peer to enable')
        disable_peer_qos_parser.set_defaults(func=self.disable_peer_qos)


    def race_connect(self, args):
        print('connecting to race with team name: {}'.format(args.team_name))

        # validate / load vehicle config

        vcfg_ok, vcfg_data, bsu_vcan, kistler_vcan, badenia_vcan = prepare_vehicle_cfg(args.vehicle_config)

        if not vcfg_ok:
            print('error reading config file: {}'.format(vcfg_data))
            return

        vcan_ok = True
        if not check_vcan_exists(bsu_vcan) and not args.no_check_cans:
            print('bsu vcan {} does not appear to exist'.format(bsu_vcan))
            vcan_ok = False
        if not check_vcan_exists(kistler_vcan) and not args.no_check_cans:
            print('kistler vcan {} does not appear to exist'.format(kistler_vcan))
            vcan_ok = False
        if not check_vcan_exists(badenia_vcan) and not args.no_check_cans:
            print('badenia vcan {} does not appear to exist'.format(badenia_vcan))
            vcan_ok = False

        if not vcan_ok:
            return

        # make api call to begin connection
        our_ip = get_local_instance_ip()

        connection_request = {
            'action': 'connect',
            'sim_index': args.sim_index,
            'ip_to_reserve': our_ip,
            'team_name': args.team_name,
            'sim_id_override': args.instance_id,
            'ensure_instance_is_running': False,
            'config_data': vcfg_data
        }

        ok, response = call_race_cloud_api(connection_request)
        if not ok:
            print('connect api error: {}'.format(response))

        ok, rbody, sim_ip = get_api_script_response(response)
        if not ok:
            print(rbody)
            return

        if args.print_debug:
            print(rbody)
        #print(sim_ip)

        slot_info = {}
        for k, v in rbody.items():
            #print('out: {}'.format(v['stdout']))
            #print('err: {}'.format(v['stderr']))
            slot_info = json.loads(v['stdout'])

        if not slot_info['ok']:
            print('issue reserving slot: {}'.format(slot_info['msg']))
            return

        sim_slot = slot_info['slot']

        # enable first peer since this is on a client (only will ever have 1, the sim)
        enable_peer_qos(sim_slot, sim_ip)

        # will need to get port from received slot id to connect peer vcans
        connect_peer_vcan(sim_slot, sim_ip, 0, bsu_vcan)
        connect_peer_vcan(sim_slot, sim_ip, 1, kistler_vcan)
        connect_peer_vcan(sim_slot, sim_ip, 2, badenia_vcan)

        # configure the CLI to communicate with the cloud sim instance
        self.cfg['sim_address'] = sim_ip
        save_cfg('avrs', self.cfg)

        print('connection success with team name {} and slot id {}'.format(args.team_name, sim_slot))

    # this should only run on sim instances (not dev instances)
    def rx_connect(self, args):
        ok, msg, slot = try_get_open_slot(args.team_name, args.ip)

        bsu_vcan = get_auto_vcan_name(slot, 0)
        kistler_vcan = get_auto_vcan_name(slot, 1)
        badenia_vcan = get_auto_vcan_name(slot, 2)

        # get CAN names from this
        register_received_vehicle(
            args.team_name, slot, args.cfg_data, bsu_vcan, kistler_vcan, badenia_vcan)

        vcan_ok = True
        vcan_msg = ''
        if not check_vcan_exists(bsu_vcan):
            vcan_msg = 'bsu vcan {} does not appear to exist'.format(bsu_vcan)
            vcan_ok = False
        if not check_vcan_exists(kistler_vcan):
            vcan_msg = 'kistler vcan {} does not appear to exist'.format(kistler_vcan)
            vcan_ok = False
        if not check_vcan_exists(badenia_vcan):
            vcan_msg = 'badenia vcan {} does not appear to exist'.format(badenia_vcan)
            vcan_ok = False

        if not vcan_ok:
            print(json.dumps({
                'ok': vcan_ok,
                'msg': vcan_msg,
                'slot': -1
                }))
            return

        if ok:
            enable_peer_qos(slot, args.ip)
            connect_peer_vcan(slot, args.ip, 0)
            connect_peer_vcan(slot, args.ip, 1)
            connect_peer_vcan(slot, args.ip, 2)

        response = {
            'ok': ok,
            'msg': msg,
            'slot': slot
        }

        print(json.dumps(response)) # print this so that when called from the ssh lambda we can get the result

    def sim_ctrl(self, args):
        if args.local:
            self.local_sim_ctrl(args)
        else:
            self.remote_sim_ctrl(args)

    def local_sim_ctrl(self, args):
        if args.action == 'reset-connection':
            print('resetting race cloud connection')
            print('resetting qos file, removing CAN lock files, stopping all cannelloni instances')
            reset_race_cloud_connection()
            if args.clear_autospawns:
                clear_autospawns()
        if args.action == 'stop' or args.action == 'restart':
            print('stopping sim program on sim instance {}'.format(args.sim_index))
            bash_kill_process('Autoverse')
        if args.action == 'start' or args.action == 'restart':
            print('starting sim program on sim instance {}'.format(args.sim_index))
            exe_path = os.path.join(get_sim_exe_path())
            start_exe(exe_path)

    def remote_sim_ctrl(self, args):

        # go ahead and reset local connection as well
        if args.action == 'reset-connection':
            reset_race_cloud_connection()

        our_ip = get_local_instance_ip()

        reset_request = {
            'action': args.action,
            'sim_index': args.sim_index,
            'ip_to_reserve': our_ip,
            'sim_id_override': args.instance_id,
            'ensure_instance_is_running': False
        }

        ok, response = call_race_cloud_api(reset_request)
        #print(response)
        if not ok:
            print(response)
            return

        ok, rbody, sim_ip = get_api_script_response(response)
        if not ok:
            print(rbody)
            return

        for k, v in rbody.items():
            print(v['stdout'])

    def reset_qos(self, args):
        print('resetting qos file')
        reset_rmw_qos()

    def enable_peer_qos(self, args):
        print('enabling peer qos for id {} using ip address {}'.format(
            args.peer_id, args.ip))
        enable_peer_qos(args.peer_id, args.ip)

    def disable_peer_qos(self, args):
        print('disabling peer qos for id {}'.format(args.peer_id))
        disable_peer_qos(args.peer_id)