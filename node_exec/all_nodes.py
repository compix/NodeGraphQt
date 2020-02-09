import node_exec.flow_nodes
import node_exec.misc_nodes
import node_exec.convert_nodes
import node_exec.string_nodes
import node_exec.inline_nodes
import node_exec.compare_nodes
import node_exec.operator_nodes
import node_exec.collection_nodes
import node_exec.excel_nodes
import node_exec.csv_nodes
import node_exec.table_nodes
import node_exec.core_nodes

import os
# Add nodes that are only supported on windows:
if os.name == 'nt':
    import node_exec.windows_nodes