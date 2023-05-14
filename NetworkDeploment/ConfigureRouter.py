from netmiko import ConnectHandler, BaseConnection
import time
"""
Este libreria de funciones consiste en la configuracion de routers a traves de telnet.

Actualmente se ha provado en routers cisco, generando la automatizacion funcional para este tipo de dispositivos.
"""


def connectRouter(router, ip, port):
    """
    Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param router: tipo de router (validado para routers cisco)
    :param ip: ip del nodo en el que vamos a virtualizar el router
    :param port: puerto que esta abierto para realizar la conexion
    :return: conector al router

Nota:Se puede apliar esta funcion para otras ips si se parametriza el parametro host, si se quiere conectar al router
directamente. Tambien se puede eliminar la palabra telnet y utilizar ssh si se encuentra disponible al igual que añadir
claves que no son necesarios para este modo.
    """
    connected = False
    while not connected:  # por si tarda mas en encenderse del tiempo esperado
        try:
            device: BaseConnection = ConnectHandler(
                device_type="%s_telnet" % router,  # para switch cisco tiene que contener cisco_ios
                host=ip,
                port=port
            )
            connected = True
        except Exception as e:
            print("Error de conexión:", str(e))
            print("Reintentando la conexión en 5 segundos...")
            time.sleep(5)
    return device


def confIp(settings):
    """
    Configura ip's de un router a traves de telnet
    :param settings: diccionario con los datos de configuracion del router
        claves:
            - router: tipo de router que se va configurar
            - port: puerto donde se va a relaziar la conexion telnet
            - interfaces: lista interface o interfaces que se van a configurar
                claves de cada interface:
                    * iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
                    * ip: ip de la interfaz router
                    * netmask: mascara de la ip
                    * nat(optional): nateo de la interfaz (inside o outside) (no necesario)
    :return: None
    """
    device = connectRouter(settings['router'], settings['console_ip'], settings['console_port'])
    for interface in settings['interfaces']:
        config_iface = []
        if "vlan" in interface:
            config_iface.append('interface %s.%s' % (interface['iface'], interface["vlan"]))
            config_iface.append("encapsulation dot1Q %s" % interface["vlan"])
            config_iface.append('ip address %s %s' % (interface['ip'], interface['netmask']))
            config_iface.append('no shutdown')
            config_iface.append("exit")
            config_iface.append('interface %s' % interface['iface'])
            config_iface.append('no shutdown')
        else:
            config_iface.append('interface %s' % interface['iface'])
            if "ip" in interface:
                config_iface.append('ip address %s %s' % (interface['ip'], interface['netmask']))
            else:
                config_iface.append('ip address dhcp')
            config_iface.append('no shutdown')
            if 'nat' in interface:
                nat = interface['nat']
                if nat == 'inside' or nat == 'outside':
                    config_iface.append('ip nat %s' % nat)

        output = device.send_config_set(config_iface)
    device.disconnect()


def confRoute(settings):
    """
    Configura el enrutamiento de un router dado
    :param settings:diccionario con los datos de configuracion del router
        claves:
            - router: tipo de router que se va configurar
            - port: puerto donde se va a relaziar la conexion telnet
            - type: tipo de enrutamiento (static, rip)
            - routes: lista de rutas
                claves de las rutas static:
                    * origin: ip de origen
                    * orNetmask: mascara de la ip de origen
                    * dest: siguiente salto del paquete
                claves de las rutas rip:
                    * version: version del protocolo rip
                    * networks: lista de redes que alcanza el router
    :return: None
    """
    device = connectRouter(settings['router'], settings['console_ip'], settings['console_port'])

    config_route = []
    if settings['type'] == 'static':  # si el tipo de enrutamiento es estatico.
        for route in settings['routes']:
            config_route.append('ip route %s %s %s' % (route['origin'], route['orNetmask'], route['dest']))
    elif settings['type'] == 'rip':  # para el tipo de enrutamiento dinamico con rip
        version = settings['routes']['version']
        networks = settings['routes']['networks']
        config_route.append('router rip')
        config_route.append('version %s' % version)
        for net in networks:
            config_route.append('network %s' % net)
    elif settings['type'] == 'ospf':  # para el tipo de enrutamiento dinamico con ospf
        config_route.append("router ospf 1")
        for area in settings['routes']:
            config_route.append("network %s %s area %s" % (area["ip"], area["wilcard"], area["area"]))
    output = device.send_config_set(config_route)
    device.disconnect()


def confAcl(settings):
    """
    Configura las acl de un router dado y las aplica en las interfaces
    :param settings:  diccionario con los datos de configuracion del router
        claves:
            - router: tipo de router que se va configurar
            - port: puerto donde se va a relaziar la conexion telnet
            - acls: lista con las acl que se quieren aplicar, se configurar en orden de la lista
                claves de las acls:
                    * list: lista a la que pertenece la acl
                    * action: accion que se va a aplicar a la acl
                    * origin: ip de origen
                    * orNetmask(optional): mascara de red de la ip de origen
                    * dest(optional): ip de destino
                    * destNetmask(optional): ascara de red de la ip de destino
                    * protocol(optional): tipo de socket ( ip | tcp | udp | icmp)
                    * operator(optinal): comparacion que se va a aplicar al puerto, en caso de omision se aplicara un eq
                    * port(optional): pnumero o nombre del puerto sobre el que se aplica la acl
            - interfaces_acl: interfaz del router donde se van a aplicar las eq por defecto (gt | lt | eq)**
                claves de las interfaces:
                    * interfaz: interfaz a la que se va a aplicar la lista (formatos validos fa 0/0 y fast ethernet 0/0)
                    * listAcl: lista con todas las acl que se quieren aplicar a esa interfaz y el tipo de accion
                    claves de las listAcl:
                        % list: lista que se quiere aplicar
                        % action: con que tipo de paquetes aplicar
    :return: None

nota: Si se quiere añadir una sentencia final a una lista de acl para permit o deny any se tendra que añadir dentro de la lista
    de las acls al final de la lista.
nota**: gt = greater than, lt = lesser than, eq = equal
    """
    device = connectRouter(settings['router'], settings['console_ip'], settings['console_port'])

    config_acl = []
    for acl in settings['acls']:
        sentence = "access-list %s %s " % (acl['list'], acl['action'])  # añado la lista y la accion de la sentencia

        if 'protocol' in acl:  # Contiene un tipo protocolo
            sentence += acl['protocol'] + ' '
        if 'orNetmask' in acl:  # contiene mascara para el origen
            sentence += acl['origin'] + ' ' + acl['orNetmask'] + ' '
        else:
            if 'any' == acl['origin']:  # el origien no es any (cualquiera)
                sentence += acl['origin'] + ' '
            else:
                sentence += 'host ' + acl['origin'] + ' '
        if 'dest' in acl:  # Hay una ip destino
            if 'destNetmask' in acl:  # contiene mascara para el destino
                sentence += acl['dest'] + ' ' + acl['destNetmask'] + ' '
            else:
                if 'any' == acl['dest']:  # el destino es any (cualquiera
                    sentence += acl['dest'] + ' '
                else:
                    sentence += 'host ' + acl['dest'] + ' '
        if 'port' in acl:  # añade un puerto para la sentencia
            if 'operator' in acl:
                sentence += acl['operator'] + ' ' + acl['port']
            else:
                sentence += 'eq ' + acl['port']
        config_acl.append(sentence)
    output = device.send_config_set(config_acl)
    for interface in settings['interfaces_acl']:
        apply_acl = ['interface %s ' % interface['interface']]
        for listAcl in interface['list_acl']:
            apply_acl.append('ip access-group %s %s' % (listAcl['list'], listAcl['action']))
        output = device.send_config_set(apply_acl)
    device.disconnect()


def saveConfiguration(router, console_ip, console_port):
    """
    Guarda la configuracion para el arranque del equipo
    :param router: tipo de SO del router
    :param console_ip: ip del servidor gns3
    :param console_port: puerto por el que se va a conectar
    :return: None
    """
    device = connectRouter(router, console_ip, console_port)
    output = device.send_command_timing('copy running-config startup-config')
    if "Address or name" in output:
        output += device.send_command_timing("\n")
    if "Destination filename" in output:
        output += device.send_command_timing("\n")

    device.disconnect()


def confNateo(router, console_ip, console_port, iface):
    """
    Configura el nodo conectado a el nat para permitir conexiones del resto de nodos
    :param router: tipo de SO del router
    :param console_ip: ip del servidor gns3
    :param console_port: puerto por el que se va a conectar
    :param iface: Interfaz por la que se conecta el nat
    :return: None
    """
    device = connectRouter(router, console_ip, console_port)
    comands = ["ip nat inside source list 1 interface %s overload" % iface,
               "access-list 1 permit any"]
    output = device.send_config_set(comands)
    device.send_config_set()

    device.disconnect()
