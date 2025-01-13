# aMotion
Adapter for managing the connection, control and monitoring of the HVAC aMotion family family

## Install:

```
python3 -m pip install amotion
```

## Usage examples:

### Initiate library:
```
from amotion import aMotionConnector

amotion = aMotionConnector("username", "password", "192.168.0.1:8080")

```

### Compose parts or entities:

You need the device description. Response is a aMotionDescription object

```
from amotion import aMotionConnector
import asyncio
from pprint import pprint

amotion = aMotionConnector("username", "password", "192.168.0.1:8080")


async def main():
    result = await amotion.description()
    pprint(vars(result))


asyncio.run(main())
```

Properties:

        device_name = "Amotion Device"        device name
        device_type = "aMotion"             device type
        board_type = "Unknown"              board type (aM-CL, aM-CE, aM-GB etc)
        production_number = "Unknown"       factory ident
        brand = "Unknown"                   commerce brand
        requests = list[str]                list of the params for the control unit
        unit = list[str]                    list of the monitoring params 
        types = {}                          deep description of the params
        control = {}                        type, range and units of the control params
        sensors = {}                        description of the monitoring params (for the HA sensors)
        scenes = []                         scene is a device preset
        functions = []                      function is a unit trigger controller

This is a complete description to compose all relevant entity. You get somethink like 

```
{'board_type': 'CL',
 'brand': 'amotion.eu',
 'control': {'fan_power_req': {'max': 100.0,
                               'min': 0.0,
                               'name': 'fan_power_req',
                               'step': 1,
                               'type': 'range',
                               'unit': '%',
                               'valueType': 'percent'},
             'temp_request': {'max': 40.0,
                              'min': 10.0,
                              'name': 'temp_request',
                              'step': 0.5,
                              'type': 'range',
                              'unit': '°C',
                              'valueType': 't_control'},
             'work_regime': {'name': 'work_regime',
                             'type': 'enum',
                             'unit': 'enum',
                             'valueType': 'WorkRegime',
                             'values': ['OFF',
                                        'AUTO',
                                        'VENTILATION',
                                        'NIGHT_PRECOOLING']}},
 'device_name': 'Office',
 'device_type': 'DUPLEX 570 EC5',
 'functions': [{'enabled': False, 'id': 4, 'name': 'test RS', 'triggerId': []}],
 'production_number': '355183014',
 'requests': ['work_regime', 'fan_power_req', 'temp_request'],
 'scenes': [{'author': 'admin',
             'created': 1649922877,
             'icon': 'Turbo',
             'id': 3,
             'items': [{'operation': '=',
                        'value': 'VENTILATION',
                        'variable': 'work_regime'},
                       {'operation': '=',
                        'value': '75',
                        'variable': 'fan_power_req'},
                       {'operation': '=',
                        'value': '18',
                        'variable': 'temp_request'}],
             'lastModification': 1696322349,
             'name': 'Provoz 75/18',
             'purpose': 'USER',
             'visible': True},
            {'author': 'admin',
             'created': 1654475509,
             'icon': 'Fireplace',
             'id': 6,
             'items': [{'operation': '=',
                        'value': 'AUTO',
                        'variable': 'work_regime'},
                       {'operation': '=',
                        'value': '36.0',
                        'variable': 'fan_power_req'}],
             'lastModification': 1697449467,
             'name': 'automat',
             'purpose': 'USER',
             'visible': True},
            {'author': '!servis',
             'created': 1665641378,
             'icon': 'Fan',
             'id': 7,
             'items': [{'operation': '=',
                        'value': 'OFF',
                        'variable': 'work_regime'},
                       {'operation': '=',
                        'value': '0',
                        'variable': 'fan_power_req'}],
             'lastModification': 1697456918,
             'name': 'Vypnuto',
             'purpose': 'USER',
             'visible': True},
            {'author': 'admin',
             'created': 946840038,
             'icon': 'Fan',
             'id': 8,
             'items': [{'operation': '=',
                        'value': 'VENTILATION',
                        'variable': 'work_regime'},
                       {'operation': '>',
                        'value': '65',
                        'variable': 'fan_power_req'},
                       {'operation': '=',
                        'value': '18',
                        'variable': 'temp_request'}],
             'lastModification': 1696485908,
             'name': 'Provoz 65/18_D',
             'purpose': 'USER',
             'visible': True},
            {'author': 'admin',
             'created': 1696485927,
             'icon': 'Fan',
             'id': 9,
             'items': [{'operation': '=',
                        'value': 'VENTILATION',
                        'variable': 'work_regime'},
                       {'operation': '>',
                        'value': '65',
                        'variable': 'fan_power_req'},
                       {'operation': '=',
                        'value': '18',
                        'variable': 'temp_request'}],
             'lastModification': 1696485937,
             'name': 'Provoz 65/18_H',
             'purpose': 'USER',
             'visible': True}],
 'sensors': {'fan_eta_factor': {'max': 100.0,
                                'min': 0.0,
                                'step': 1,
                                'type': 'range',
                                'unit': '%',
                                'valueType': 'percent'},
             'fan_sup_factor': {'max': 100.0,
                                'min': 0.0,
                                'step': 1,
                                'type': 'range',
                                'unit': '%',
                                'valueType': 'percent'},
             'heater_status': {'type': 'bool',
                               'unit': 'On',
                               'valueType': 'bool'},
             'mode_current': {'type': 'enum',
                              'unit': 'enum',
                              'valueType': 'DedicatedMode',
                              'values': ['OFF',
                                         'EVAPORATION',
                                         'RUNDOWN',
                                         'NORMAL',
                                         'FILTER_TEST',
                                         'FLOW_STABILIZATION',
                                         'SUBSTITUTE_CONTROL',
                                         'INTERVAL_VENTILATION',
                                         'DEFROST_HRC',
                                         'FORCE_CIRCULATION',
                                         'STARTUP',
                                         'WARM_UP',
                                         'EMERGENCY_OFF',
                                         'MANUAL',
                                         'ANTIFREEZE',
                                         'PREVENT_OFF']},
             'season_current': {'type': 'enum',
                                'unit': 'enum',
                                'valueType': 'Season',
                                'values': ['AUTO_TODA',
                                           'AUTO_TODA_RATIO',
                                           'HEATING',
                                           'NON_HEATING',
                                           'USER']},
             'season_request': {'type': 'enum',
                                'unit': 'enum',
                                'valueType': 'Season',
                                'values': ['AUTO_TODA',
                                           'AUTO_TODA_RATIO',
                                           'HEATING',
                                           'NON_HEATING',
                                           'USER']},
             'season_switch_temp': {'max': 50.0,
                                    'min': -30.0,
                                    'step': 0.1,
                                    'type': 'range',
                                    'unit': '°C',
                                    'valueType': 't_outside'},
             'temp_cool_active_offset': {'max': 3.0,
                                         'min': 0.1,
                                         'step': 0.1,
                                         'type': 'range',
                                         'unit': '°C',
                                         'valueType': 't_hysterese'},
             'temp_eha': {'max': 50.0,
                          'min': -30.0,
                          'step': 0.1,
                          'type': 'range',
                          'unit': '°C',
                          'valueType': 't_outside'},
             'temp_eta': {'max': 40.0,
                          'min': 10.0,
                          'step': 0.1,
                          'type': 'range',
                          'unit': '°C',
                          'valueType': 't_inside'},
             'temp_ida': {'max': 40.0,
                          'min': 10.0,
                          'step': 0.1,
                          'type': 'range',
                          'unit': '°C',
                          'valueType': 't_inside'},
             'temp_ida_cooler_hyst': {'max': 3.0,
                                      'min': 0.1,
                                      'step': 0.1,
                                      'type': 'range',
                                      'unit': '°C',
                                      'valueType': 't_hysterese'},
             'temp_ida_heater_hyst': {'max': 3.0,
                                      'min': 0.1,
                                      'step': 0.1,
                                      'type': 'range',
                                      'unit': '°C',
                                      'valueType': 't_hysterese'},
             'temp_oda': {'max': 50.0,
                          'min': -30.0,
                          'step': 0.1,
                          'type': 'range',
                          'unit': '°C',
                          'valueType': 't_outside'},
             'temp_oda_mean': {'max': 50.0,
                               'min': -30.0,
                               'step': 0.1,
                               'type': 'range',
                               'unit': '°C',
                               'valueType': 't_outside'},
             'temp_oda_mean_interval': {'type': 'enum',
                                        'unit': 'enum',
                                        'valueType': 'TempOdaMeanIntervalOptions',
                                        'values': ['HOURS_1',
                                                   'HOURS_3',
                                                   'HOURS_6',
                                                   'HOURS_12',
                                                   'DAYS_1',
                                                   'DAYS_2',
                                                   'DAYS_3',
                                                   'DAYS_4',
                                                   'DAYS_5',
                                                   'DAYS_6',
                                                   'DAYS_7',
                                                   'DAYS_8',
                                                   'DAYS_9',
                                                   'DAYS_10']},
             'temp_sup': {'max': 100.0,
                          'min': -30.0,
                          'step': 0.1,
                          'type': 'range',
                          'unit': '°C',
                          'valueType': 't_system'}},
 'types': {'fan_eta_factor': {'max': 100.0,
                              'min': 0.0,
                              'step': 1,
                              'type': 'range',
                              'unit': '%',
                              'valueType': 'percent'},
           'fan_power_req': {'max': 100.0,
                             'min': 0.0,
                             'name': 'fan_power_req',
                             'step': 1,
                             'type': 'range',
                             'unit': '%',
                             'valueType': 'percent'},
           'fan_sup_factor': {'max': 100.0,
                              'min': 0.0,
                              'step': 1,
                              'type': 'range',
                              'unit': '%',
                              'valueType': 'percent'},
           'heater_status': {'type': 'bool', 'unit': 'On', 'valueType': 'bool'},
           'mode_current': {'type': 'enum',
                            'unit': 'enum',
                            'valueType': 'DedicatedMode',
                            'values': ['OFF',
                                       'EVAPORATION',
                                       'RUNDOWN',
                                       'NORMAL',
                                       'FILTER_TEST',
                                       'FLOW_STABILIZATION',
                                       'SUBSTITUTE_CONTROL',
                                       'INTERVAL_VENTILATION',
                                       'DEFROST_HRC',
                                       'FORCE_CIRCULATION',
                                       'STARTUP',
                                       'WARM_UP',
                                       'EMERGENCY_OFF',
                                       'MANUAL',
                                       'ANTIFREEZE',
                                       'PREVENT_OFF']},
           'season_current': {'type': 'enum',
                              'unit': 'enum',
                              'valueType': 'Season',
                              'values': ['AUTO_TODA',
                                         'AUTO_TODA_RATIO',
                                         'HEATING',
                                         'NON_HEATING',
                                         'USER']},
           'season_request': {'type': 'enum',
                              'unit': 'enum',
                              'valueType': 'Season',
                              'values': ['AUTO_TODA',
                                         'AUTO_TODA_RATIO',
                                         'HEATING',
                                         'NON_HEATING',
                                         'USER']},
           'season_switch_temp': {'max': 50.0,
                                  'min': -30.0,
                                  'step': 0.1,
                                  'type': 'range',
                                  'unit': '°C',
                                  'valueType': 't_outside'},
           'temp_cool_active_offset': {'max': 3.0,
                                       'min': 0.1,
                                       'step': 0.1,
                                       'type': 'range',
                                       'unit': '°C',
                                       'valueType': 't_hysterese'},
           'temp_eha': {'max': 50.0,
                        'min': -30.0,
                        'step': 0.1,
                        'type': 'range',
                        'unit': '°C',
                        'valueType': 't_outside'},
           'temp_eta': {'max': 40.0,
                        'min': 10.0,
                        'step': 0.1,
                        'type': 'range',
                        'unit': '°C',
                        'valueType': 't_inside'},
           'temp_ida': {'max': 40.0,
                        'min': 10.0,
                        'step': 0.1,
                        'type': 'range',
                        'unit': '°C',
                        'valueType': 't_inside'},
           'temp_ida_cooler_hyst': {'max': 3.0,
                                    'min': 0.1,
                                    'step': 0.1,
                                    'type': 'range',
                                    'unit': '°C',
                                    'valueType': 't_hysterese'},
           'temp_ida_heater_hyst': {'max': 3.0,
                                    'min': 0.1,
                                    'step': 0.1,
                                    'type': 'range',
                                    'unit': '°C',
                                    'valueType': 't_hysterese'},
           'temp_oda': {'max': 50.0,
                        'min': -30.0,
                        'step': 0.1,
                        'type': 'range',
                        'unit': '°C',
                        'valueType': 't_outside'},
           'temp_oda_mean': {'max': 50.0,
                             'min': -30.0,
                             'step': 0.1,
                             'type': 'range',
                             'unit': '°C',
                             'valueType': 't_outside'},
           'temp_oda_mean_interval': {'type': 'enum',
                                      'unit': 'enum',
                                      'valueType': 'TempOdaMeanIntervalOptions',
                                      'values': ['HOURS_1',
                                                 'HOURS_3',
                                                 'HOURS_6',
                                                 'HOURS_12',
                                                 'DAYS_1',
                                                 'DAYS_2',
                                                 'DAYS_3',
                                                 'DAYS_4',
                                                 'DAYS_5',
                                                 'DAYS_6',
                                                 'DAYS_7',
                                                 'DAYS_8',
                                                 'DAYS_9',
                                                 'DAYS_10']},
           'temp_request': {'max': 40.0,
                            'min': 10.0,
                            'name': 'temp_request',
                            'step': 0.5,
                            'type': 'range',
                            'unit': '°C',
                            'valueType': 't_control'},
           'temp_sup': {'max': 100.0,
                        'min': -30.0,
                        'step': 0.1,
                        'type': 'range',
                        'unit': '°C',
                        'valueType': 't_system'},
           'work_regime': {'name': 'work_regime',
                           'type': 'enum',
                           'unit': 'enum',
                           'valueType': 'WorkRegime',
                           'values': ['OFF',
                                      'AUTO',
                                      'VENTILATION',
                                      'NIGHT_PRECOOLING']}},
 'unit': ['season_current',
          'temp_oda',
          'temp_oda_mean',
          'temp_eta',
          'temp_eha',
          'fan_sup_factor',
          'fan_eta_factor',
          'temp_ida',
          'temp_sup',
          'heater_status',
          'mode_current']}

```
### Poll data:

```

async def main():
    result = await amotion.update()
    pprint(result)


asyncio.run(main())

```

Response is a dictionary of the params

```
{'fan_eta_factor': 65,
 'fan_power_req': '65',
 'fan_sup_factor': 65,
 'heater_status': True,
 'mode_current': 'NORMAL',
 'season_current': 'HEATING',
 'temp_eha': 2.8,
 'temp_eta': 18.3,
 'temp_ida': 18.3,
 'temp_oda': -0.4,
 'temp_oda_mean': -0.427273,
 'temp_request': '18',
 'temp_sup': 13.8,
 'work_regime': 'VENTILATION'}
```

### Control:

#### Set param:

```

async def main():
    result = await amotion.control("temp_request", 25)
    pprint(result)

asyncio.run(main())

```

Return True or False

#### Use scene

```

async def main():
    result = await amotion.setScene(3)
    pprint(result)

asyncio.run(main())

```

This example use the scene 'Provoz 75/18' from previous example. Returns True or False


#### Enable/disable function (device trigger)

```

async def main():
    result = await amotion.setFce(1, True)
    pprint(result)

asyncio.run(main())

```
