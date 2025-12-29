import asyncio
import sdbus

INTERFACE_NAME = "org.example.test"

class ExampleInterface(
    sdbus.DbusInterfaceCommonAsync,
    interface_name=INTERFACE_NAME,
):
    def __init__(self, system_bus):
         self.systembus = system_bus
         super().__init__()
    @sdbus.dbus_method_async(
        input_signature="",
        result_signature="s",
        flags=sdbus.DbusUnprivilegedFlag,
    )
    async def unprivileged(self) -> str:
        """Returns 'unprivileged' when called.
		   The flag sdbus.DbusUnprivilegedFlag allows it to be called by everyone.
		"""
        return "unprivileged"

    @sdbus.dbus_method_async(
        input_signature="",
        result_signature="s",
    )
    async def privileged(self) -> str:
        """Returns 'privileged' when called. Only callable by the owner of the service or root"""
        return "privileged"

    @sdbus.dbus_property_async("s")
    def read_string(self) -> str:
        """A read-only property returning 'Test'."""
        return "Test"

    @sdbus.dbus_signal_async("as")
    def str_signal(self) -> list[str]:
        """A signal emitting a list of strings."""
        raise NotImplementedError  # This function should be triggered elsewhere


async def main():
    # Open the system bus (requires root privileges)
    system_bus = sdbus.sd_bus_open_system()
    # Request a name on the system bus
    await system_bus.request_name_async(INTERFACE_NAME, 0)

    # Create and export the interface on the system bus
    interface = ExampleInterface(system_bus=system_bus)
    interface.export_to_dbus("/", system_bus)

    print("D-Bus service running on the system bus... Press Ctrl+C to stop.")

    await asyncio.sleep(5)

    # emit a signal
    interface.str_signal.emit(["test", "1", "2", "3"])

    # Keep the event loop running
    await asyncio.Future()  # Runs forever

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
	    pass
