
import usb.core
import usb.util


class HidDevice:
    """
    This class provides basic functions to access
    a USB HID device to write an endpoint
    """

    def __init__(self, dev, ep_in, ep_out):
        self.dev = dev
        self.ep_in = ep_in
        self.ep_out = ep_out

    def write(self, data):
        """
        write data on the OUT endpoint associated to the HID interface
        """
        self.ep_out.write(data)

    def read(self):
        return self.ep_in.read(self.ep_in.wMaxPacketSize, -1)

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.dev)

    @staticmethod
    def find(vid=0x2886, pid=0x0007):
        dev = usb.core.find(idVendor=vid, idProduct=pid)
        if not dev:
            return

        config = dev.get_active_configuration()

        # Iterate on all interfaces to find a HID interface
        ep_in, ep_out = None, None
        for interface in config:
            if interface.bInterfaceClass == 0x03:
                try:
                    if dev.is_kernel_driver_active(interface.bInterfaceNumber):
                        dev.detach_kernel_driver(interface.bInterfaceNumber)
                except Exception as e:
                    print(e.message)

                for ep in interface:
                    if ep.bEndpointAddress & 0x80:
                        ep_in = ep
                    else:
                        ep_out = ep
                break



        if ep_in and ep_out:
            hid = HidDevice(dev, ep_in, ep_out)

            return hid


class UsbPixelRing:
    PIXELS_N = 12

    MONO = 1
    THINK = 3
    VOLUME  = 5
    CUSTOM = 6

    def __init__(self, hid=None, pattern=None):
        self.hid = hid if hid else HidDevice.find()
        if not self.hid:
            print('No USB device found')

        colors = [0] * 4 * self.PIXELS_N
        colors[0] = 0x4
        colors[1] = 0x40
        colors[2] = 0x4

        colors[4 + 1] = 0x8
        colors[4 * 11 + 1] = 0x8

        self.direction_template = colors

    def set_brightness(self, brightness):
        print('Not support to change brightness')

    def change_pattern(self, pattern=None):
        print('Not support to change pattern')

    def off(self):
        self.set_color(rgb=0)

    def set_color(self, rgb=None, r=0, g=0, b=0):
        if rgb:
            self.write(0, [self.MONO, rgb & 0xFF, (rgb >> 8) & 0xFF, (rgb >> 16) & 0xFF])
        else:
            self.write(0, [self.MONO, b, g, r])

    def think(self):
        self.write(0, [self.THINK, 0, 0, 0])

    wait = think

    speak = think

    def set_volume(self, pixels):
        self.write(0, [self.VOLUME, 0, 0, pixels])

    def wakeup(self, angle=0):
        if angle < 0 or angle > 360:
            return

        position = int((angle + 15) % 360 / 30) % self.PIXELS_N
        colors = self.direction_template[-position*4:] + self.direction_template[:-position*4]

        self.write(0, [self.CUSTOM, 0, 0, 0])
        self.write(3, colors)

        return position

    def listen(self, angle=0):
        self.write(0, [self.MONO, 0, 0x10, 0])

    def show(self, data):
        self.write(0, [self.CUSTOM, 0, 0, 0])
        self.write(3, data)

    @staticmethod
    def to_bytearray(data):
        if type(data) is int:
            array = bytearray([data & 0xFF])
        elif type(data) is bytearray:
            array = data
        elif type(data) is str or type(data) is bytes:
            array = bytearray(data)
        elif type(data) is list:
            array = bytearray(data)
        else:
            raise TypeError('%s is not supported' % type(data))

        return array

    def write(self, address, data):
        data = self.to_bytearray(data)
        length = len(data)
        if self.hid:
            packet = bytearray([address & 0xFF, (address >> 8) & 0xFF, length & 0xFF, (length >> 8) & 0xFF]) + data
            self.hid.write(packet)

    def close(self):
        if self.hid:
            self.hid.close()

    def __call__(self, data):
        self.write(3, data)


def find():
    hid = HidDevice.find()

    if hid:
        pixel_ring = UsbPixelRing(hid)
        return pixel_ring


if __name__ == '__main__':
    import time

    pixel_ring = UsbPixelRing()
    while True:
        try:
            pixel_ring.wakeup(180)
            time.sleep(3)
            pixel_ring.listen()
            time.sleep(3)
            pixel_ring.think()
            time.sleep(3)
            pixel_ring.set_volume(8)
            time.sleep(3)
            pixel_ring.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break

    pixel_ring.off()
    
