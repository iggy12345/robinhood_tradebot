from multiprocessing import Process, Queue
from queue import Full, Empty

from message import MessageHandler


class QSM(Process):
    def __init__(self, name: str, msg_list: list = None):
        super().__init__()
        self.is_exitting = False

        self.mappings = {}
        self.setup_states()

        self.msg_map = {}
        self.setup_msg_mappings(msg_list)

        self.handler = None  # MessageHandler(name, self.msg_map)
        self.states = Queue()
        self.append_state('init')

    def run(self) -> None:
        self.handler = MessageHandler(self.name, self.msg_map)  # Because otherwise we can't join from 'final'
        while not self.is_exitting:
            try:
                s = self.states.get_nowait()
                # print('Going to {}'.format(s['state']))
                if s['payload'] is not None:
                    self.mappings[s['state']](s['payload'])
                else:
                    self.mappings[s['state']]()
            except Empty as _:
                self.mappings['idle']()

    def setup_msg_mappings(self, msg_list: list):
        """Sets up the self.msg_map dictionary, mapping message titles to state names,
        by default, appends '_msg' to msg_list entries"""
        for m in msg_list:
            self.msg_map[m] = m + '_msg'

    def setup_states(self):
        """Sets up the self.mappings dictionary, mapping state names to state methods,
        by default 'init', 'idle', 'exit', and 'final' states are set up."""
        self.mappings['init'] = self.initial_state
        self.mappings['idle'] = self.idle_state
        self.mappings['exit'] = self.exit_state
        self.mappings['final'] = self.final_state

    def append_state(self, state: str, payload: object = None):
        try:
            # print('Appending {}'.format(state))
            self.states.put_nowait({'state': state, 'payload': payload})
        except Full as _:
            print('{} state queue is full, skipping {}'.format(self.name, state))

    def append_states(self, states: list, payloads: list = None):
        for i, s in enumerate(states):
            p = payloads[i] if payloads is not None else None
            self.append_state(s, p)

    def initial_state(self):
        """This is the first state to execute, always"""
        pass

    def idle_state(self):
        """This is the state the is triggered when the state machine has nowhere to go to."""
        m = self.handler.receive()
        if m is not None:
            self.append_state(self.msg_map[m.title], m)

    def exit_state(self):
        """This stateis triggered when the qsm should exit, enqueues the 'final' state"""
        # print('Exitting')
        self.append_state('final')

    def final_state(self):
        """This is the final state to execute, always"""
        self.is_exitting = True
        self.handler.join()


if __name__ == '__main__':
    from message import Message


    class TestQSM(QSM):
        def __init__(self, name: str):
            super().__init__(name, ['test'])

        def setup_states(self):
            super().setup_states()
            self.mappings['test_msg'] = self.test_msg

        def initial_state(self):
            self.handler.send(Message('test'))

        def test_msg(self, msg: Message):
            print('This is the test message')
            self.append_state('exit')


    print('Testing QSM capabilities')
    t = TestQSM('test')
    t.start()
    t.join()

    exit(0)