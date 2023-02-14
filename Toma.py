# crear una máquina virtual y configurarla con el archivo VDI agregado
machine_name = "NOMBRE_DE_LA_MAQUINA"
machine = vbox.createMachine("", machine_name, [], 'Linux', '')
machine.attachDevice('SATA', 0, 0, virtualbox.DeviceType_HardDisk, medium)

# agregar un adaptador de red a la máquina virtual
network_adapter = machine.getNetworkAdapter(0)
network_adapter.enabled = True
network_adapter.attachment_type = virtualbox.NetworkAttachmentType_NAT

# guardar los cambios en la configuración de la máquina virtual
machine.saveSettings()

# lanzar la máquina virtual
session = virtualbox.Session()
machine.launchVMProcess(session, "gui", "")
