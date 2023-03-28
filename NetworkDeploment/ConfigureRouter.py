from netmiko import ConnectHandler, BaseConnection

"""
Este libreria de funciones consiste en la configuracion de routers a traves de telnet.

Actualmente se ha provado en routers cisco, generando la automatizacion funcional para este tipo de dispositivos.
"""
"""
Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.

Parametros de entrada:
    + router: tipo de router (validado para routers cisco)
    + port: puerto que esta abierto para realizar la conexion
devuelve:
    + device: conector al router
Nota:Se puede apliar esta funcion para otras ips si se parametriza el parametro host, si se quiere conectar al router 
directamente. Tambien se puede eliminar la palabra telnet y utilizar ssh si se encuentra disponible al igual que añadir 
claves que no son necesarios para este modo.
"""


def connectRouter(router, port):
    device: BaseConnection = ConnectHandler(
        device_type="%s_telnet" % router,  # para router cisco tiene que contener cisco_ios
        host="127.0.0.1",
        port=port
    )
    return device


"""
Configura ip's de un router a traves de telnet

Parametros de entrada:
    + settings: diccionario con los datos de configuracion del router
        claves:
            - router: tipo de router que se va configurar
            - port: puerto donde se va a relaziar la conexion telnet
            - interfaces: lista interface o interfaces que se van a configurar
                claves de cada interface:
                    * iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
                    * ip: ip de la interfaz router
                    * netmask: mascara de la ip
                    * nat(optional): nateo de la interfaz (inside o outside) (no necesario)

"""


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
    device = connectRouter(settings['router'], settings['port'])
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
            config_iface.append('ip address %s %s' % (interface['ip'], interface['netmask']))
            config_iface.append('no shutdown')
            if 'nat' in interface:
                nat = interface['nat']
                if nat == 'inside' or nat == 'outside':
                    config_iface.append('ip nat %s' % nat)

        output = device.send_config_set(config_iface)


"""
Configura el enrutamiento de un router dado
Parametros de entrada:
    + settings: diccionario con los datos de configuracion del router
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
"""


def confRoute(settings):
    device = connectRouter(settings['router'], settings['port'])

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


"""
Configura las acl de un router dado y las aplica en las interfaces
Parametros de entrada:
    + settings: diccionario con los datos de configuracion del router
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
nota: Si se quiere añadir una sentencia final a una lista de acl para permit o deny any se tendra que añadir dentro de la lista
    de las acls al final de la lista.
nota**: gt = greater than, lt = lesser than, eq = equal
"""


def confAcl(settings):
    device = connectRouter(settings['router'], settings['port'])

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
        apply_acl = []
        apply_acl.append('interface %s ' % interface['interface'])
        for listAcl in interface['list_acl']:
            apply_acl.append('ip access-group %s %s' % (listAcl['list'], listAcl['action']))
        output = device.send_config_set(apply_acl)


if __name__ == '__main__':
    interface = [{'iface': 'fa0/0',
                  'ip': '10.0.0.1',
                  'netmask': '255.255.255.0'
                  },
                 {'iface': 'fa1/0',
                  'ip': '10.0.1.1',
                  'netmask': '255.255.255.0',
                  'nat': 'inside'
                  },
                 {'iface': 'fa2/0',
                  'ip': '10.0.2.1',
                  'netmask': '255.255.255.0',
                  'nat': 'asd'
                  }
                 ]
    config_ip = {'router': 'cisco_ios',
                 'port': '5001',
                 'interfaces': interface
                 }

    # confIp(config_ip)

    routes_static = [{'origin': '10.0.0.0',
                      'orNetmask': '255.255.255.0',
                      'dest': '10.0.1.2'
                      },
                     {'origin': '10.0.1.0',
                      'orNetmask': '255.255.255.0',
                      'dest': '10.0.2.2'
                      }
                     ]
    routes_rip = {'version': '2',
                  'networks': ['10.0.0.0', '10.0.1.0', '10.0.2.0']
                  }
    routes_ospf = [{"ip": "192.168.10.0", "wilcard": "0.0.0.255", "area": "1"},
                   {"ip": "192.168.20.0", "wilcard": "0.0.0.255", "area": "1"},
                   {"ip": "192.168.0.0", "wilcard": "0.0.0.255", "area": "1"}]
    config_route = {'router': 'cisco_ios',
                    'port': '5001',
                    'type': 'rip',
                    'routes': routes_rip
                    }
    # confRoute(config_route)
    acl = [{'list': '10',
            'action': 'permit',
            'origin': '10.0.1.0',
            'orNetmask': '255.255.255.0',
            },
           {'list': '110',
            'action': 'deny',
            'origin': '10.0.2.14',
            'dest': '10.0.0.0',
            'destNetmask': '255.255.255.0',
            'protocol': 'tcp',
            'port': '25'
            }
           ]
    list_acl = [{'interface': 'fa0/0',
                 'list_acl': [{'list': '10', 'action': 'out'},
                              {'list': '110', 'action': 'out'}]

                 }]
    config_acl = {'router': 'cisco_ios',
                  'port': '5001',
                  'acls': acl,
                  'interfaces_acl': list_acl
                  }
    confAcl(config_acl)
