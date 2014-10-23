from fluidity import StateMachine, state
from rootio import config
from rootio.radio import Program, Station

__author__ = 'kenneth'

#This code does not work yet but it can give an idea of my direction of though 

# dummy_menu = {
#     'program': 1, 'station': 1,
#     'actions': {
#         'call_host': {'listen_to': 1, 'related_media': [], 'order': 0},
#         'play_music': {'listen_to': 2, 'related_media': [], 'order': 1},
#         'hang_up': {'listen_to': 9, 'order': 2}
#     }
# }


class Menu(StateMachine):
    actions = __import__(getattr(config, 'TEL_ACTIONS', 'actions'))

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__()
        self.states = []
        self.ivr_choice = -1
        self.initial_state = None
        self.menu = self.loads(kwargs.pop('menu'))
        self.program = Program.query.filter_by(id=self.menu['program']).first()
        self.station = Station.query.filter_by(id=self.menu['station']).first()
        self.call_params = self._process_menu_for_call_params()

    def _process_menu_for_actions(self):
        _actions = self.menu['actions']
        for action in _actions:
            func = getattr(self.actions, action)
            kwargs = _actions[action]
            order = kwargs.pop('order')
            self.states.insert(order, action)
            setattr(self, action, func(self, **kwargs))

    def _add_process_menu_for_call_params(self):
        return self.menu['call_prams'] #Todo: Make this work

    def setup(self):
        for action in self.states:
            self.add_state(action)

    def listen_to_choice(self):
        # We try to listen and set the choice selected by host. And return that as the next step in the transition
        self.ivr_choice = -1  #Todo: This is where we listen and tell what the user pressed

    state('listen_to_choice')

    def create_transitions(self):
        self.initial_state = self.states[0]
        end_state = self.states[self.ivr_choice]
        if not self.current_state:
            self.add_transition(self.initial_state, 'listen_to_choice', end_state)
            self.current_state = end_state
        else:
            self.add_transition(self.current_state, 'listen_to_choice', end_state)