import json
import threading
import time
import sys
import os

from gns3fy import Gns3Connector, Project

import NetworkDeployment.ConfigureDocker
import NetworkDeployment.ConfigureGns3
import NetworkDeployment.ConfigureRouter
import NetworkDeployment.ConfigureSwitch


def readJson(file):
    """
    Se encarga de ir leyendo los distintos elementos de la red y ir configurandolos paso a paso:
    :param file: fichero donde se contiene la red que se desea desplegar con el formato descrito en LaboratoryFormat.txt,
        se usara este nombre para crear o buscar el laboratorio que abrir en gns3
    :return: None
    """
    hilos = {}  # dicionario con los hilos creados
    f = open(file, "r")
    try: #validacion JSON valido
        network = json.load(f)
        print("Se empieza a configurar el laboratorio")
        gns3 = network["gns3"] #10.0.49.2 ip interna de equipo
        gns3_server = Gns3Connector(url=f"http://{gns3['ip']}:{gns3['port']}",
                                    user=gns3["user"], cred=gns3["pass"])
        lab_name = network["labName"]
        lab: Project = NetworkDeployment.ConfigureGns3.openProject(gns3_server, lab_name)

        if "nat" in network:  # creacion hilo para configurar el Nat
            nat = network["nat"]
            for iface in network["components"][nat["router"]]["interfaces"]:
                iface["nat"] = "inside"
            network["components"][nat["router"]]["interfaces"].append({"iface": nat["iface"], "nat": "outside"})
            network["connection_list"].append([{"name": nat["router"], "interface": nat["iface"]},
                                               {"name": "NAT", "interface": nat["nat"]}])
            nat["OS"] = network["components"][nat["router"]]["OS"]
            hilos["nat"] = threading.Thread(name="nat", target=configureNat,
                                            args=(lab, "NAT", nat))

        for deviceName, settings in network["components"].items():
            if settings["machineType"].lower() == "switch":  # creacion hilo para configurar switch
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureSwitch,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
            elif settings["machineType"].lower() == "router":  # creacion hilo para configurar router
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureRouter,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
            if settings["machineType"].lower() == "docker":  # creacion hilo para configurar dockers
                hilos[deviceName] = threading.Thread(name=deviceName, target=configureDocker,
                                                     args=(lab, deviceName, settings))
                hilos[deviceName].start()
        if "connection_list" in network:  # apartado de crear las conexiones entre maquinas
            hilos["connection_list"] = threading.Thread(name="connection_list", target=connectNodes,
                                                        args=(lab, gns3_server, network["connection_list"]))

        for deviceName in hilos:
            if not (deviceName == "connection_list" or deviceName == "nat"):
                hilos[deviceName].join()
        # añadir aqui la cracion del nat

        hilos["nat"].start()
        hilos["nat"].join()
        hilos["connection_list"].start()
        hilos["connection_list"].join()

        print(f"Red {lab_name} creada y configura")
    except json.JSONDecodeError:
        print("Invalid JSON format. Please provide a valid JSON file.")
    finally:
        f.close()


def configureRouter(lab, name, settings):
    """
    Crea el nodo router selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    if "template" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template=settings["template"])
    elif "template_id" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template_id=settings["template_id"])

    NetworkDeployment.ConfigureGns3.manageMachines(name, lab, "start")
    time.sleep(30)  # tiempo de esperado para que se encienda el equipo
    if "interfaces" in settings:
        config_ip = {"router": settings["OS"], "console_ip": console_ip, "console_port": console_port, "interfaces": settings["interfaces"]}
        NetworkDeployment.ConfigureRouter.confIp(config_ip)
    if "routes" in settings:
        config_route = {"router": settings["OS"], "console_ip": console_ip, "console_port": console_port, "pathingType": settings["pathingType"],
                        "routes": settings["routes"]}
        NetworkDeployment.ConfigureRouter.confRoute(config_route)
    if "acls" in settings:
        config_acl = {"router": settings["OS"], "console_ip": console_ip, "console_port": console_port, "acls": settings["acls"],
                      "interfaces_acl": settings["interfaces_acl"]}
        NetworkDeployment.ConfigureRouter.confAcl(config_acl)
    if "gateway" in settings:
        config_default_route = {"router": settings["OS"], "console_ip": console_ip, "console_port": console_port, "pathingType": "static",
                                "routes": [{"origin": "0.0.0.0", "orNetmask": "0.0.0.0", "dest": settings["gateway"]}]}
        NetworkDeployment.ConfigureRouter.confRoute(config_default_route)

    NetworkDeployment.ConfigureRouter.saveConfiguration(settings["OS"], console_ip, console_port)

    print(f"Configured: {name}")


def configureSwitch(lab, name, settings):
    """
    Crea el nodo switch selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    if "template" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template=settings["template"])
    elif "template_id" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template_id=settings["template_id"])
    NetworkDeployment.ConfigureGns3.manageMachines(name, lab, "start")
    time.sleep(60)  # tiempo de esperado para que se encienda el equipo
    if "vlans" in settings:
        config_vlan = {"switch": settings["OS"], "console_ip": console_ip, "console_port": console_port, "vlans": settings["vlans"]}
        NetworkDeployment.ConfigureSwitch.confVlan(config_vlan)
    NetworkDeployment.ConfigureRouter.saveConfiguration(settings["OS"], console_ip, console_port)
    print(f"Configured: {name}")


def configureDocker(lab, name, settings):
    """
    Crea el nodo docker selecionado, lo enciende y lo configurarlo
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :param opensearch: diccionario con los datos de la ip y puerto del servidor opensearch
    :return: None
    """
    if "template" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template=settings["template"])
    elif "template_id" in settings:
        console_ip, console_port = NetworkDeployment.ConfigureGns3.addNode(name, lab, template_id=settings["template_id"])
    #se llamara a la funcion para cambiar el nombre del docker y añadir los templates.
    docker_id = NetworkDeployment.ConfigureGns3.getDockerId(name, lab)

    #Actualizamos el docker
    if "logs_route" in settings:
        NetworkDeployment.ConfigureDocker.updateDocker(docker_id, name, lab.name, logs_docker=settings["logs_route"],
                                                       console_ip=console_ip)
    else:
        NetworkDeployment.ConfigureDocker.updateDocker(docker_id, name, lab.name, console_ip=console_ip)

    NetworkDeployment.ConfigureGns3.manageMachines(name, lab, "start")


    NetworkDeployment.ConfigureDocker.configIp({"iface": settings["iface"], "ip": settings["ip"],
                                               "netmask": settings["netmask"], "gateway": settings["gateway"]},
                                               docker_id, console_ip)
    print(f"Configured: {name}")

def connectNodes(lab, server, conection_list):
    """
    Crea los enlaces entre los nodos de la red
    :param lab: laboratorio de gns3 abierto
    :param server: conector con el servidor gns3
    :param conection_list: lista con los nodos a conectar
    :return: None
    """
    for nodos in conection_list:
        NetworkDeployment.ConfigureGns3.createLinks(lab, server, nodos[0], nodos[1])
    print("Nodos conected")


def configureNat(lab, name, settings):
    """
    Conecta un router con el nodo nat, y configura la acl-list para el envio de paquetes
    :param lab: laboratorio de gns3 abierto
    :param name: nombre que se le va a otorgar al nodo
    :param settings: diicionario con los datos a configurar con el formato descrito en LaboratoryFormat.txt
    :return: None
    """
    NetworkDeployment.ConfigureGns3.addNode(name, lab, "NAT")
    console_ip = lab.get_node(settings["router"]).console_host
    console_port = lab.get_node(settings["router"]).console
    NetworkDeployment.ConfigureRouter.confNateo(settings["OS"], console_ip, console_port, settings["iface"])
    # no necesario poner ip domain-server 8.8.8.8 y ip domain-lookup
    NetworkDeployment.ConfigureRouter.saveConfiguration(settings["OS"], console_ip, console_port)

    print(f"Configured: {name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid number of arguments provided. Please provide a valid path to a JSON file.")
    else:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print("Invalid file. Please provide a valid path to a JSON file.")
        else:
            readJson(filename)
