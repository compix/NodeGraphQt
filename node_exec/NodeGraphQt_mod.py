from NodeGraphQt.base.port import Port

def modify_port_connect_to(orig_connect_to):
    """
    Modifies Port.connect_to to 
    - Extend port incompatibility of execution and standard ports (input, output types).
    """
    def connect_to(self, port=None):
        if port == None:
            return

        # Execution ports are not compatible to standard input, output ports:
        if self.is_exec != port.is_exec:
            return

        return orig_connect_to(self, port)

    return connect_to

Port.connect_to = modify_port_connect_to(Port.connect_to)