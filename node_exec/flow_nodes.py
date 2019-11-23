from node_exec.base_nodes import BaseExecuteNode

FLOW_CONTROL_IDENTIFIER = 'Flow Control'

class ForLoopNode(BaseExecuteNode):
    __identifier__ = FLOW_CONTROL_IDENTIFIER
    NODE_NAME = 'For Loop'

    def __init__(self):
        super(ForLoopNode, self).__init__()
        self.add_exec_input('Execute')
        self.loop_body_port = self.add_exec_output('Iteration')
        self.loop_complete_port = self.add_exec_output('Completed')

        self.in_start = self.add_input('Start')
        self.in_end = self.add_input('End')

        self.add_output('Index')


class ForEachLoopNode(BaseExecuteNode):
    __identifier__ = FLOW_CONTROL_IDENTIFIER
    NODE_NAME = 'For Each Loop'

    def __init__(self):
        super(ForEachLoopNode, self).__init__()
        self.add_exec_input('Execute')
        self.loop_body_port = self.add_exec_output('Iteration')
        self.loop_complete_port = self.add_exec_output('Completed')

        self._in = self.add_input('Collection')

        self.add_output('Loop Value')

class WhileLoopNode(BaseExecuteNode):
    __identifier__ = FLOW_CONTROL_IDENTIFIER
    NODE_NAME = 'While Loop'

    def __init__(self):
        super(WhileLoopNode, self).__init__()
        self.add_exec_input('Execute')
        self.loop_body_port = self.add_exec_output('Iteration')
        self.loop_complete_port = self.add_exec_output('Completed')

        self.condition_port = self.add_input('Condition')

class IfNode(BaseExecuteNode):
    __identifier__ = FLOW_CONTROL_IDENTIFIER
    NODE_NAME = 'If'

    def __init__(self):
        super(IfNode, self).__init__()

        self.truePort = self.add_exec_output('True')
        self.falsePort = self.add_exec_output('False')

        self.add_exec_input('Execute')
        self._in = self.add_input('Condition')
