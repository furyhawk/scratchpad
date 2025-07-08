from gpiozero import LED

led = LED(21)

def blink_led():
    led.on()
    print("LED is ON")
    led.off()
    print("LED is OFF")

if __name__ == "__main__":
    while True:
        # blink_led()
        led.on()
        print("LED is ON")
        input("Press Enter to blink again...")
        led.off()
        print("LED is OFF")
        # Uncomment the line below to add a delay between blinks
        # You can add a delay here if you want to control the blink rate
        # import time
        # time.sleep(1)  # Delay for 1 second before the next blink
        # Note: Make sure to run this script with appropriate permissions to access GPIO pins.
        # For example, you might need to run it with sudo on a Raspberry Pi.
        # Also, ensure that the GPIO pin number (17 in this case) matches your setup.
        # You can change the pin number as needed.
        # This script will keep blinking the LED until you stop it (e.g., with Ctrl+C).
        # Make sure to have the LED connected correctly with a suitable resistor to avoid damaging it.
        # If you're using a Raspberry Pi, ensure that the GPIO library is installed and configured correctly.
        # You can install the gpiozero library using pip if it's not already installed:
        # pip install gpiozero