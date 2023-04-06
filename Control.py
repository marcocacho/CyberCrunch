from NetworkDeploment.ConfigureRouter import connectRouter
from NetworkDeploment.ConfigureSwitch import connectSwitch
import re


def manageMachines(name, lab, action):
    """
    Funcion encargada de modifica una maquina de un proyencto de gns3
    :param name: nombre del nodo de la red sobre el que se quiere actuar
    :param lab: laboratorio de gns3
    :param action: accion que se quiere realizar (start, stop, reload, suspend, delete, status)
    :return: None
    """
    node = lab.get_node(name)
    if node is not None:
        action_dict = {"start": node.start,
                       "stop": node.stop,
                       "reload": node.reload,
                       "suspend": node.suspend,
                       "delete": node.delete}
        select = action_dict.get(action)
        if select is not None:
            select()
        else:
            print("No se encontro accion " + action)
    else:
        print("No existe el nodo seleccionado")


def getLinkData(links_global, lab, name):
    """
    Consulta el nodo, interfaces con el que esta conectado el nodo dado
    :param link: lista de enlace
    :param lab: lboratorio de gns3
    :param name: nombre del nodo
    :return: diccionario con (interface, destinationInterface, destinationName)
    """
    allData = []
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
            allData.append(data)

    return allData


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
            id = match.group(1)
            interfaces = (match.group(4).replace(',', '').split())
            vlans[id] = interfaces

    return vlans


def getInfoRouter(name, lab):
    """
    Solicta informacion considerada importante de un router
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    data = {"name": name, "type": "router"}
    data["links"] = getLinkData(lab.links, lab, name)
    data["ip"] = getIpInfoRouter(lab, name)
    data["protocol"] = getProtocolRouter(lab, name)

    return data


def getInfoSwithch(name, lab):
    """
    Solicta informacion considerada importante de un switch
    :param name: nombre del nodo
    :param lab: laboratorio de gns3
    :return: diccionario con los datos
    """
    data = {"name": name, "type": "router"}
    data["links"] = getLinkData(lab.links, lab, name)
    data["vlans"] = getVlanSwitch(lab, name)

    return data
