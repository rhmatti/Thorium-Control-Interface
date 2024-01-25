from functools import partial
from PyQt5 import QtWidgets
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall

from thorium.control.clients.qtui.QCustomSpinBox import QCustomSpinBox


class HV500BenderClient(QtWidgets.QWidget):
    """Client for bender electrode voltage control through HV500 supply."""

    _vmax = 300
    _vmin = -300

    def __init__(self, reactor, parent=None):
        super(HV500BenderClient, self).__init__()
        self.setWindowTitle("HV500 Bender Client")
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.reactor = reactor

        self.index = [kk for kk in range(1, 11)] # 10 bender electrodes
        self._loop_updates = []
        for kk in self.index:
            loop = LoopingCall(partial(self._update_voltage, kk))
            self._loop_updates.append(loop)

        self.v_names = {1:"Q1", 2:"Q2", 3:"Q3", 4:"Q4", 5:"TL", 6:"TR", 7:"BL", 8:"BR", 9:"AL", 10:"AR"}

        self.v_location = {1:("b", 15), 2:("b", 12), 3:("b", 13), 4:("l", 15), 5:("l", 14),
                      6:("b", 16), 7:("l", 16), 8:("l", 12), 9:("l", 13), 10:("b", 14)}

        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Connects to LabRAD and initializes the GUI.

        GUI init is placed in this function rather than __init__,
        because this function runs async, and GUI initialization should happen after connect.
        """
        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync(name="HV500 Bender Client")

        self.bender_server = yield self.cxn.hv500_bender_server
        self.loading_server = yield self.cxn.hv500_loading_server

        self.initializeGUI()
        yield self._update_widgets()
        self._connect_widgets()

    def _get_qbox_index(self, index):
        """Returns a QGroupBox instance that contains controls for a output index."""
        supply, channel = self.v_location[index]
        qbox = QtWidgets.QGroupBox(f"{self.v_names[index]}")
        sub_layout = QtWidgets.QGridLayout()
        qbox.setLayout(sub_layout)

        vmon = QtWidgets.QLabel(self._get_vmon_text(index, 0))
        self._vmon_labels.append(vmon)
        sub_layout.addWidget(vmon, 0, 0, 1, 2)

        vlabel = QtWidgets.QLabel(f"{supply}, {channel}")
        sub_layout.addWidget(vlabel, 1, 0, 1, 2)

        vset = QCustomSpinBox("Setpoint (V): ", (self._vmin, self._vmax))
        vset.spinLevel.setDecimals(1)
        vset.setStepSize(1)
        self._vset_spinboxes.append(vset)
        sub_layout.addWidget(vset, 2, 0, 1, 2)

        return qbox

    def initializeGUI(self):
        layout = QtWidgets.QGridLayout()

        qbox = QtWidgets.QGroupBox("HV500 Bender Client")
        sub_layout = QtWidgets.QGridLayout()
        qbox.setLayout(sub_layout)
        layout.addWidget(qbox, 0, 0)

        self._vmon_labels = []
        self._vset_spinboxes = []

        for kk in self.index:
            qbox_index = self._get_qbox_index(kk)
            if kk <= 8:
                sub_layout.addWidget(qbox_index, 0, kk - 1)
            else:
                sub_layout.addWidget(qbox_index, 1, kk - 1 - 8)
            self._begin_mon_update(kk)

        self.setLayout(layout)

    def _connect_widgets(self):
        """Connects widget events with the corresponding functions."""
        for kk in self.index:
            self._vset_spinboxes[kk - 1].spinLevel.valueChanged.connect(
                partial(self._vset_changed, kk)
            )

    def _begin_mon_update(self, index):
        """Sets the update period of the voltage monitor of a index to 5 seconds."""
        self._loop_updates[index - 1].start(5)

    @inlineCallbacks
    def _update_voltage(self, index, recall=False):
        """Updates the voltage of a index from the server."""
        supply, channel = self.v_location[index]
        if supply == "b":
            vmon = yield self.bender_server.get_voltage(channel)
        elif supply == "l":
            vmon = yield self.loading_server.get_voltage(channel)

        self._vmon_labels[index - 1].setText(self._get_vmon_text(index, vmon))
        if recall: return vmon

    def _get_vmon_text(self, index, voltage):
        """Returns label text for a voltage monitor label."""
        voltage = round(voltage, 1) # round voltage to 1 dp
        return f"Actual V: {voltage} V"

    @inlineCallbacks
    def _update_widgets(self):
        """Updates all voltages from the server."""
        for kk in self.index:
            v_init = yield self._update_voltage(kk, recall=True)
            self._vset_spinboxes[kk - 1].setValues(round(v_init))

    @inlineCallbacks
    def _vset_changed(self, index, value):
        """Changes the server voltage setpoint when the spinbox is changed."""
        supply, channel = self.v_location[index]
        if supply == "b":
            yield self.bender_server.set_voltage(channel, value)
        elif supply == "l":
            yield self.loading_server.set_voltage(channel, value)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtWidgets.QApplication([])
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    client = HV500BenderClient(reactor)
    client.show()
    reactor.run()
