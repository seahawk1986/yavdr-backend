import asyncio
import sdbus

# Open the system bus (requires root privileges)
system_bus = sdbus.sd_bus_open_system()


class ExampleInterface(
    sdbus.DbusInterfaceCommonAsync,
    interface_name="de.yavdr.SystemBackend",
):
    @sdbus.dbus_method_async(
        input_signature="",
        result_signature="s",
        method_name="Foo",
        flags=sdbus.DbusUnprivilegedFlag,
    )
    async def foo(self) -> str:
        """Returns 'spam' when called."""
        return "spam"

    @sdbus.dbus_property_async("s")
    def read_string(self) -> str:
        """A read-only property returning 'Test'."""
        return "Test"

    @sdbus.dbus_signal_async("as")
    def str_signal(self) -> list[str]:
        """A signal emitting a list of strings."""
        raise NotImplementedError  # This function should be triggered elsewhere


async def main():
    # Request a name on the system bus
    await system_bus.request_name_async("de.yavdr.SystemBackend", 0)

    # Create and export the interface
    interface = ExampleInterface()
    interface.export_to_dbus("/", system_bus)

    print("D-Bus service running on the system bus... Press Ctrl+C to stop.")

    # Keep the event loop running
    await asyncio.Future()  # Runs forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
