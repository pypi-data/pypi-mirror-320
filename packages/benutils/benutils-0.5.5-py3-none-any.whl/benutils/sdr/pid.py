# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019-2025
license   GPL v3.0+
brief     PID controller classes.
details   Implement position and velocity PID algorithms.
"""

import time
import logging
import signalslot as ss


class PidCore():
    """Abstract PID controller class, the core part of PID controller classes.
    The following common signals needs to be implemented:
    - in_updated: new data available @ input
    - out_updated: new data available @ output
    - out_saturating: output value is limited by range [omin omax]
    """

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, sp=0.0, omax=1000.0, omin=0.0, osp=0.0, srmax=1.0):
        """The constructor.
        :param kp: proportional gain (float)
        :param ki: integral gain (float)
        :param kd: derivative gain (float)
        :param sp: set-point (float)
        :param omax: upper output range of controller (float)
        :param omin: lower output range of controller (float)
        :param srmax: maximal slew rate (float)
        :param osp: initial output value of controller (float)
        :returns: None
        """
        self._inp = 0.0
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._sp = sp
        self._omax = omax
        self._omin = omin
        self._osp = osp
        self._srmax = srmax
        self._out = osp
        self._freeze = False
        self._sr_enabled = False
        self.in_updated = ss.Signal(args=['value'], name="PID_in")
        self.error_updated = ss.Signal(args=['value'], name="PID_error")
        self.out_updated = ss.Signal(args=['value'], name="PID_out")
        self.out_saturating = ss.Signal(args=['value'], name="PID_sat")
        logging.debug("PID initialized %r", self)

    def reset(self) -> None:
        """Abstract method, sets PID process in its init state.
        The derived class needs to reset all their state variables here.
        :returns: None
        """
        raise NotImplementedError("Method not implemented by derived class")

    def process(self, value, **kwargs) -> float:
        """Computes response of velocity PID algorithm.
        :param value: current value of corrected signal (str or float)
        :returns: the corrected value (float)
        """
        raise NotImplementedError("Method not implemented by derived class")

    def get_input(self):
        """Get current intput value.
        :returns: current input value (float)
        """
        return self._inp

    def get_output(self):
        """Get current output value.
        :returns: current output value (float)
        """
        return self._out

    def set_freeze(self, freeze):
        """Set freeze/unfreeze servo state.
        :param freeze: current freeze state (bool)
        :returns: None
        """
        self._freeze = freeze

    def get_freeze(self) -> bool:
        """Get freeze/unfreeze servo state.
        :returns: current freeze state (bool)
        """
        return self._freeze

    def set_sr_state(self, state):
        """Set slew rate limiter state.
        :param state: current slew rate limiter state (bool)
        :returns: None
        """
        self._sr_enabled = state

    def get_sr_state(self):
        """Get slew rate limiter state.
        :returns: current slew rate limiter state (bool)
        """
        return self._sr_enabled

    def set_kp(self, kp):
        """Sets kp.
        :param kp: proportional gain (float)
        :returns: None
        """
        self._kp = kp

    def get_kp(self):
        """Gets kp.
        :returns: proportional gain (float)
        """
        return self._kp

    def set_ki(self, ki):
        """Sets ki.
        :param ki: integral gain (float)
        :returns: None
        """
        self._ki = ki

    def get_ki(self):
        """Gets ki.
        :returns: integral gain (float)
        """
        return self._ki

    def set_kd(self, kd):
        """Sets kd.
        :param kd: derivative gain (float)
        :returns: None
        """
        self._kd = kd

    def get_kd(self):
        """Gets kd.
        :returns: derivative gain (float)
        """
        return self._kd

    def set_sp(self, sp):
        """Sets sp.
        :param sp: set-point (float)
        :returns: None
        """
        self._sp = sp

    def get_sp(self):
        """Gets sp.
        :returns: set-point (float)
        """
        return self._sp

    def set_osp(self, osp):
        """Sets osp.
        :param osp: output set-point (float)
        :returns: None
        """
        self._osp = osp

    def get_osp(self):
        """Gets osp.
        :returns: output set-point (float)
        """
        return self._osp

    def set_omin(self, omin):
        """Sets omin.
        :param omin: lower output range of controller (float)
        :returns: None
        """
        self._omin = omin

    def get_omin(self):
        """Gets omin.
        :returns: lower output range of controller (float)
        """
        return self._omin

    def set_omax(self, omax):
        """Sets omax.
        :param omax: upper output range of controller (float)
        :returns: Non
        """
        self._omax = omax

    def get_omax(self):
        """Gets omax.
        :returns: upper output range of controller (float)
        """
        return self._omax

    def set_srmax(self, srmax):
        """Set srmax. Slew rate is defined by the variation of output value
        between two samples.
        :param srmax: MAXimal Slew Rate (float)
        :returns: None
        """
        self._srmax = srmax

    def get_srmax(self):
        """Gets omax.
        :returns: MAXimal Slew Rate (float)
        """
        return self._srmax



class PidVelocity(PidCore):
    """Class for the velocity form of the PID controller.
    Inspired by algorithm found on Digital PID Controller from
    www.controlsystemslab.com.
    """

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, sp=0.0, omax=1000.0, omin=0.0, osp=0.0, srmax=1.0):
        """The constructor.
        See PidCore().
        """
        super().__init__(kp, ki, kd, sp, omax, omin, osp, srmax)
        self.set_kp(kp)
        self.set_ki(ki)
        self.set_kd(kd)
        self._er1 = 0.0  # error @ n-1
        self._er2 = 0.0  # error @ n-2

    def reset(self, **kwargs):
        """Overloaded method: reset state variable of PID process.
        :returns: None
        """
        self._er1 = 0.0
        self._er2 = 0.0
        self._out = self._osp
        self._freeze = False
        self.out_updated.emit(value=self._out)

    def process(self, value, **kwargs) -> float:
        """Computes response of velocity PID algorithm.
        :param value: current value of corrected signal (str or float)
        :returns: the corrected value (float)
        """
        saturating = False
        self._inp = float(value)
        # Notify new computation (ie new data at input of PID)
        self.in_updated.emit(value=float(value))
        # If freeze is True return last, and also current, value
        if self._freeze is True:
            return self._out
        # Compute output itself
        er = self._sp - float(value)
        self.error_updated.emit(value=er)
        delta_u = self._k1*er + self._k2*self._er1 + self._k3*self._er2
        un = self._out + delta_u
        # Limit output range (static)
        if un > self._omax:
            un = self._omax
            saturating = True
        elif un < self._omin:
            un = self._omin
            saturating = True
        # Limit output slew rate (dynamic)
        if un < self._out - self._srmax and self._sr_enabled is True:
            un = self._out - self._srmax
        elif un > self._out + self._srmax and self._sr_enabled is True:
            un = self._out + self._srmax
        # Save internal variables for next computation
        self._er2 = self._er1
        self._er1 = er
        self._out = un
        # Notify end of computation (ie new data at output of PID)
        self.out_updated.emit(value=un)
        self.out_saturating.emit(value=saturating)
        # Return result
        return un

    def set_osp(self, osp):
        """Sets osp.
        :param osp: output set-point (float)
        :returns: None
        """
        delta_osp = osp - self._osp
        super().set_osp(osp)
        self._out += delta_osp 

    def set_kp(self, kp):
        """Overloaded method. In the velocity form of the PID controller,
        kp parameter is not directly used. But due to its meaning for PID user,
        it is already used as indirect PID tuning.
        Notes that setting kp involves to recalculate parameters k1 and k2.
        :param kp: proportional gain (float)
        :returns: None
        """
        super().set_kp(kp)
        self._set_k1()
        self._set_k2()

    def set_ki(self, ki):
        """Overloaded method. In the velocity form of the PID controller,
        ki parameter is not directly used. But due to its meaning for PID user,
        it is already used as indirect PID tuning.
        Notes that setting ki involves to recalculate parameter k1.
        :param ki: integral gain (float)
        :returns: None
        """
        super().set_ki(ki)
        self._set_k1()

    def set_kd(self, kd):
        """Overloaded method. In the velocity form of the PID controller,
        kd parameter is not directly used. But due to its meaning for PID user,
        it is already used as indirect PID tuning.
        Notes that setting kd involves to recalculate parameters k1, k2 and k3.
        :param kd: derivative gain (float)
        :returns: None
        """
        super().set_kd(kd)
        self._set_k1()
        self._set_k2()
        self._set_k3()

    def _set_k1(self):
        """Process calculation of k1 parameter. In the velocity form of the PID
        controller, k1 is the sum: kp + ki + kd
        :returns: None
        """
        self._k1 = self._kp + self._ki + self._kd

    def _set_k2(self):
        """Process calculation of k2 parameter. In the velocity form of the PID
        controller, k2 is the sum: -kp - 2*kd
        :returns: None
        """
        self._k2 = -self._kp - 2 * self._kd

    def _set_k3(self):
        """Process calculation of k3 parameter. In the velocity form of the PID
        controller, k3 is equal to: kd
        :returns: None
        """
        self._k3 = self._kd



class PidPosition(PidCore):
    """Class for the position form of the PID controller.
    Inspired by algorithm found on:
    http://read.pudn.com/downloads74/sourcecode/math/271645/IAR/pid.c__.htm
    Specific signals:
    - intSaturated: integrator saturated status (NOT IMPLEMENTED YET)
    """

    EPSILON = 0.0         # Minimum error corrected by I effect
    MAX_INT = 2.0**32     # Limits to avoid overflow
    MAX_I_TERM = 2.0**64  # Limits to avoid overflow

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, sp=0.0, omax=1000.0, omin=0.0, osp=0.0, srmax=1.0, scale=1.0):
        """The constructor.
        See PidCore().
        :param scale: scaling factor, scales PID response (float)
        :returns: None
        """
        super().__init__(kp, ki, kd, sp, omax, omin, osp, srmax)
        self._scale = scale
        self._p_term = 0.0
        self._i_term = 0.0
        self._d_term = 0.0
        self._inp1 = 0.0  # previous data input
        self._ermax = self.MAX_INT / (kp + 1)  # maximal error value
        self._sum_er = 0.0  # integrator
        self._sum_ermax = self.MAX_I_TERM  # maximal integrator value
        self.intSaturated = ss.Signal(args=['flag'], name='Integrator')
        self.intSaturated.emit(flag=False)

    def reset(self, **kwargs):
        """Overloaded method: reset state variable of PID process.
        :returns: None
        """
        self._out = self._osp
        self._inp1 = 0.0
        self._sum_er = 0.0

    def process(self, value, **kwargs):
        """Computes PID response with positional PID algorithm.
        :param value: actual value of corrected signal (float)
        :returns: the corrected value (float)
        """
        saturating = False
        self._inp = value
        # Notify new computation (ie new data at input of PID)
        self.in_updated.emit(value=value)
        # If freeze is True return last, and also current, value
        if self._freeze is True:
            return self._out
        # Compute output itself
        er = self._sp - value
        self.error_updated.emit(value=float(er))
        """
        ## Calculates Pterm and limit error overflow
        if er > self._ermax:
            self._p_term = self._omax
        elif er < -self._ermax:
            self._p_term = self._omin
        else:
            self._p_term = self._kp * er
        """
        self._p_term = self._kp * er
        ## Calculates Iterm and limit integral runaway.
        ## In case of error too small stop integration.
        if abs(er) > self.EPSILON:
            temp = self._sum_er + er
            if temp > self._sum_ermax:
                self.intSaturated.emit(flag=True)
                self._i_term = self.MAX_I_TERM
                self._sum_er = self._sum_ermax
            elif temp < -self._sum_ermax:
                self.intSaturated.emit(flag=True)
                self._i_term = -self.MAX_I_TERM
                self._sum_er = -self._sum_ermax
            else:
                self.intSaturated.emit(flag=False)
                self._sum_er = temp
                self._i_term = self._ki * self._sum_er
        ## Calculates the derivative term.
        ## To avoid 'derivative kick' when a set-point change is made,
        ## derivative action is applied to the mesured variable rather
        ## than to the error.
        self._d_term = self._kd * (self._inp1 - value)
        self._inp1 = value
        ## Calculates PID output
        un = (self._p_term + self._i_term + self._d_term) * self._scale + \
            self._osp
        if un > self._omax:
            un = self._omax
            saturating = True
        elif un < self._omin:
            un = self._omin
            saturating = True
        # Limit output slew rate (dynamic)
        if un < self._out - self._srmax and self._sr_enabled is True:
            un = self._out - self._srmax
        elif un > self._out + self._srmax and self._sr_enabled is True:
            un = self._out + self._srmax
        # Save internal variables for next computation
        self._out = un
        # Notify end of computation (ie new data at output of PID)
        self.out_updated.emit(value=un)
        self.out_saturating.emit(value=saturating)
        # Returns result
        return un

    def set_scale(self, scale):
        """Sets scale.
        :param scale: scaling factor (float)
        :returns: None
        """
        self._scale = scale

    def get_scale(self):
        """Gets scale.
        :returns: scaling factor (float)
        """
        return self._scale


class PidPositionTime(PidPosition):
    """Class for the position form of the PID controller.
    Append timing into account to the base class PidPosition.
    """

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, sp=0.0, omax=0.0, omin=0.0,
                 osp=0.0, scale=1.0):
        """The constructor. More information in the base class PidPosition.
        Details on parameters in the base class.
        :returns: None
        """
        super().__init__(kp, ki, kd, sp, omax, omin, osp, scale)
        self._prevtm = None

    def reset(self, **kwargs):
        """Overloaded method.
        """
        super().reset()
        self._prevtm = None

    def process(self, value, **kwargs):
        """Overloaded method, computes PID response with positional PID
        algorithm and taking into account 'real' timing.
        :param value: actual value of corrected signal (float)
        :returns: the corrected value (float)
        """
        saturating = False
        self._inp = float(value)
        # Compute delta t
        # During the first pass, if 'self._prevtm' is defined as equal to 0.0,
        # dt can be excessively huge and so integrated part too.
        # To avoid the problem, the first pass of PID is only a P computation.
        currtm = time.time()
        if self._prevtm is None:
            dt = 0.0
        else:
            dt = currtm - self._prevtm
        # Notify new computation (ie new data at input of PID)
        self.in_updated.emit(value)
        # Compute output itself
        er = self._sp - value
        # Calculates Pterm and limit error overflow
        """
        if er > self._ermax:
            self._p_term = self._omax
        elif er < -self._ermax:
            self._p_term = self._omin
        else:
            self._p_term = self._kp * er
        """
        self._p_term = self._kp * er
        # Calculates Iterm and limit integral runaway.
        # In case of error too small stop integration.
        if abs(er) > self.EPSILON:
            temp = self._sum_er + er * dt
            if temp > self._sum_ermax:
                self.intSaturated.emit(flag=True)
                self._i_term = self.MAX_I_TERM
                self._sum_er = self._sum_ermax
            elif temp < -self._sum_ermax:
                self.intSaturated.emit(flag=True)
                self._i_term = -self.MAX_I_TERM
                self._sum_er = -self._sum_ermax
            else:
                self.intSaturated.emit(flag=False)
                self._sum_er = temp
                self._i_term = self._ki * self._sum_er
        # Calculates the derivative term.
        # To avoid 'derivative kick' when a set-point change is made,
        # derivative action is applied to the mesured variable rather
        # than to the error.
        if dt > 0:
            self._d_term = self._kd * (self._inp1 - value) / dt
        self._inp1 = value
        # Calculates PID output
        un = (self._p_term + self._i_term + self._d_term) * self._scale + \
            self._osp
        if un > self._omax:
            un = self._omax
            saturating = True
        elif un < self._omin:
            un = self._omin
            saturating = True
        self._out = un
        # Notify end of computation (ie new data at output of PID)
        self.out_updated.emit(value=un)
        self.out_saturating.emit(value=saturating)
        # Save t for next pass
        self._prevtm = currtm
        # Returns result
        return un


# =============================================================================
if __name__ == '__main__':
    KP = 3.0
    KI = 10.0
    KD = 2.0
    SP = 0.0
    OMAX = 10000.0
    OMIN = -10000.0
    OSP = 5000.0
    SRMAX = 500.0

    START = 100
    STOP = 0
    INC = -5

    PID_CTRL1 = PidVelocity(kp=KP, ki=KI, kd=KD, sp=SP, omax=OMAX, omin=OMIN, osp=OSP, srmax=SRMAX)
    PID_CTRL2 = PidPosition(kp=KP, ki=KI, kd=KD, sp=SP, omax=OMAX, omin=OMIN, osp=OSP, srmax=SRMAX)

    OUT1 = [OSP]
    for val in range(START, STOP, INC):
        OUT1.append(PID_CTRL1.process(val))
    OUT2 = [OSP]
    for val in range(START, STOP, INC):
        OUT2.append(PID_CTRL2.process(val))
    OUT_1 = iter(OUT1)
    OUT_2 = iter(OUT2)

    print("")

    PID_CTRL1.reset()
    PID_CTRL2.reset()
    PID_CTRL1.set_sr_state(True)
    PID_CTRL2.set_sr_state(True)

    OUT1_SR = [OSP]
    for val in range(START, STOP, INC):
        OUT1_SR.append(PID_CTRL1.process(val))
    OUT2_SR = [OSP]
    for val in range(START, STOP, INC):
        OUT2_SR.append(PID_CTRL2.process(val))
    OUT1_SR = iter(OUT1_SR)
    OUT2_SR = iter(OUT2_SR)

    print("PidVelocity\tPidPosition\tPidVelocitySR\tPidPositionSR")
    for i in OUT1:
        print(next(OUT_1), "\t", next(OUT_2), "\t", next(OUT1_SR), "\t", next(OUT2_SR))
