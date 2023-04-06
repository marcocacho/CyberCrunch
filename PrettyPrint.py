def prettyRouterInfo(dictionary):
    # Print name and type
    print(f"Name: {dictionary['name']}\nType: {dictionary['type']}\n")

    # Print links in a subtable
    links = dictionary['links']
    print("Links:")
    print("{:<20} {:<20} {:<20}".format("Destination Name", "Destination Interface", "Interface"))
    for link in links:
        print("{:<20} {:<20} {:<20}".format(link['destinationName'], link['destinationInterface'], link['interface']))
    print()

    # Print interfaces and IP addresses in a table
    interfaces = dictionary['interfaces']
    ip_addresses = dictionary['ip']
    print("Interfaces:")
    print("{:<20} {:<20} {:<20}".format("Interface", "Status", "IP Address"))
    for interface, status in interfaces.items():
        ip_address = ip_addresses.get(interface, "N/A")
        print("{:<20} {:<20} {:<20}".format(interface, status, ip_address))
    print()

    # Print protocol
    print(f"Protocol: {dictionary['protocol']}\n")
