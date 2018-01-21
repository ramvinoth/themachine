import ctypes 
 
user32 = ctypes.cdll.LoadLibrary("user32.dll") 
user32.LockWorkStation()