"""
use the next audio output device 
and change the input device to the one with close enougth physical device name
"""

import argparse
from typing import NamedTuple
import difflib
import winsound

from pycaw.constants import DEVICE_STATE, EDataFlow
from pycaw.pycaw import AudioUtilities
from pycaw.utils import AudioDevice


PHYS_NAME_CLOSENESS = 0.6



### utils ### 

class DeviceNames(NamedTuple):
    physicalName: str
    virtualName: str
    
def getNames(device:AudioDevice)->DeviceNames:
    return DeviceNames(
        physicalName=device.properties['{B3F8FA53-0004-438E-9003-51A46E139BFC} 6'], 
        virtualName=device.properties['{A45C254E-DF1C-4EFD-8020-67D146A850E0} 2'])


### output ###

def get_active_output_devices()->list[AudioDevice]:
    return AudioUtilities.GetAllDevices(
        data_flow=EDataFlow.eRender.value,
        device_state=DEVICE_STATE.ACTIVE.value)

def get_default_output_device()->AudioDevice:
    device = AudioUtilities.GetSpeakers()
    assert device is not None
    return device


### input ###

def get_active_input_devices()->list[AudioDevice]:
    return AudioUtilities.GetAllDevices(
        data_flow=EDataFlow.eCapture.value,
        device_state=DEVICE_STATE.ACTIVE.value)

def get_default_input_device()->AudioDevice:
    device = AudioUtilities.CreateDevice(AudioUtilities.GetMicrophone())
    assert device is not None
    return device


### both ### 

def set_default_device(device: AudioDevice):
    from pycaw.constants import ERole
    AudioUtilities.SetDefaultDevice(
        device.id, [ERole.eCommunications, ERole.eMultimedia])

def showList(devices:list[AudioDevice], defaultDeviec:AudioDevice)->None:
    for device in devices:
        prefix = ('*' if device.id == defaultDeviec.id else ' ')
        names = getNames(device)
        print(f" {prefix} {names.virtualName} ({names.physicalName})")

def getSelectedDeviceIndex(
        deviceList:list[AudioDevice], deviceSelected:AudioDevice)->int|None:
    for index, device in enumerate(deviceList):
        if device.id == deviceSelected.id:
            return index
    return None

def getSelectedDeviceWithName(
        deviceList:list[AudioDevice], selectedPhysName:str)->AudioDevice|None:
    names = [getNames(dev).physicalName for dev in deviceList]
    closest = difflib.get_close_matches(
        selectedPhysName, names, n=1, cutoff=PHYS_NAME_CLOSENESS)
    if len(closest) == 0:
        return None # => no device are close enougth
    selectedPhysName = closest[0]
    for device in deviceList:
        names = getNames(device)
        if names.physicalName == selectedPhysName:
            return device
    return None


### main ###

def main():
    # get the devices
    outputs = get_active_output_devices()
    inputs = get_active_input_devices()
    default_output = get_default_output_device()
    # determine the ones to select
    # => swap output and select same input device
    selectedOutputIndex = getSelectedDeviceIndex(outputs, default_output)
    assert selectedOutputIndex is not None, \
        f"[BUG] the default device ({default_output.FriendlyName!r}) isn't listed"
    nextOutput: AudioDevice = outputs[(selectedOutputIndex + 1) % len(outputs)]
    devicePhysName: str = getNames(nextOutput).physicalName
    nextInput = getSelectedDeviceWithName(
        inputs, selectedPhysName=devicePhysName)
    assert nextInput is not None, \
        (f"[BUG] there is no devices with close enougth physical name: {devicePhysName!r} "
         f"in {set(getNames(dev).physicalName for dev in inputs)}")
    # select the devices
    set_default_device(nextOutput)
    set_default_device(nextInput)
    # list currently selected devices
    print(f"Output devices:")
    showList(outputs, get_default_output_device())
    print(f"Input devices:")
    showList(inputs, get_default_input_device())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--closeness", default=0.6, type=float, help="to change the 'PHYS_NAME_CLOSENESS'")
    parser.add_argument("--grabErrors", action="store_true", help="to force the script to show errors")
    
    args = parser.parse_args()
    PHYS_NAME_CLOSENESS = args.closeness
    try:
        main()
    except Exception as err:
        winsound.Beep(1000, 500)
        if args.grabErrors is True:
            print(f"{err.__class__.__name__}: {err}")
            input("press enter to exit ...")
        raise