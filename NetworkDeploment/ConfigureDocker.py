import docker
from ConfigureGns3 import getDockerId
#cambiar por cone
def connectDocker(id):
    """
    Se conecta a un router a traves de telnet desplegado en gns3 instalado en la maquina local.
    :param id: id del docker al que se quiere conectar
    :return: conector al docker
    """
    client = docker.from_env()
    return client.containers.get(id)



def configIp(settings, name, lab):
    """
    Configura la ip de un docker a traves de telnet
    :param settings: diccionario con los datos de configuracion del docker
        claves:
            - docker: tipo de docker que se va configurar
            - port: puerto donde se va a relaziar la conexion telnet
            - interfaces: lista interface o interfaces que se van a configurar
                claves de cada interface:
                    * iface: interfaz del router (formatos validos fa 0/0 y fast ethernet 0/0)
                    * ip: ip de la interfaz o dhcp para usar un servidor dhcp
                    * netmask(optional): mascara de la red
                    * gateway(optional): router de salida
                    :return:
    """

    docker = connectDocker(getDockerId(name))
    for interface in settings['interfaces']:
        if interface["ip"].lower() == "dhcp":
            config_iface = "dhclient $s" % interface["iface"]
        else:
            config_iface = ["ifconfig %s up;" % interface["iface"],
                            "ifconfig %s %s netmask %s;" % (interface["iface"], interface["ip"], interface["netmask"]),
                            "oute add default gw %s %s;" % (interface["gateway"], interface["iface"])]
        docker.exec_run(config_iface)