import re

from NetworkDeploment.ConfigureDocker import connectDocker
from NetworkDeploment.ConfigureGns3 import getDockerId
from NetworkDeploment.ConfigureRouter import connectRouter
from NetworkDeploment.ConfigureSwitch import connectSwitch


def getLinkData(links_global, lab, name):
    """
    Consulta el nodo, interfaces con el que esta conectado el nodo dado
    :param link: lista de enlace
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: diccionario con (interface, destinationInterface, destinationName)
    """
    all_data = []
    for links in links_global:
        data = {}
        in_node = False
        for link in links.nodes:
            node = lab.get_node(node_id=link["node_id"])
            if node.name != name:  # compruebo si es el nodo destino
                data["destinationName"] = node.name
                data["destinationInterface"] = node.ports[link["adapter_number"]]["name"]
            else:  # es el nodo origen
                data["interface"] = node.ports[link["adapter_number"]]["name"]
                in_node = True
        if in_node:
            all_data.append(data)

    return all_data


def getIpInfoRouter(lab, name):
    """
    Consulta la ip de las interfaces de un router
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: diccionario con las ip de las interfaces y sus ips
    """
    node = lab.get_node(name)
    device = connectRouter("cisco_ios", node.console)
    config = device.send_command("show ip interface brief")
    data = {}
    for i, line in enumerate(config.split("\n")):
        if i == 0:
            continue
        else:
            word = line.split()
            k, v = word[:2]
            if v != 'unassigned':
                data[k] = v
    return data


def getProtocolRouter(lab, name):
    """
    Consulta el protocolo configurado en un router
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: devuelve el procolo configurado
    """
    node = lab.get_node(name)
    device = connectRouter("cisco_ios", node.console)
    config = device.send_command("show ip protocol")
    words = config.split("\n")[2].split()
    return (words[3] + " " + words[4]).replace('\"', '')


def getVlanSwitch(lab, name):
    """
    Consulta las vlans existentes en un switch, junto con la interfaz a la que pertenece
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: devuelve un dicionaro con las vlans y las intefaces que pertenece
    """
    node = lab.get_node(name)
    device = connectSwitch("cisco_ios", node.console)
    config = device.send_command("show vlan brief")

    vlans = {}
    for line in config.split("\n")[2:]:
        match = re.match(r'^s*(\d+)\s+(\S+(?: \d+)?)\s+(\S+)\s(.+)$', line)
        if match:
            vlan_id = match.group(1)
            interfaces = (match.group(4).replace(',', '').split())
            vlans[vlan_id] = interfaces

    return vlans


def getGatewayLinux(lab, name):
    """
    Consulta la Ip del gateway de un dispositivo linux
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: Ip del gateway
    """
    docker_connection = connectDocker(getDockerId(name, lab))
    result = docker_connection.exec_run("route")
    config = result.output.decode("utf-8")
    gateway_match = re.search(r"^default\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", config, re.MULTILINE)
    if gateway_match:
        return gateway_match.group(1)
    else:
        return None


def getIpLinux(lab, name):
    """
    Consulta la Ip  de un equipo linux
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: Ip del equipo
    """
    docker_connection = connectDocker(getDockerId(name, lab))
    result = docker_connection.exec_run("ifconfig eth0")
    config = result.output.decode("utf-8")
    gateway_match = re.search(r"^\s+inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", config, re.MULTILINE)
    if gateway_match:
        return gateway_match.group(1)
    else:
        return None


def getInfoRouter(name, lab):
    """
    Solicta informacion considerada importante de un router
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    node = lab.get_node(name)
    data = {"name": name, "type": "router", "links": getLinkData(lab.links, lab, name),
            "ip": getIpInfoRouter(lab, name), "protocol": getProtocolRouter(lab, name), "status": node.status}

    return data


def getInfoSwithch(name, lab):
    """
    Solicta informacion considerada importante de un switch
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    node = lab.get_node(name)
    data = {"name": name, "type": "Switch", "links": getLinkData(lab.links, lab, name),
            "vlans": getVlanSwitch(lab, name), "status": node.status}

    return data


def getInfoLinux(name, lab):
    """
    Solicta informacion considerada importante de un equipo linux
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    node = lab.get_node(name)
    data = {"name": name, "type": "Linux", "links": getLinkData(lab.links, lab, name),
            "ip": getIpLinux(lab, name), "gateway": getGatewayLinux(lab, name), "status": node.status}

    return data
