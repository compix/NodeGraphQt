def init():
    global NODES_TO_REGISTER

    try:
        if NODES_TO_REGISTER != None:
            return
    except:
        pass

    NODES_TO_REGISTER = set()