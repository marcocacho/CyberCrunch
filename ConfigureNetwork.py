import json
import time
import threading
from gns3fy import Gns3Connector, Project
import NetworkDeploment.ConfigureRouter
import NetworkDeploment.ConfigureGns3
import NetworkDeploment.ConfigureSwitch
import NetworkDeploment.ConfigureMachine
import NetworkDeploment.ConfigureDocker

def readJson(file):
    """
    Se encarga de ir leyendo los distintos elementos de la red y ir configurandolos paso a paso:
    :param file: fichero donde se contiene la red que se desea desplegar con el formato descrito en LaboratoryFormat.txt,
        se usara este nombre para crear o buscar el laboratorio que abrir en gns3
    :return:
    """
    hilos = {} # dicionario con los hilos creados
    f = open(file, "r")
    network = json.load(f)
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    lab_name = file.replace(".json", "")
    lab: Project = NetworkDeploment.ConfigureGns3.openProject(gns3_server, lab_name)
    for deviceName in network:
        settings = network[deviceName]
        if deviceName == "connection_list":  # apartado de crear las conexiones entre maquinas
            hilos[deviceName] = threading.Thread(name=deviceName, target=connectNodes,
                                                 args=(lab, gns3_server, settings))
        else:  # apartado de crear los nodos y configurarlos

            if settings["machineType"] == "switch":
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureSwitch,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
            elif settings["machineType"] == "router":
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureRouter,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
            elif settings["machineType"] == "docker":
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureDocker,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
    for deviceName in hilos:
        if not deviceName == "connection_list":
            hilos[deviceName].join()
    #añadir aqui la cracion del nat
    hilos["connection_list"].start()
    hilos["connection_list"].join()
    print(f"Red {lab_name} creada y configura")
    f.close()


def configureRouter(lab, name, settings):
    """
    Crea el nodo router selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    port = NetworkDeploment.ConfigureGns3.addNode(name, lab, settings["template"])
    NetworkDeploment.ConfigureGns3.manageMachines(name, lab, "start")
    time.sleep(30) # tiempo de espera a que se encienda el equipo
    if "interfaces" in settings:
        config_ip = {"router": settings["router"], "port": port, "interfaces": settings["interfaces"]}
        NetworkDeploment.ConfigureRouter.confIp(config_ip)
    if "routes" in settings:
        config_route = {"router": settings["router"], "port": port, "type": settings["type"],
                        "routes": settings["routes"]}
        NetworkDeploment.ConfigureRouter.confRoute(config_route)
    if "acls" in settings:
        config_acl = {"router": settings["router"], "port": port, "acls": settings["acls"],
                      "interfaces_acl": settings["interfaces_acl"]}
        NetworkDeploment.ConfigureRouter.confAcl(config_acl)
    NetworkDeploment.ConfigureRouter.saveConfiguration(settings["router"], port)

    print(f"{name} creado y configurado")

def configureSwitch(lab, name, settings):
    """
    Crea el nodo switch selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    port = NetworkDeploment.ConfigureGns3.addNode(name, lab, settings["template"])
    NetworkDeploment.ConfigureGns3.manageMachines(name, lab, "start")
    time.sleep(60) # tiempo de espera a que se encienda el equipo
    if "vlans" in settings:
        #NetworkDeploment.ConfigureSwitch.enableTerminal(settings["switch"], port)
        config_vlan = {"switch": settings["switch"], "port": port, "vlans": settings["vlans"]}
        NetworkDeploment.ConfigureSwitch.confVlan(config_vlan)
    NetworkDeploment.ConfigureRouter.saveConfiguration(settings["switch"], port)
    print(f"{name} creado y configurado")

def configureDocker(lab, name, settings):
    """
    Crea el nodo docker selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    port = NetworkDeploment.ConfigureGns3.addNode(name, lab, settings["template"])
    NetworkDeploment.ConfigureGns3.manageMachines(name, lab, "start")
    docker_id = NetworkDeploment.ConfigureGns3.getDockerId(name, lab)
    NetworkDeploment.ConfigureDocker.configIp({"iface": settings["iface"], "ip": settings["ip"],
                                               "netmask": settings["netmask"],"gateway": settings["gateway"]},
                                              docker_id)
    print(f"{name} creado y configurado")
def connectNodes(lab, server, conection_list):
    """
    Crea los enlaces entre los nodos de la red
    :param lab: laboratorio de gns3 abierto
    :param server: conector con el servidor gns3
    :param conection_list: lista con los nodos a conectar
    :return: None
    """
    for nodos in conection_list:
        NetworkDeploment.ConfigureGns3.createLinks(lab, server, nodos[0], nodos[1])
    print ("Nodos conectados")

def configureNat(lab, name, settings):
    """
    Conecta un router con el nodo nat, y configura la acl-list para el envio de paquetes
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    #Se añade el nodo nat aqui
    #Se necesita poner la interfaz del router en dhcp (ip address dhcp), nateo del router para outside(ip nat outside)
    #se necesita poner las interfaces que no son del nat con nat inside (ip nat inside)
    #Se tiene que configurar la acceslist (por ahora ip nat inside source list 1 interface fastEthernet 2/0 overload y access-list 1 permit any)
    #no necesario poner ip domain-server 8.8.8.8 y ip domain-lookup
    #resto de router añadir ruta por defecto con el mas cercano al nodo con nat (ip route 0.0.0.0 0.0.0.0 ip)



if __name__ == "__main__":
    readJson("redPrueba.json")
