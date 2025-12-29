import logging
from pathlib import Path
from pydantic import BaseModel

NET_BASE_PATH = Path("/sys/class/net")
ACPI_DEVICE_BASE_PATH = Path("/sys/bus/acpi/devices")
PROC_ACPI_PATH = Path('/proc/acpi/wakeup')

class ACPIWakeupInfo(BaseModel):
    name: str
    enabled: bool

def get_nic_acpi_wakeup_map() -> dict[str, ACPIWakeupInfo]:
    result: dict[str, ACPIWakeupInfo] = {}

    acpi_wakeup: dict[str, ACPIWakeupInfo] = {}
    try:
        for line in PROC_ACPI_PATH.read_text().splitlines()[1:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            name = parts[0]
            status = parts[2].lstrip("*")
            pci = parts[3] if parts[3].startswith("pci:") else None
            if pci:
                acpi_wakeup[pci.replace("pci:", "")] = ACPIWakeupInfo(name=name, enabled=True if status == "enabled"  else False)
    except FileNotFoundError:
        logging.exception(f"could not read '{PROC_ACPI_PATH}'")
        return result


    for iface_device in Path("/sys/class/net").glob('*/device'):
        if (iface_name := iface_device.parent.name) == "lo":
            continue

        if not iface_device.is_symlink():
            continue

        try:
            pci_path = iface_device.resolve()
            pci_addr = pci_path.name
        except OSError:
            logging.exception(f"could not revolve path '{iface_device}'")
            continue

        # Direct match from /proc/acpi/wakeup
        if pci_addr in acpi_wakeup:
            result[iface_name] = acpi_wakeup[pci_addr]
            continue

        # Fallback: search ACPI physical_node
        acpi_name = None
        for dev in ACPI_DEVICE_BASE_PATH.glob('*/physical_node'):
            try:
                target = dev.resolve()
                if pci_addr in target.name:
                    acpi_name = dev.name.split(":")[0]
                    break
            except OSError:
                logging.exception("could not resolve '{dev}'")
                continue

        if acpi_name and (acpi_status := acpi_wakeup.get(acpi_name)):
            result[iface_name] = acpi_status

    return result

if __name__ == '__main__':
    print(f"{get_nic_acpi_wakeup_map()=}")