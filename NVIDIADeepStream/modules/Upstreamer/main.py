# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
import json

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                #print("the data in the message received on input1 was ")
                #print(input_message.data)
                data = json.loads(input_message.data)
                obj = data['object']
                #print(obj)
                is_car = 0
                x_car = 0
                y_car = 0
                is_person = 0
                x_person = 0
                y_person = 0

                if('car\r' in obj):
                    is_car = 1
                    x_car = obj['bbox']['topleftx']
                    y_car = obj['bbox']['toplefty']
                if('person\r' in obj):
                    is_person = 1
                    x_person = obj['bbox']['topleftx']
                    y_person = obj['bbox']['toplefty']

                topleftx = obj['bbox']['topleftx']
                toplefty = obj['bbox']['toplefty']
                bottomrightx = obj['bbox']['bottomrightx']
                bottomrighty = obj['bbox']['bottomrighty']
                json_dict = {
                    "is_car": is_car,
                    "x_car": x_car,
                    "y_car": y_car,
                    "is_person": is_person,
                    "x_person": x_person,
                    "y_person": y_person,
                    #"topleftx": topleftx,
                    #"toplefty": toplefty,
                    #"bottomrightx": bottomrightx,
                    #"bottomrighty": bottomrighty
                    }
                json_str = json.dumps(json_dict)
                print(json_str)
                #print("custom properties are")
                #print(input_message.custom_properties)
                #print("forwarding mesage to output1")
                await module_client.send_message_to_output(json_str, "output1")

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())