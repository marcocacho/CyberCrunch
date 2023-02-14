import virtualbox

def addMachine(pathDisk, name, vbox):
    disk_location = pathDisk.format(name, name)
    hdd = vbox.create_medium(format_p="vdi",
                             location=disk_location,
                             access_mode=virtualbox.library.AccessMode.read_write,
                             a_device_type_type=virtualbox.library.DeviceType.hard_disk)
    #print("Hard Disk name is {}".format(hdd.name))

    machine = vbox.create_machine(name=name,
                                  os_type_id="",
                                  settings_file="",
                                  groups=['/'],
                                  flags="")
    machine.add_storage_controller("SATA", virtualbox.library.StorageBus.sata)

    vbox.register_machine(machine)



if __name__ == '__main__':
    vbox = virtualbox.VirtualBox()
    name = "xubuntuLow"
    name1 = "XubuntuVbox"

    #Añade un vdi y crea una maquina para ese vdi
    #addMachine("/home/marco/Descargas/XubuntuLow.vdi", name, vbox)
    machine = vbox.find_machine(name1)

    session = virtualbox.Session()

    machine.launch_vm_process(session, "gui", [])


