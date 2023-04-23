from netmiko import ConnectHandler, BaseConnection
"""
Este libreria de funciones consiste en la configuracion de swithces a traves de telnet.

Actualmente se ha provado en los swithces proporcionados por gns3, generando la automatizacion funcional para este tipo de dispositivos.
"""
"""
Se conecta a un switch a traves de telnet desplegado en gns3 instalado en la maquina local.
Parametros de entrada:
    + switch: tipo de switch (validado para switch proporcionado por gns3)
    + port: puerto que esta abierto para realizar la conexion
    
Devuelve:
    + device: conector al switch

Nota:Se puede apliar esta funcion para otras ips si se parametriza el parametro host, si se quiere conectar al router 
directamente. Tambien se puede eliminar la palabra telnet y utilizar ssh si se encuentra disponible al igual que añadir 
claves que no son necesarios para este modo.
"""
def connectSwitch(switch, port):
    device: BaseConnection = ConnectHandler(
        device_type="%s_telnet" % switch,  # para switch cisco tiene que contener cisco_ios
        host="127.0.0.1",
        port=port
    )
    return device

"""
Configura las vlans de un switch dado y las aplica en las interfaces
Parametros de entrada:
    + settings: diccionario con los datos de configuracion del swithc
        calves:
            - switch: tipo de switch (validado para switch proporcionado por gns3)
            - port: puerto que esta abierto para realizar la conexion
            - vlans: lista de vlans a aplicar en el switch
                clave de las vlans:
                    * number: numero correspondiente a la vlan, si se encuentra trunk se considera que es el trunk
                    * name(optional): nombre de la vlan
                    * interfaces: lista de puertos donde se aplican la lista

nota: numbre: trunk -> se considera que se esta selecionando el modo trunk para los puertos esogidos en interfaces
"""
def confVlan(settings):
    device = connectSwitch(settings['switch'], settings['port'])
    device.enable()
    for vlan in settings['vlans']:
        config_vlan = []
        if vlan['number']=='trunk':
            for port in vlan['interfaces']:
                config_vlan.append('int %s' % port)
                config_vlan.append('switchport trunk encapsulation dot1q')
                config_vlan.append('switchport mode trunk')
        else:
            config_vlan.append('vlan %s' % vlan['number'])
            if 'name' in vlan:
                config_vlan.append('name %s' % vlan['name'])
            for port in vlan['interfaces']:
                config_vlan.append('int %s' % port)
                config_vlan.append('switchport mode access')
                config_vlan.append('switchport access vlan %s' % vlan['number'])
                config_vlan.append('no shutdown')
        output = device.send_config_set(config_vlan)
        device.disconnect()


if __name__ == '__main__':
    vlans = [{'number': 'trunk',
              'interfaces': ['Gi 0/0']
              },
             {
                'number': '10',
                 'name': 'prueba',
                 'interfaces': ['Gi 0/1', 'Gi 0/2']
             },
             {
                 'number': '20',
                 'name': 'prueba2',
                 'interfaces': ['Gi 1/1', 'Gi 1/2']
             }]
    config_vlan = {'switch': 'cisco_ios',
                    'port': '5000',
                    'vlans': vlans
                    }
    confVlan(config_vlan)