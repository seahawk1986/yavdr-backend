import ansible_runner
import json
from concurrent.futures import ThreadPoolExecutor

import pydbus
from gi.repository import GLib

loop = GLib.MainLoop()
interface_name = "org.yavdr.backend.ansible"

bus = pydbus.SessionBus()


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
            <method name='cancelJob'>
                <arg type='s' name='jobID' direction='in'/>
                <arg type='s' name='comment' direction='out' />
            </method>
            <method name='Status'>
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
    inventory = {"all": {"hosts": {"127.0.0.1": {"ansible_connection": "local"}}}}

    def __init__(self, private_data_dir: str) -> None:
        self.private_data_dir = private_data_dir

    def sender(self, data):
        # print("data:", json.dumps(data, indent=2))
        self.send_playbook_event(json.dumps(data, ensure_ascii=False))

    def finisher(self, runner):
        r = runner
        print("finished playbook!")
        print(f"{r.status}: {r.rc}")
        for each_host_event in r.events:
            print(each_host_event["event"])
        print("final status:")
        print(r.stats)

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


if __name__ == "__main__":
    p = PlaybookRunner()
    p.run_playbook("displays.yml")
