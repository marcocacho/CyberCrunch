import sys
import json

from gns3fy import Gns3Connector, Project, Node
from iteration_utilities import unique_everseen

import PrettyPrint
import InformationDevice


def printNodeInfo(lab_name, GNS3_info, node_name):
    gns3_server = Gns3Connector(url=f"http://{GNS3_info['ip']}:{GNS3_info['port']}",
                                user=GNS3_info["user"], cred=GNS3_info["pass"])
    lab: Project = Project(name=lab_name, connector=gns3_server)
    lab.get()
    lab.open()
    nodo: Node = lab.get_node(name=node_name)
    if nodo == None:
        print(f"The node does not exist in the selected {lab_name}.")
    nodo.start()
    # Fata para detectar el nat
    if "docker" == nodo.node_type:
        info = InformationDevice.getInfoLinux(lab, node_name)
        PrettyPrint.prettyLinuxInfo(info)
    elif "qemu" == nodo.node_type:
        info = InformationDevice.getInfoSwithch(lab, node_name)
        PrettyPrint.prettySwitchInfo(info)
    elif "dynamips" == nodo.node_type:
        info = InformationDevice.getInfoRouter(lab, node_name)
        PrettyPrint.prettyRouterInfo(info)


def TransformLinks(name, link):
    return [{"name": name, "interface": link["interface"]},
            {"name": link["destinationName"], "interface": link["destinationInterface"]}]

def getVlans(links, vlans, vlans_names):
    """
    Devuelve las vlans activas en un switch
    :param links: lista de las conexiones
    :param vlans: lista de las vlans del equipo
    :return: lista con todos las vlans en el formato {"number": numero de la vlan o trunk,
                "interfaces": lista con las interfaces}
    """
    new_vlans = []
    infaces_vlans = {}
    for link in links:
        vlan_number = "Trunk"
        vlan_name = "N/A"
        for vlan in vlans:
            if link['interface'] in vlans[vlan]:
                vlan_number = vlan
                vlan_name = vlans_names[vlan]
                break
        new_vlans.append({"number": vlan_number, "name": vlan_name})
        if vlan_number in infaces_vlans:
            infaces_vlans[vlan_number].append(link['interface'])
        else:
            infaces_vlans[vlan_number] = [link['interface']]
    for vlan, iface in infaces_vlans.items():
        for vlans in new_vlans:
            if vlans["number"] == vlan:
                vlans["interfaces"] = iface
                break

    return new_vlans
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
    lab: Project = Project(name=lab_name, connector=gns3_server)
    lab.get()
    lab.open()
    print("The information of the nodes is being collected.")
    lab.start_nodes(poll_wait_time=5)
    network = {"labName": lab_name, "gns3": GNS3_info, "components": {}, "connection_list": []}
    links = []
    for nodo in lab.nodes:
        if "docker" == nodo.node_type:
            info = InformationDevice.getInfoLinux(lab, nodo.name)
            info["template_id"] = nodo.template_id
            info["machineType"] = "docker"
        elif "qemu" == nodo.node_type:
            info = InformationDevice.getInfoSwithch(lab, nodo.name)
            info["vlans"] = getVlans(info["links"], info["vlans"], info["vlans_names"])
            info["template_id"] = nodo.template_id
            info["OS"] = "cisco_ios"
            del info["vlans_names"]
        elif "dynamips" == nodo.node_type:
            info = InformationDevice.getInfoRouter(lab, nodo.name)
            info["template_id"] = nodo.template_id
            info["OS"] = "cisco_ios"
        elif "nat" == nodo.node_type.lower():
            network["nat"] = InformationDevice.getNatInfo(lab, nodo.name)
            continue
        for link in info["links"]:
            tranform_link = TransformLinks(nodo.name, link)
            if not ("nat" == tranform_link[0]["name"].lower() or "nat" == tranform_link[1]["name"].lower()):
                links.append(tranform_link)

        name = info["name"]
        del info["name"]
        del info["links"]
        del info["status"]
        network["components"][name] = info


        # Convert inner lists to sets of tuples to eliminate duplicates
        links_of_tuples = [set(tuple(d.items()) for d in inner_list) for inner_list in links]

        # Convert outer list to set of inner sets to eliminate duplicates
        set_of_links = set(tuple(s) for s in links_of_tuples)

        # Convert sets back to lists of dictionaries
        links = [[dict(t) for t in s] for s in set_of_links]
        network["connection_list"] = links
    print(f"The information collection is complete, and now the data is being written to the file {filename}.")
    with open(filename, "w") as file:
        json.dump(network, file)
    print("JSON file uploaded successfully.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Invalid number of arguments provided.")
    else:
        option = sys.argv[1]
        if option == "print":
            if len(sys.argv) == 5:
                lab_name = sys.argv[2]
                GNS3_info = sys.argv[3]
                node_name = sys.argv[4]
                GNS3 = None
                try:
                    # Convert string dictionary to Python dictionary
                    GNS3 = json.loads(GNS3_info)
                except:
                    print("The provided argument is not a valid dictionary.")
                printNodeInfo(lab_name, GNS3, node_name)
            else:
                print(
                    "Invalid number of arguments provided for print. The arguments valid are lab name, GNS3 info and node name")
        elif option == "export":
            if len(sys.argv) == 5:
                lab_name = sys.argv[2]
                GNS3_info = sys.argv[3]
                filename = sys.argv[4]
                try:
                    # Convert string dictionary to Python dictionary
                    GNS3 = json.loads(GNS3_info)
                except:
                    print("The provided argument is not a valid dictionary.")
                exportLabInfo(lab_name, GNS3, filename)
            else:
                print(
                    "Invalid number of arguments provided for export. The arguments valid are lab name, GNS3 info and filename")
        else:
            print("Invalid option. Available options: print, export")
