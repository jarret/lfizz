# Source code for Lightning Network Pepsi Machine Conversion

This is the source for two daemons to run on a Raspberry Pi for driving the Vendo V 470 Pepsi Machine via the coin mech interface.

The main daemon, `lfizz` interfaces with OpenNode for obtaining BOLT11 invoices at a stable price. It drives the e-ink display to display the QR code for payment. When the invoice is paid, it drives the GPIO to drive the relay for vending the drink and detecting when the drink has dropped so it can reset.

The other daemon, `blinkr` drives the neopixel WS2812b RGB LEDs mounted on the front of the machine. It takes instruction over ZeroMQ from `lfizz` for which animation to be running.

#$ The circuit

One GPIO pin goes out to a relay, which closes the pins of the Jones plug to credit the machine to allow vending a drink.

One GPIO pin attaches to an optoisolator part which detects when the "insert correct change" lamp of the machine is on. The Optoisolator part detects the presence of 120v AC to indicate that the machine is currently awaiting payment.

## The E-ink display

The setup uses a Waveshare 4.2 inch 400x300 E-ink panel to display the QR code on the outside of the machine. The source code renders the image and writes it over the serial connection to the machine.

## Neopixels

There are a couple hundred LEDs on the front of the machine driven by a GPIO pin and are powered by a separate power supply. The `blinkr` daemon controls that using a third party library.


# More Documentation?

Sorry, I haven't written better docs. Better stuff will come eventually
