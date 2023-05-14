from netmiko import ConnectHandler, BaseConnection
import time

"""
Este libreria de funciones consiste en la configuracion de swithces a traves de telnet.

Actualmente se ha provado en los swithces proporcionados por gns3, generando la automatizacion funcional para este tipo de dispositivos.
"""


def connectSwitch(switch, ip, port):
    """
    Se conecta a un switch a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param switch: tipo de switch (validado para switch proporcionado por gns3)
    :param ip: ip del nodo en el que vamos a virtualizar el switch
    :param port: puerto que esta abierto para realizar la conexion
    :return: None

Nota:Se puede apliar esta funcion para otras ips si se parametriza el parametro host, si se quiere conectar al router
directamente. Tambien se puede eliminar la palabra telnet y utilizar ssh si se encuentra disponible al igual que añadir
claves que no son necesarios para este modo.
    """
    connected = False
    while not connected:
        try:
            device: BaseConnection = ConnectHandler(
                device_type="%s_telnet" % switch,  # para switch cisco tiene que contener cisco_ios
                host=ip,
                port=port
            )
            connected = True
        except Exception as e:
            print("Error de conexión:", str(e))
            print("Reintentando la conexión en 5 segundos...")
            time.sleep(5)

    return device


def confVlan(settings):
    """
    Configura las vlans de un switch dado y las aplica en las interfaces
    :param settings: diccionario con los datos de configuracion del swithc
        calves:
            - switch: tipo de switch (validado para switch proporcionado por gns3)
            - port: puerto que esta abierto para realizar la conexion
            - vlans: lista de vlans a aplicar en el switch
                clave de las vlans:
                    * number: numero correspondiente a la vlan, si se encuentra trunk se considera que es el trunk
                    * name(optional): nombre de la vlan
                    * interfaces: lista de puertos donde se aplican la lista
    :return: None
nota: numbre: trunk -> se considera que se esta selecionando el modo trunk para los puertos esogidos en interfaces
    """
    device = connectSwitch(settings['switch'], settings['console_ip'], settings['console_port'])
    device.enable()
    for vlan in settings['vlans']:
        config_vlan = []
        if vlan['number'] == 'trunk':
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



