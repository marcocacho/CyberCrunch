from gns3fy import Gns3Connector, Project, Node, Link
import time

"""
Esta libreria de funciones consiste en la creacion y  cracion de los proyectos en GNS3.
"""


def openProject(server, name):
    """
    Abre un proyecto de GNS3 en el caso de existir, en caso de no existir crea un nuevo proyecto
    Parametros de entrada:
        + server: conector con el servidor gns3
        + name: nombre del proyecto

    Devuelve:
        lab: un laboratiro de gns3 abierto
    """
    lab = Project(name=name, connector=server)
    try:
        lab.get()
        lab.open()
    except:
        lab.create()

    return lab


def addNode(name, lab, node):
    """
    Añade un nuevo nodo al proyecto GNS3 con el nombre indicado y lo levanta
    :param name: nombre que se le va a otorgar al nodo
    :param lab: laboratorio de gns3 abierto
    :param node: template selecionado de los disponibles
    :return: puerto donde se abrio la consola
    """
    lab.create_node(name=name, template=node)
    time.sleep(1)
    node = lab.get_node(name)
    return node.console

def createLinks(lab, server, node1, node2):
    """
    Crea un enlace entre dos interfaces de dos nodos del proyecto
    :param lab: laboratorio de gns3 abierto
    :param server: conector con el servidor gns3
    :param node1: primer nodo existente en el proyecto que se quiere conectar
    :param node2: segundo nodo existente en el proyecto que se quiere conectar
    :return: None

    nodo1 y nodo2 son diccionarios que contienen el nombre:
     + name: nombre del nodo:
     + interface: interfaz que se quiere usar para conectar (vala nombre corto y largo)
    """
    #Se busca el numero del adaptador al que pertenece la interfaz para ambos nodos
    for port in lab.get_node(node1['name']).ports:
        if port['name'] == node1['interface'] or port['short_name'] == node1['interface']:
            adapter_node1 = port['adapter_number']
            port_number1 = port['port_number']

    for port in lab.get_node(node2['name']).ports:
        if port['name'] == node2['interface'] or port['short_name'] == node2['interface']:
            adapter_node2 = port['adapter_number']
            port_number2 = port['port_number']
    #lista con los nodos ha conectar
    nodes = [
        dict(node_id=lab.get_node(node1['name']).node_id, adapter_number=adapter_node1, port_number=port_number1),
        dict(node_id=lab.get_node(node2['name']).node_id, adapter_number=adapter_node2, port_number=port_number2)]

    #Se crea el enlace entre los nodos
    link = Link(project_id=lab.project_id, connector=server, nodes=nodes)
    link.create()

def getDockerId(name, lab):
    """
    Devuelve el id del docker pedido
    :param name: nombre del nodo
    :param lab: laboratorio de gns3 abierto donde se encuentra el nodo
    :return:
    """
    node = lab.get_node(name)
    return node.properties["container_id"]

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




#Se puede añadir una nueva funcion para añdir maquinas odockers, ejemplo para virtualbox en prueba Gns3

if __name__ == '__main__':
    # Inicializamos la API de GNS3
    gns3_server = Gns3Connector(url="http://127.0.0.1:3080")
    lab: Project = openProject(gns3_server, "test_lab")
    node1 = {"name": "R2",
          "interface": "FastEthernet0/0"}
    node2 = {'name': 'S2',
             'interface': 'Gi0/0'}
    createLinks(lab, gns3_server, node1, node2)
