"""Device connection management logic."""

import sys
import time
import typing

import click
import meshtastic
import meshtastic.serial_interface
import serial
import serial.tools.list_ports

from baymesh.cli import echo

if typing.TYPE_CHECKING:
    from serial.tools.list_ports_common import ListPortInfo

    IFNPair = typing.Tuple[meshtastic.serial_interface.SerialInterface, "meshtastic.Node"]


def detect_supported_devices_via_serial() -> list["ListPortInfo"]:
    """Returns a list of ports that may have a supported device connected."""
    supported_devices = meshtastic.util.detect_supported_devices()
    if not supported_devices:
        return []
    candidate_ports = meshtastic.util.active_ports_on_supported_devices(supported_devices)
    all_serial_ports = serial.tools.list_ports.comports()
    matches = []
    for serial_port in all_serial_ports:
        if serial_port.device in candidate_ports:
            matches.append(serial_port)
    return matches


def select_device_flow() -> "ListPortInfo":
    """If multiple supported devices are connected, prompt the user to select one."""
    ports = detect_supported_devices_via_serial()
    if not ports:
        raise click.UsageError("Could not find a supported device connected via USB.")
    if len(ports) == 1:
        # Only one device, no need to prompt!
        return ports[0]

    while True:
        click.echo("Found multiple supported devices:")
        for i, port in enumerate(ports):
            click.echo(f"{i}) {port.device} - {port.description} - {port.hwid}")
        num_selected = int(
            click.prompt(
                "Which device number would you like to validate?",
                type=click.Choice(list(str(c) for c in range(len(ports)))),
            )
        )
        return ports[num_selected]


def ensure_meshtastic_interface(
    device_path: str, port: "ListPortInfo"
) -> meshtastic.serial_interface.SerialInterface:
    """Given a device path, returns a SerialInterface or non-zero exits."""
    click.echo(f"⚙️  Opening connection to {port.description} via {port.device}...")
    try:
        return meshtastic.serial_interface.SerialInterface(device_path)
    except OSError as e:
        if "Resource busy" in str(e):
            echo.error(
                "Device is busy. If you have another configuration client open, "
                "please close it and try again."
            )
            sys.exit(1)
        raise


def block_until_device_returns(
    interface: "meshtastic.serial_interface.SerialInterface",
) -> "meshtastic.serial_interface.SerialInterface":
    """Block until the specified devices becomes responsive.

    Most useful for applying configs and waiting for the device to come back up.
    """
    while True:
        try:
            # Just trying to trigger an exception if the device isn't ready.
            interface = meshtastic.serial_interface.SerialInterface(interface.devPath)
            # Give it another couple of seconds to settle up, since we were seeing
            # warnings with some devices.
            time.sleep(2)
            return interface
        except serial.SerialException:
            time.sleep(1)


def block_until_device_returns_node(
    interface: "meshtastic.serial_interface.SerialInterface",
) -> "IFNPair":
    """Same as block_until_device_returns but also returns a meshtastic.Node."""
    our_node = block_until_device_returns(interface)
    return interface, our_node.getNode("^local")
