#!/usr/bin/env python3
import time
from pydbus.generic import signal
from pydbus import SessionBus
from gi.repository import GLib
import random
loop = GLib.MainLoop()
interface_name = "org.yavdr.backend.ansible"
bus = SessionBus()


class Server_XML(object):
    """
    Server_XML definition.
    Emit / Publish a signal that is a random integer every second
    type='i' for integer. 
    """
    dbus = """
    <node>
        <interface name="org.example.project_1.server_1">
            <signal name="app_1_signal">
                <arg type='a{sd}'/>
            </signal>
        </interface>
    </node>
    """
    app_1_signal = signal()

def repeating_timer():
    """Generate random integer between 0 and 100 and emit over Session D-Bus
    return True to keep the GLib timer calling this function once a second."""
    random_integer = random.randint(0,100)
    t = time.time()
    print(random_integer, t)
    emit.app_1_signal({
        "value": random_integer,
        "timestamp": t
        })
    return True


if __name__=="__main__":
    # Setup server to emit signals over the DBus
    emit = Server_XML()
    bus.publish(interface_name, emit)
    # Setup repeating timer
    GLib.timeout_add_seconds(interval=1, function=repeating_timer)
    # Run loop with graceful ctrl C exiting.
    try:
        loop.run()
    except KeyboardInterrupt as e:
        loop.quit()
        print("\nExit by Control C")