import node_exec.base_nodes
import node_exec.misc_nodes
import node_exec.flow_nodes
import node_exec.inline_nodes

def execute():
    node_exec.misc_nodes.ExecStart.execute()
    var_0xb911ad0_0 = 5
    var_0xb911cd0_0 = 3
    var_0xb9116b0_0 = var_0xb911ad0_0 + var_0xb911cd0_0
    var_0xb911f10_0 = 10
    var_0xb911830_0 = var_0xb911f10_0 + var_0xb911f10_0
    for var_0xb9119d0_0 in range(var_0xb9116b0_0,var_0xb911830_0):
        node_exec.misc_nodes._print(var_0xb9119d0_0)
