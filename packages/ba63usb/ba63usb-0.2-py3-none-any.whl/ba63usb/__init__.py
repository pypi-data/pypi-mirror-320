import hid

VID = 2727
PID = 512

class BA63USB:
    
    @staticmethod
    def get(vid : int = VID,pid : int = PID, itf : int = 1):
        """Returns a list of compatible devices matching filter"""
        hid_tree = [dev for dev in hid.enumerate(vendor_id = vid,product_id = pid) if dev["interface_number"] == itf]
        return hid_tree

    def __init__(self,path):
        """Creates a new BA63 device"""
        # Support passing device dict or direct path
        if isinstance(path,dict) and "path" in path:
            path = path["path"]
        try:
            self._device = hid.device()
            self._device.open_path(path)
        except Exception as e:
            print("Exception opening device")
            raise e

        self.encoding = "cp858"

    def transmit(self,msg : bytes):
        """Sends a text or control sequence"""
        self._device.write(b'\x00\x02\x00'+bytes([len(msg)])+msg)

    def __del__(self):
        self._device.close()


    def set_charset(self,charset = 0x34,encoding="cp858"):
        """Changes charset. Default latin1 & cp858 encoding"""
        self.encoding = encoding
        self.transmit(b'\x1B\x52'+bytes([charset]))

    def clear(self):
        """Clears the display"""
        self.transmit(b'\x1B\x5B\x32\x4A')

    def clear_eol(self):
        """Clears the display until end of line"""
        self.transmit(b'\x1B\x5B\x30\x4B')

    def set_cursor(self,row : int,col : int):
        """Moves cursor for the next print (Count starts at 1)"""
        msg = bytes([0x1B,0x5B,row | 0x30,0x3B,col | 0x30,0x48])
        self.transmit(msg)

    def print_at(self,msg : str,row : int,col : int):
        """Prints a message at the specified cursor position (Count starts at 1)"""
        self.set_cursor(row,col)
        self.print(msg)

    def print(self,msg : str):
        """Prints a message at the current cursor position"""
        self.transmit(bytes(msg, self.encoding))
