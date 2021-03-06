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
import node_exec.filesystem_nodes
import node_exec.json_nodes
import node_exec.qt_file_dialog_nodes
import node_exec.qt_input_nodes
import node_exec.xml_nodes
import node_exec.qt_message_box_nodes
import node_exec.zip_nodes

import os
# Add nodes that are only supported on windows:
if os.name == 'nt':
    import node_exec.windows_nodes