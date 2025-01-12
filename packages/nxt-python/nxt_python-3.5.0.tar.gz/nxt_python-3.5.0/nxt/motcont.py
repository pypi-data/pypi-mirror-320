# nxt.motcont module -- Interface to Linus Atorf's MotorControl NXC
# Copyright (C) 2011  Marcus Wanner
# Copyright (C) 2021  Nicolas Schodet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import time
from collections.abc import Iterable
from threading import Lock
from typing import Union

import nxt.brick
import nxt.error
import nxt.motor

__all__ = ["MotCont"]


def _power(power: int) -> str:
    pw = abs(power)
    if power < 0:
        pw += 100
    return f"{pw:03}"


def _tacho(tacholimit: int) -> str:
    return f"{tacholimit:06}"


class MotCont:
    """Interface to MotorControl.

    This class provides an interface to Linus Atorf's MotorControl NXC program. It is
    a wrapper which follows the `MotorControl documentation`_ and provides command
    strings and timing intervals as dictated there.

    To use this module, you will need to put ``MotorControl22.rxe`` on your NXT brick.
    It can be built using NXC and the corresponding source can be found at
    https://github.com/schodet/MotorControl.

    Use :func:`MotCont.start` to start the program. You can also start it manually my
    using the menu on the brick. When your script exits, it would be a good idea to do
    :func:`MotCont.stop`.

    Original `MotorControl site`_ is no longer available, but you can still find
    a mirror on web archive.

    .. _MotorControl documentation:
        https://github.com/schodet/MotorControl/blob/master/doc/MotorControl.md
    .. _MotorControl site:
        http://www.mindstorms.rwth-aachen.de/trac/wiki/MotorControl
    """

    def __init__(self, brick: nxt.brick.Brick) -> None:
        self._brick = brick
        self._is_ready_lock = Lock()
        self._last_is_ready = time.time() - 1
        self._last_cmd: dict[nxt.motor.Port, float] = {}

    def _interval_is_ready(self) -> None:
        delay = 0.010
        diff = time.time() - self._last_is_ready
        if diff < delay:
            time.sleep(delay - diff)

    def _interval_motors(self, ports: Iterable[nxt.motor.Port]) -> None:
        delay = 0.015
        now = time.time()
        diff = delay
        for port in ports:
            if port in self._last_cmd:
                diff = min(diff, now - self._last_cmd[port])
        if diff < delay:
            time.sleep(delay - diff)

    def _record_time_motors(self, ports: Iterable[nxt.motor.Port]) -> None:
        now = time.time()
        for port in ports:
            self._last_cmd[port] = now

    def _decode_ports(
        self, ports: Union[nxt.motor.Port, Iterable[nxt.motor.Port]], max_ports: int
    ) -> tuple[frozenset[nxt.motor.Port], str]:
        if isinstance(ports, Iterable):
            ports = frozenset(ports)
        else:
            ports = frozenset((ports,))
        mapping = {
            frozenset((nxt.motor.Port.A,)): "0",
            frozenset((nxt.motor.Port.B,)): "1",
            frozenset((nxt.motor.Port.C,)): "2",
            frozenset((nxt.motor.Port.A, nxt.motor.Port.B)): "3",
            frozenset((nxt.motor.Port.A, nxt.motor.Port.C)): "4",
            frozenset((nxt.motor.Port.B, nxt.motor.Port.C)): "5",
            frozenset((nxt.motor.Port.A, nxt.motor.Port.B, nxt.motor.Port.C)): "6",
        }
        if ports not in mapping or len(ports) > max_ports:
            raise ValueError("invalid combination of ports")
        return ports, mapping[ports]

    def cmd(
        self,
        ports: Union[nxt.motor.Port, Iterable[nxt.motor.Port]],
        power: int,
        tacholimit: int,
        speedreg: bool = True,
        smoothstart: bool = False,
        brake: bool = False,
    ) -> None:
        """Send a controlled motor command to MotorControl.

        :param ports: Port or ports to control, use one of the port identifiers, or
           an iterable returning one or two of them.
        :param power: Speed or power, -100 to 100.
        :param tacholimit: Position to drive to, 1 to 999999.
        :param speedreg: ``True`` to enable regulation.
        :param smoothstart: ``True`` to enable smooth start.
        :param brake: ``True`` to hold brake at end of movement.

        The motors on the selected ports must be idle, i.e. they can not be carrying out
        any other movement commands. If this should happen, the NXT will indicate this
        error by a signal (high and low beep) and will drop the message. To find out if
        a motor is ready to accept new commands, use the :meth:`is_ready` method. It is
        also possible to stop the motor before using :meth:`set_output_state` method.

        In certain situations, :meth:`set_output_state` method should be used instead.
        See :meth:`set_output_state` for more details.
        """
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 2)
        self._interval_motors(ports)
        mode = str(0x01 * int(brake) + 0x02 * int(speedreg) + 0x04 * int(smoothstart))
        command = "1" + strports + _power(power) + _tacho(tacholimit) + mode
        self._brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)

    def reset_tacho(
        self, ports: Union[nxt.motor.Port, Iterable[nxt.motor.Port]]
    ) -> None:
        """Reset NXT tacho count.

        :param ports: Port or ports to control, use one of the port identifiers, or
           an iterable returning one to three of them.
        """
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 3)
        command = "2" + strports
        self._brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)

    def is_ready(self, port: Union[nxt.motor.Port, Iterable[nxt.motor.Port]]) -> bool:
        """Determine the state of a single motor.

        :param port: Port to control, use one of the port identifiers, or an iterable
           returning one of them.
        :return: ``True`` if the motor is ready to accept new commands.
        """
        self._interval_is_ready()
        ports, strports = self._decode_ports(port, 1)
        with self._is_ready_lock:
            command = "3" + strports
            self._brick.message_write(1, command.encode("ascii"))
            time.sleep(0.015)  # 10ms pause from the docs seems to not be adequate
            reply = self._brick.message_read(0, 1, True)[1]
            if chr(reply[0]) != strports:
                raise nxt.error.ProtocolError("wrong port returned from ISMOTORREADY")
        self._last_is_ready = time.time()
        return bool(int(chr(reply[1])))

    def set_output_state(
        self,
        ports: Union[nxt.motor.Port, Iterable[nxt.motor.Port]],
        power: int,
        tacholimit: int,
        speedreg: bool = True,
    ) -> None:
        """Send a classic motor command to MotorControl.

        :param ports: Port or ports to control, use one of the port identifiers, or
           an iterable returning one or two of them.
        :param power: Speed or power, -100 to 100.
        :param tacholimit: Position to drive to, 1 to 999999, or 0 for unlimited.
        :param speedreg: ``True`` to enable regulation.

        This is similar to the regular :meth:`nxt.brick.Brick.set_output_state` method,
        but informs the MotorControl program to avoid any unwanted side effect.

        When to use :meth:`set_output_state` instead of :meth:`cmd`:

        - when tacholimit is 0 for unlimited movement,
        - or when the motor must coast (spin freely) after tacholimit has been reached
          (it will overshoot then),
        - or when you want to be able to change the power of a running motor at runtime.

        Also use this method to stop a currently running motor:

        - To stop and let a motor spin freely (coasting), use `power` 0 and no
          regulation.
        - To stop and hold the current position (brake), use `power` 0 with regulation.
        """
        self._interval_is_ready()
        ports, strports = self._decode_ports(ports, 2)
        self._interval_motors(ports)
        command = "4" + strports + _power(power) + _tacho(tacholimit) + str(speedreg)
        self._brick.message_write(1, command.encode("ascii"))
        self._record_time_motors(ports)

    def start(self, version: int = 22) -> None:
        """Start the MotorControl program on the brick.

        :param version: Version to start, default to 22 (version 2.2).

        It needs to already be present on the brick's flash and named
        ``MotorControlXX.rxe``, where `XX` is the version number passed as the version
        argument.

        .. warning:: When starting or stopping a program, the NXT firmware resets every
           sensors and motors.
        """
        try:
            self._brick.stop_program()
            time.sleep(1)
        except nxt.error.DirectProtocolError:
            pass
        self._brick.start_program("MotorControl%d.rxe" % version)
        time.sleep(0.1)

    def stop(self) -> None:
        """Stop the MotorControl program.

        All this actually does is to stop the currently running program.

        .. warning:: When starting or stopping a program, the NXT firmware resets every
           sensors and motors.
        """
        self._brick.stop_program()
