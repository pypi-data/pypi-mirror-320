import os
import json
import base64

from avrs.simconfig_util import *

def get_payload(cfg_object, payload_name):
	for p in cfg_object['payloads']:
		if p['typeName'] == payload_name:
			return p
	return None

def clear_autospawns():
	# also need to edit the yas_marina_env.json to have autospawn for this config
	sim_path = os.environ.get('AVRS_INSTALL_PATH', 
		os.path.join(os.environ['HOME'], 'autoverse-linux'))
	sim_saved = os.path.join(sim_path, 'Linux', 'Autoverse', 'Saved')
	cfg_files = SimConfigFiles(sim_saved)

	cfg_ok, msg = cfg_files.validate()
	if not cfg_ok:
		print(msg)
		return

	cfg_files.files['yas']['autoSpawnObjects'] = []
	cfg_files.files['main']['objectTemplatePaths'] = []
	cfg_files.save()

def register_received_vehicle(team_name, slot, cfg_data, bsu_vcan, kistler_vcan, badenia_vcan):
	cfg_string = base64.b64decode(cfg_data)
	cfg_object = json.loads(cfg_string.decode('utf-8'))

	# ensure perception is disabled
	eav24 = get_payload(cfg_object, 'Eav24Initializer')
	if eav24 is None:
		return (False, 'no eav24 payload found')

	eav24['body']['bLidarEnabled'] = False
	eav24['body']['bCameraEnabled'] = False
	eav24['body']['bRadarEnabled'] = False
	eav24['body']['bPublishGroundTruth'] = False
	eav24['body']['bPublishInputs'] = False
	eav24['body']['bsuCanName'] = bsu_vcan
	eav24['body']['kistlerCanName'] = kistler_vcan
	eav24['body']['badeniaCanName'] = badenia_vcan

	# do not allow default object name (collision)
	if cfg_object['name'] == 'eav24':
		cfg_object['name'] = team_name
	cfg_object['specName'] = 'eav24_{}'.format(team_name)

	# also need to edit the yas_marina_env.json to have autospawn for this config
	sim_path = os.environ.get('AVRS_INSTALL_PATH', 
		os.path.join(os.environ['HOME'], 'autoverse-linux'))
	sim_saved = os.path.join(sim_path, 'Linux', 'Autoverse', 'Saved')
	cfg_files = SimConfigFiles(sim_saved)

	cfg_ok, msg = cfg_files.validate()
	if not cfg_ok:
		print(msg)
		return

	start_landmark = 'MvStart{}'.format(slot)

	entry_exists = False
	for i in cfg_files.files['yas']['autoSpawnObjects']:
		if 'objectSpec' in i and i['objectSpec'] == cfg_object['specName']:
			entry_exists = True

	if not entry_exists:
		cfg_files.files['yas']['autoSpawnObjects'].append({
				'bShouldSpawn': True,
				'objectType': 'Eav24',
				'objectSpec': cfg_object['specName'],
				'bSpawnAtLandmark': True,
				'spawnLandmarkName': start_landmark
			})

	# also need to add the object template to main sim config

	new_cfg_name = 'eav24_{}.json'.format(team_name)
	cfg_files.files['main']['objectTemplatePaths'].append(os.path.join('Objects', new_cfg_name))
	cfg_files.save()

	target_path = os.path.join(sim_saved, 'Objects', new_cfg_name)
	with open(target_path, 'w', encoding='utf-8') as f:
		json.dump(cfg_object, f, ensure_ascii=False, indent=4)

def prepare_vehicle_cfg(cfg_path):

	#print('preparing config for transmission: {}'.format(cfg_path))

	if not os.path.isfile(cfg_path):
		return (False, '{} is not a valid file'.format(cfg_path), None, None, None)

	cfg_object = {}
	with open(cfg_path, 'r', encoding='utf-8') as f:
		cfg_object = json.load(f)


	# obtain desired CAN names to start cannelloni
	eav24 = get_payload(cfg_object, 'Eav24Initializer')
	if eav24 is None:
		return (False, 'no eav24 payload found', None, None, None)

	bsu_vcan = eav24['body']['bsuCanName']
	kistler_vcan = eav24['body']['kistlerCanName']
	badenia_vcan = eav24['body']['badeniaCanName']

	cfg_data = base64.b64encode(json.dumps(cfg_object).encode('utf-8')).decode('utf-8')
	return (True, cfg_data, bsu_vcan, kistler_vcan, badenia_vcan)

