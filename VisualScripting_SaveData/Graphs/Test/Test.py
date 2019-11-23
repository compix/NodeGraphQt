import node_exec.base_nodes
import node_exec.misc_nodes
import node_exec.flow_nodes
import node_exec.inline_nodes

def execute():
    node_exec.misc_nodes.ExecStart.execute()
    var_0x1b25be53948 = 5
    var_0x1b25be54308 = 3
    var_0x1b25be48c88 = var_0x1b25be53948 + var_0x1b25be54308
    var_0x1b25be544c8 = 10
    var_0x1b25be48ec8 = var_0x1b25be544c8 + var_0x1b25be544c8
    for var_0x1b25be518c8 in range(var_0x1b25be48c88,var_0x1b25be48ec8):
        node_exec.misc_nodes._print(var_0x1b25be518c8)
