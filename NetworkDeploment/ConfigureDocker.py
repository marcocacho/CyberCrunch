import docker

"""
Libreria de funciones para configurar un docker activo
"""


def connectDocker(id):
    """
    Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param id: id del docker al que se quiere conectar
    :return: conector al docker
    """
    client = docker.from_env()
    return client.containers.get(id)


def configIp(settings, docker_id):
    """
    Configura la ip de un docker a traves de telnet
    :param settings: diccionario con los datos de configuracion del docker
        claves:
            - iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
            - ip: ip de la interfaz o dhcp para usar un servidor dhcp
            - netmask(optional): mascara de la red
            - gateway(optional): router de salida
    :param docker_id: id del docker que se quiere configurar
    :return:
    """

    docker_connection = connectDocker(docker_id)
    if settings["ip"].lower() == "dhcp":
        config_iface = "dhclient $s" % settings["iface"]
    else:
        config_iface = ["ifconfig %s up" % settings["iface"],
                        "ifconfig %s %s netmask %s" % (settings["iface"], settings["ip"], settings["netmask"]),
                        "route add default gw %s %s" % (settings["gateway"], settings["iface"])]

    for command in config_iface:
        print(f"{settings['ip']}: {docker_connection.exec_run(command)}")
