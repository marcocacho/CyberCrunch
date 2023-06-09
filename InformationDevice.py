import re

from NetworkDeployment.ConfigureDocker import connectDocker
from NetworkDeployment.ConfigureGns3 import getDockerId
from NetworkDeployment.ConfigureRouter import connectRouter
from NetworkDeployment.ConfigureSwitch import connectSwitch


def getLinkData(links_global, lab, name):
    """
    Consulta el nodo, interfaces con el que esta conectado el nodo dado
    :param links_global: lista de enlace
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
    device = connectRouter("cisco_ios", node.console_host, node.console)
    config = device.send_command("show run | inc interface | ip address")
    interfaces = []
    pattern = r"interface\s+(\S+)\s+ip address\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(pattern, config)
    for match in matches:
        interfaces.append({"iface": match[0], "ip": match[1], "netmask": match[2]})

    return interfaces


def getProtocolRouter(lab, name):
    """
    Consulta el protocolo configurado en un router
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: devuelve el procolo configurado
    """
    node = lab.get_node(name)
    device = connectRouter("cisco_ios", node.console_host, node.console)
    config = device.send_command("show ip protocol")
    #Añadir la deteccion de areas y ips
    words = config.split("\n")[2].split()

    pathingType = (words[3]).replace('\"', '')
    routes = []
    if pathingType.lower() == "ospf":
        pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s)+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+area\s+(\d+)"
        # Find all matches in the OSPF output
        matches = re.findall(pattern, config)
        for ip, wildcard, area in matches:
            routes.append({"ip": ip, "wildcard": wildcard, "area": area})

    return pathingType, routes


def getVlanSwitch(lab, name):
    """
    Consulta las vlans existentes en un switch, junto con la interfaz a la que pertenece
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: devuelve un dicionaro con las vlans y las intefaces que pertenece
    """
    node = lab.get_node(name)
    device = connectSwitch("cisco_ios", node.console_host, node.console)
    config = device.send_command("show vlan brief")

    vlans = {}
    vlans_names = {}
    for line in config.split("\n")[2:]:
        match = re.match(r'^s*(\d+)\s+(\S+(?: \d+)?)\s+(\S+)\s(.+)$', line)
        if match:
            vlan_id = match.group(1)
            interfaces = (match.group(4).replace(',', '').split())
            vlans[vlan_id] = interfaces
            vlans_names[vlan_id] = match.group(2)

    return vlans, vlans_names


def getGatewayLinux(lab, name, console_ip, console_port=2375):
    """
    Consulta la Ip del gateway de un dispositivo linux
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: Ip del gateway
    """
    docker_connection = connectDocker(getDockerId(name, lab), console_ip, console_port)
    result = docker_connection.exec_run("route")
    config = result.output.decode("utf-8")
    gateway_match = re.search(r"^default\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", config, re.MULTILINE)
    if gateway_match:
        return gateway_match.group(1)
    else:
        return None


def getIpLinux(lab, name, console_ip, console_port=2375):
    """
    Consulta la Ip  de un equipo linux
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: Ip del equipo
    """
    docker_connection = connectDocker(getDockerId(name, lab), console_ip, console_port)
    result = docker_connection.exec_run("ifconfig eth0")
    config = result.output.decode("utf-8")
    gateway_match = re.search(r"^\s+inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", config, re.MULTILINE)
    if gateway_match:
        return gateway_match.group(1)
    else:
        return None

def getNetmaskLinux(lab, name, console_ip, console_port=2375):
    """
    Consulta la mascasra  de un equipo linux
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: Ip del equipo
    """
    docker_connection = connectDocker(getDockerId(name, lab), console_ip, console_port)
    result = docker_connection.exec_run("ifconfig eth0")
    config = result.output.decode("utf-8")
    gateway_match = re.search(r"netmask\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", config, re.MULTILINE)
    if gateway_match:
        return gateway_match.group(1)
    else:
        return None

def getInfoRouter(lab, name):
    """
    Solicta informacion considerada importante de un router
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """

    node = lab.get_node(name)
    protocol, routes = getProtocolRouter(lab, name)
    data = {"name": name, "machineType": "router", "links": getLinkData(lab.links, lab, name),
            "interfaces": getIpInfoRouter(lab, name), "pathingType": protocol, "routes": routes, "status": node.status}

    return data


def getInfoSwithch(lab, name):
    """
    Solicta informacion considerada importante de un switch
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    node = lab.get_node(name)
    vlans, vlans_names = getVlanSwitch(lab, name)
    data = {"name": name, "machineType": "Switch", "links": getLinkData(lab.links, lab, name),
            "vlans": vlans, "vlans_names": vlans_names, "status": node.status}

    return data


def getInfoLinux(lab, name):
    """
    Solicta informacion considerada importante de un equipo linux
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    node = lab.get_node(name)
    data = {"name": name, "links": getLinkData(lab.links, lab, name), "iface": "eth0",
            "ip": getIpLinux(lab, name, node.console_host), "gateway": getGatewayLinux(lab, name, node.console_host),
            "netmask": getNetmaskLinux(lab, name, node.console_host), "status": node.status}

    return data

def getNatInfo(lab, name):
    link = getLinkData(lab.links, lab, name)
    return {"router": link [0]["destinationName"], "iface": link[0]["destinationInterface"], "nat":  link[0]["interface"]}