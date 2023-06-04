import sys
import json

from gns3fy import Gns3Connector, Project, Node

import PrettyPrint
import InformationDevice
def printNodeInfo(lab_name, GNS3_info, node_name):

    gns3_server = Gns3Connector(url=f"http://{GNS3_info['ip']}:{GNS3_info['port']}",
                                user=GNS3_info["user"], cred=GNS3_info["pass"])
    lab: Project = gns3_server.get_project(name=lab_name)
    nodo: Node = lab.get_node(name=node_name)
    if "docker" == nodo.node_type:
        info = InformationDevice.getInfoLinux(lab, node_name)
        PrettyPrint.prettyLinuxInfo(info)
    elif "qemu" == nodo.node_type:
        info = InformationDevice.getInfoSwithch(lab, node_name)
        PrettyPrint.prettySwitchInfo(info)
    elif "dynamips" == nodo.node_type:
        info = InformationDevice.getInfoRouter(lab, node_name)
        PrettyPrint.prettyRouterInfo(info)
def TransformLinks(name, links):
    return [{"name": name, "interface": links["interface"]},
            {"name": links["destinationName"], "interface": links["destinationInterface"]}]
def exportLabInfo(lab_name, GNS3_info, filename):
    """
    Exporta los datos del proyecto a un fichero json para su reutilizacion
    :param lab_name: nombre del laboratorio a exportar
    :param GNS3_info: datos del servidor gns3
    :param filename: nombre del fichero que se quiere alamacenar
    :return:
    """
    global info
    gns3_server = Gns3Connector(url=f"http://{GNS3_info['ip']}:{GNS3_info['port']}",
                                user=GNS3_info["user"], cred=GNS3_info["pass"])
    lab: Project = gns3_server.get_project(name=lab_name)
    network = {"labName": lab_name, "gns3": GNS3_info, "components":[], "connection_list": []}
    for nodo in lab.nodes:
        if "docker" == nodo.node_type:
            info = InformationDevice.getInfoLinux(lab, node_name)
        elif "qemu" == nodo.node_type:
            info = InformationDevice.getInfoSwithch(lab, node_name)
        elif "dynamips" == nodo.node_type:
            info = InformationDevice.getInfoRouter(lab, node_name)

        links = TransformLinks(node_name, info["links"])
        del info["links"]
        network["components"].append(info)
        network["connection_list"].append(links)

    with open(filename, "w") as file:
        json.dump(network, file)
    print("Archivo JSON cargado exitosamente.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Invalid number of arguments provided.")
    else:
        option = sys.argv[1]
        if option == "print":
            if len(sys.argv) == 4:
                lab_name = sys.argv[2]
                GNS3_info = sys.argv[3]
                node_name = sys.argv[4]
                printNodeInfo(lab_name, GNS3_info, node_name)
            else:
                print("Invalid number of arguments provided for print. The arguments valid are lab name, GNS3 info and node name")
        elif option == "export":
            if len(sys.argv) == 4:
                lab_name = sys.argv[2]
                GNS3_info = sys.argv[3]
                filename = sys.argv[4]
                exportLabInfo(lab_name, GNS3_info, filename)
            else:
                print("Invalid number of arguments provided for export. The arguments valid are lab name, GNS3 info and filename")
        else:
            print("Invalid option. Available options: print, export")