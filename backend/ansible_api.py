import ansible_runner
import json
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import pydbus
from gi.repository import GLib

loop = GLib.MainLoop()
interface_name = "org.yavdr.backend.ansible"


class PlaybookRunner(object):
    """
    This class provides a dbus interface to run ansible playbooks.
    It emits DBus signals to allow other services to react
    on the playbook output and results.
    """

    dbus = f"""
    <node>
        <interface name="{interface_name}.PlaybookRunner">
            <method name='addJob'>
                <arg type='s' name='playbook' direction='in'/>
                <arg type='s' name='options' direction='in'/>
                <arg type='s' name='jobID' direction='out' />
                <arg type='s' name='comment' direction='out' />
            </method>
            <!--
            <method name='cancelJob'>
                <arg type='s' name='jobID' direction='in'/>
                <arg type='b' name='result' direction='out' />
                <arg type='s' name='comment' direction='out' />
            </method>
            -->
            <method name='status'>
                <arg type='a{{ss}}' name='jobs' direction='out' />
                <arg type='s' name='runningJob' direction='out' />
                <arg type='s' name='comment' direction='out' />
            </method>
            <signal name="playbook_event">
                <arg type='a{{ss}}'/>
            </signal>
            <signal name="playbook_finished">
                <arg type='a{{ss}}'/>
            </signal>
        </interface>
    </node>
    """
    send_playbook_event = pydbus.generic.signal()
    send_playbook_finished = pydbus.generic.signal()
    inventory = {
        "all": {"hosts": {"127.0.0.1": {"ansible_connection": "local"}}}
    }

    def __init__(self, private_data_dir: str) -> None:
        self.private_data_dir = private_data_dir
        self.queue = ThreadPoolExecutor(max_workers=1)
        self.jobs = deque()

    def sender(self, data):
        # print("data:", json.dumps(data, indent=2))
        self.send_playbook_event(json.dumps(data, ensure_ascii=False))

    def finisher(self, runner):
        r = runner
        print("finished playbook!")
        data = {
            "status": r.status,
            "rc": r.rc,
            "events": [e for e in r.events],
            "stats": r.stats,
        }
        self.send_playbook_finished(json.dumps(data), ensure_ascii=False)
        f = self.jobs.popleft()
        print("is done:", f.done())

    def run_playbook(self, playbook):
        self.current_playbook = playbook
        r = ansible_runner.run(
            private_data_dir="/home/alexander/yavdr-ansible",
            playbook=playbook,
            inventory=self.inventory,
            event_handler=self.sender,
            finished_callback=self.finisher,
            quiet=True,
            json_mode=True,
        )
        print(f"{r.status}: {r.rc}")
        for each_host_event in r.events:
            print(each_host_event["event"])

    def addJob(self, playbook):
        self.jobs.add(self.queue.submit(self.run_playbook, playbook))


if __name__ == "__main__":
    bus = pydbus.SessionBus()
    bus.publish("org.freedesktop.Notifications", PlaybookRunner())
    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit
    # p = PlaybookRunner()
    # p.run_playbook("displays.yml")
