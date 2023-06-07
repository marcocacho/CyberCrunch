def prettyRouterInfo(dictionary):
    """
    Imprime los datos proporcionados de un router de manera legible
    :param dictionary: diccionario con los datos de un router
    :return: None
    """
    # Print name and type
    print(
        f"Name: {dictionary['name']}\nType: {dictionary['machineType']}\nStatus: {dictionary['status']}\n")

    # Print links in a subtable
    links = dictionary['links']
    print("Links:")
    print("{:<20} {:<20} {:<20}".format("Interface", "Destination Name", "Destination Interface"))
    for link in links:
        print("{:<20} {:<20} {:<20}".format(link['interface'], link['destinationName'], link['destinationInterface']))
    print()

    # Print ip in a subtable
    print("Interfaces:")
    print("{:<20} {:<20} {:<20}".format("Interface", "Ip", "Netmask"))
    for iface in dictionary["interfaces"]:
        print("{:<20} {:<20} {:<20}".format(iface["iface"],iface["ip"], iface["netmask"]))
    print()

    print(f"Pathing: {dictionary['pathingType']}")
    print("Routes:")
    print("{:<20} {:<20} {:<20}".format("Area", "Ip", "Wildcard"))
    for route in dictionary["routes"]:
        print("{:<20} {:<20} {:<20}".format(route["area"], route["ip"], route["wildcard"]))

def prettySwitchInfo(dictionary):
    """
    Imprime los datos proporcionados de un switch de manera legible
    :param dictionary: diccionario con los datos de un router
    :return: None
    """
    # Print name and type
    print(f"Name: {dictionary['name']}\nType: {dictionary['machineType']}\nStatus: {dictionary['status']}\n")

    # Print links in a subtable
    print("Links:")
    print("{:<20} {:<20} {:<20} {:<20} {:<20}".format("Interface", "Vlan", "Vlan Name", "Destination Name", "Destination Interface"))
    for link in dictionary['links']:
        vlan_number = "Trunk"
        vlan_name = "N/A"
        for vlan in dictionary['vlans']:
            if link['interface'] in dictionary['vlans'][vlan]:
                vlan_number = vlan
                vlan_name = dictionary["vlans_names"][vlan]
                break
        print("{:<20} {:<20} {:<20} {:<20} {:<20}".format(link['interface'], vlan_number, vlan_name, link['destinationName'],
                                                   link['destinationInterface']))


def prettyLinuxInfo(dictionary):
    """
    Imprime los datos proporcionados de un equipo Linux de manera legible
    :param dictionary: diccionario con los datos de un router
    :return: None
    """
    # Print name and type
    print(f"Name: {dictionary['name']}\nType: {dictionary['machineType']}\nStatus: {dictionary['status']}\n")
    print(f"Ip: {dictionary['ip']}\tNetmask:{dictionary['netmask']}\tGateway: {dictionary['gateway']}\n")

    links = dictionary['links']
    print("Links:")
    print("{:<20} {:<20} {:<20}".format("Interface", "Destination Name", "Destination Interface"))
    for link in links:
        print("{:<20} {:<20} {:<20}".format(link['interface'], link['destinationName'], link['destinationInterface']))
    print()
