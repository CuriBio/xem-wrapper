from stdlib_utils import is_cpu_arm

try:  # pragma: no cover
    from .ok import FrontPanelDevices
    from .ok import okCFrontPanel
    from .ok import okTDeviceInfo
except ImportError:  # pragma: no cover
    if not is_cpu_arm():
        raise

    class FrontPanelDevices:
        def Open(*args, **kwargs):
            pass

    class okCFrontPanel:
        deviceID = None

        def GetWireOutValue(*args, **kwargs):
            pass
    
        def ConfigureFPGA(*args, **kwargs):
            pass
    
        def ReadFromBlockPipeOut(*args, **kwargs):
            pass
    
        def SetWireInValue(*args, **kwargs):
            pass
    
        def ActivateTriggerIn(*args, **kwargs):
            pass
    
        def IsFrontPanelEnabled(*args, **kwargs):
            pass
    
        def UpdateWireOuts(*args, **kwargs):
            pass
    
        def GetDeviceInfo(*args, **kwargs):
            pass
    
        def UpdateWireIns(*args, **kwargs):
            pass
    
        def SetDeviceID(*args, **kwargs):
            pass
    
        def Open(*args, **kwargs):
            pass

    class okTDeviceInfo:
        deviceID = ""
        serialNumber = ""