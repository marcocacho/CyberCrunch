def prettyRouterInfo(dictionary):
    """
    Imprime los datos proporcionados de un router de manera legible
    :param dictionary: diccionario con los datos de un router
    :return: NONE
    """
    # Print name and type
    print(f"Name: {dictionary['name']}\nType: {dictionary['type']}\nProtocol: {dictionary['protocol']}\n")

    # Print links in a subtable
    links = dictionary['links']
    print("Links:")
    print("{:<20} {:<20} {:<20}".format("Interface", "Destination Name", "Destination Interface"))
    for link in links:
        print("{:<20} {:<20} {:<20}".format(link['interface'], link['destinationName'], link['destinationInterface']))
    print()

    # Print ip in a subtable
    interfaces = dictionary['ip']
    print("Interfaces:")
    print("{:<20} {:<20}".format("Interface", "Ip"))
    for interface in interfaces:
        print("{:<20} {:<20} ".format(interface, interfaces[interface]))


def prettySwitchInfo(dictionary):
    """
    Imprime los datos proporcionados de un switch de manera legible
    :param dictionary: diccionario con los datos de un router
    :return: NONE
    """
    # Print name and type
    print(f"Name: {dictionary['name']}\nType: {dictionary['type']}\n")

    # Print links in a subtable
    links = dictionary['links']
    print("Links:")
    print("{:<20} {:<20} {:<20} {:<20}".format("Interface", "Vlan", "Destination Name", "Destination Interface"))
    for link in links:
        vlan_name = "Trunk"
        for vlan in dictionary['vlans']:
            if link['interface'] in dictionary['vlans'][vlan]:
                vlan_name = vlan
                exit
        print("{:<20} {:<20} {:<20} {:<20}".format(link['interface'], vlan_name, link['destinationName'],

