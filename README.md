## Using the [Grove GPS Module](http://www.seeedstudio.com/depot/Grove-GPS-p-959.html?cPath=25_130) with the GrovePi

### Setting It Up

On newer versions of the Raspberry Pi, the hardware serial port `/dev/ttyAMAO` which is used in our library, is actually set to be used by the bluetooth module, leaving the software implementation `/dev/ttyS0` (aka mini UART) to the actual pins of the serial line.
The problem with this mini UART is that it's too slow for what we need, so we have to switch them so that the hardware serial points to our serial pins.  

To do that, add/modify these lines to `/boot/config.txt`
```bash
dtoverlay=pi3-miniuart-bt
dtoverlay=pi3-disable-bt
enable_uart=1
```

Next, remove the 2 console statements from `/boot/cmdline.txt`.
Initially, `/boot/cmdline.txt` might look this way:
```
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes root wait
```
After you remove the 2 statements, it should be like this:
```
dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes root wait
```

Once you've done these 2 steps from above, a reboot will be required. Do it now, and then proceed to the next section.

For more information on how the serial ports are set up, you can [read this article](https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3/#Disabling_the_Console).