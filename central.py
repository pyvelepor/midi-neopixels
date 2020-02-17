import time
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.control_change import ControlChange
from adafruit_midi.midi_message import MIDIUnknownEvent
import usb_midi

import adafruit_ble
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

def on_message(message):   
    if isinstance(message, ControlChange):
        print("Control change: {},  {}".format(message.control, message.value))

    elif isinstance(message, PitchBend):
        print("Pitch Bend: {}".format(message.pitch_bend))
    
    elif isinstance(message, NoteOn):
        print("Note On: {}, {}".format(message.note, message.velocity))

    elif isinstance(message, NoteOff):
        print("Note Off: {}, {}".format(message.note, message.velocity))

    else:
        print(message)

def get_uart_connection():
    global _uart_connection
    ble_radio = get_ble_radio()
    if _uart_connection is not None and _uart_connection.connected:
        pass

    #check if connection is cached
    elif ble_radio.connected:
        print("Checking cached connections")
        for connection in ble_radio.connections:
            if UARTService in connection:
                print("connected to UARTService")
                _uart_connection = connection
                break
    
    #otherwise, scan for UART service and connect
    else:
        print("Scanning for UARTService")
        for advertisement in ble_radio.start_scan(ProvideServicesAdvertisement, timeout=5):
            if UARTService in advertisement.services:
                print("connecting to UARTService")
                _uart_connection = ble_radio.connect(advertisement)
                print("connected to UARTService")
                break

        ble_radio.stop_scan()

def close_uart_connection():
    global _uart_connection
    if _uart_connection is not None:
        if _uart_connection.connected:
            _uart_connection.disconnect()

        _uart_connection = None

def get_midi_in(input_stream, channel=0):
    global _midi_in

    if _midi_in is None:
        _midi_in = adafruit_midi.MIDI(
            midi_in=input_stream,
            in_channel=channel
        )

    return _midi_in

def get_midi_out(output_stream, channel=0):
    global _midi_out

    if _midi_out is None:
        _midi_out = adafruit_midi.MIDI(
            midi_out=output_stream,
            out_channel=0,
        )

    return _midi_out

def get_ble_radio():
    global _ble_radio

    if _ble_radio is None:
        _ble_radio = BLERadio()

    return _ble_radio

#Do not use these
_midi_in = None
_midi_out = None
_ble_radio = None
_uart_connection = None

#Do use
uart_connection = get_uart_connection()
midi_in = get_midi_in(usb_midi.ports[0]) #input stream for MIDI is a USB port
midi_out = get_midi_out(uart_connection[UARTService]) #output stream for MIDI is a BLE UART connection

while True:
    #To avoid messages piling up, need to read MIDI messages as often as possible.
    #Needs to be done regardless of state of UART connection.
    try:
        message = midi_in.receive()
    except:
        pass
    finally:
        midi_in = get_midi_in(usb_midi.ports[0]) 

    if message is None:
        continue

    try:
        #Try to send the message, but handle all the possible errors.
        #Errors could result from bad MIDI or BLE
        midi_out.send(message)
    except AttributeError:
        pass
    except (OSError,):
        try:
            uart_connection.disconnect()
        except:
            pass
        finally:
            uart_connection = get_uart_connection()
            midi_out = get_midi_out(uart_connection[UARTService])
    
    #Handle message
    on_message(message)