from pypods.channel import Channel
from __builtin__ import str
import cothread


class LocChannel(Channel):
    _vtypes = dict(VString=str, VDouble=float)

    def __init__(self, name, typ, initial):
        super(LocChannel, self).__init__(name)
        self.initial, self.typ = self.get_initial_typ(typ, initial)
        self.value = self.initial

    def get_initial_typ(self, typ, initial):
        # convert type string to python type
        if typ is not None:
            assert typ in self._vtypes, \
                "Invalid type {}, expected one of {}"\
                .format(typ, sorted(self._vtypes.keys()))
            typ = self._vtypes[typ]
            if initial is not None:
                # convert initial string to this type
                initial = typ(initial)
        else:
            if initial is not None:
                # convert initial string to python instance and infer type
                initial = eval(initial)
                typ = type(initial)
                if typ == int:
                    # ints should be floats for local channels
                    typ = float
                    initial = typ(initial)
            else:
                # neither specified, default to string and None
                typ = str
        return initial, typ

    def connect(self):
        self.connected = True
        self.writeable = True
        cothread.Spawn(self.do_cb_connection)
        if self.value is not None:
            cothread.Spawn(self.do_cb_value)

    def validate(self, name, typ, initial):
        assert name == self.name, \
            "Channel name {} doesn't match requested name {}"\
            .format(self.name, name)
        initial, typ = self.get_initial_typ(typ, initial)
        assert initial == self.initial, \
            "Channel initial {} doesn't match requested initial {}"\
            .format(self.initial, initial)
        assert typ == self.typ, \
            "Channel type {} doesn't match requested type {}"\
            .format(self.typ, typ)

    def disconnect(self):
        self.connected = False
        self.writeable = False

    def write(self, value):
        # convert to the right type
        value = self.typ(value)
        if self.value != value:
            self.value = value
            # Raise a callback
            self.do_cb_value(value)
