from enum import Enum

class BLECyclingService(Enum):
    '''
    BLE Services and Characteristics that are broadcasted by the devices themselves when being scanned.
    
    Important!
    The '347b0001-...' service identifier does not specify Sterzo
    It is common to Elite (manufacturer of Sterzo)
    Therefore, you need to implement the following logic to find Sterzos:
    A device is Sterzo iff it has ELITE but neither FITNESS nor POWERMETER

    An Elite smart trainer, for example, can have all three ELITE & FITNESS & POWERMETER services.
    '''
    ELITE = "347b0001-7635-408b-8918-8ff3949ce592"
    
    FITNESS = "00001826-0000-1000-8000-00805f9b34fb"
    POWERMETER = "00001818-0000-1000-8000-00805f9b34fb"
    