# decode20-demos
 
sample code for the following de:code 20 session demonstration:

[X05 SaaS で迅速に IoT を実現 - Azure IoT Central 最新アップデートと活用術](https://www.microsoft.com/ja-jp/events/decode/2020session/detail.aspx?sid=X05)

* Real-time object detection on Azure IoT Edge device (NVIDIA Jetson Nano)
* Visualize insights in Azure IoT Central
* Trigger Teams alerts from Azure IoT Central

![](https://raw.githubusercontent.com/wiki/yahanda/decode20-demos/streaming.gif)

Architecture overview
![](https://raw.githubusercontent.com/wiki/yahanda/decode20-demos/architecture.jpg)

# Prerequisites
 
* See the **Prerequisites** section in [NVIDIA Deepstream + Azure IoT Edge on a NVIDIA Jetson Nano](https://github.com/Azure-Samples/NVIDIA-Deepstream-Azure-IoT-Edge-on-a-NVIDIA-Jetson-Nano#prerequisites) 
  * JetPack 4.4 is the latest as of May 2020, but it does not work properly, so please use [JetPack 4.3 image](https://developer.nvidia.com/jetpack-43-archive) 
* \+ USB Camera for real-time image processing

![](https://raw.githubusercontent.com/wiki/yahanda/decode20-demos/jetson-nano-and-camera.jpg)


# Installation
 
### Clone this repository
clone this repository by following command.
```
git clone git@github.com:yahanda/decode20-demos.git
```

### Create some configuration for Deepstream application
1. Open SSH connection on your Nano device
1. Create new folders
    ```bash
    cd /var
    sudo mkdir deepstream
    sudo chmod -R 777 deepstream
    mkdir ./deepstream/custom_configs
    mkdir ./deepstream/custom_models
    ```
1. Copy config files from your PC to your Nano device with SCP
    ```
    scp -r <cloned-folder>/configs/custom_configs username@your-nano-ip-address:/var/deepstream
    scp -r <cloned-folder>/configs/custom_models username@your-nano-ip-address:/var/deepstream
    ```

### Create an Azure Container Registry
1. Follow the instructions to [Quickstart: Create a private container registry using the Azure portal](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal)
1. After your container registry is created, browse to it, and from the left pane select **Access keys** from the menu located under **Settings**.
1. Enable Admin user and copy the values for **Login server**, **Username**, and **Password** and save them somewhere convenient.

### Build and Push IoT Edge Solution
1. Open git cloned folder with VS Code.
1. Update the `.env` with the values you made a note from Azure Container Registry.
1. Open the Visual Studio Code integrated terminal by selecting **View > Terminal**.
1. Sign in to Docker with the Azure container registry credentials that you saved after creating the registry.
    ```
    docker login -u <ACR username> -p <ACR password> <ACR login server>
    ```
1. Open the command palette and search for **Azure IoT Edge: Set Default Target Platform for Edge Solution**, or select the shortcut icon in the side bar at the bottom of the window.
1. In the command palette, select the target architecture from the list of options. For this sample, we're using a Jetson Nano as the IoT Edge device, so change the architecture to **arm64v8**.
1. **Build and Push IoT Edge Solution** by right clicking on `deployment.template.json` file.
1. Verify `deployment.arm64v8.json` file is generated in the **config** folder.

### Create an Azure IoT Edge device template to your Azure IoT Central
1. Complete the [Create an Azure IoT Central application](https://docs.microsoft.com/en-us/azure/iot-central/core/quick-deploy-iot-central) quickstart to create an IoT Central application using the **Custom app > Custom application** template.
1. In your IoT Central application, navigate to **Device templates** and select **+ New**.
1. On the **Select template type** page, select the **Azure IoT Edge** tile. Then select **Next: Customize**.
1. On the **Upload an Azure IoT Edge deployment manifest** page, select **Browse** to upload the `deployment.arm64v8.json` you generated previously. Then select **Next: Review**.
1. On the **Review** page, select **Create**.
1. When the template has been created, select **Module Upstreamer** and **+ Add capability**.
1. Select **Custom** and add the following interface.
    | Display name | Name | Capability type | Schema |
    |----|----|----|----| 
    | is_car | is_car | Telemetry | Integer |
    | x_car | x_car | Telemetry | Double |
    | y_car | y_car | Telemetry | Double |
    | is_person | is_person | Telemetry | Integer |
    | x_person | x_person | Telemetry | Double |
    | y_person | y_person | Telemetry | Double |
1. Select **Save** to update the template.
1. Select **Views** in the IoT Edge Device template.
1. On the **Select to add a new view** page, select the **Visualizing the device** tile.
1. Select the **is_car** and **is_person** telemetry types. Then select **Add tile**.
1. Select the **x_car** and **x_person** telemetry types. Then select **Add tile**.
1. Select the **y_car** and **y_person** telemetry types. Then select **Add tile**.
1. Select **Save** to save the View IoT Edge device telemetry view.
1. Navigate to the IoT Edge Device template and select **Publish**. Then select **Publish** to publish the template.

### Add an Azure IoT Edge device to your IoT Central
1. In your IoT Central application, navigate to the **Devices** page and select **+ New** to add a new device.
1. Select the IoT Edge device template you created previously and select **Create**.
1. When the device has been created, select **Connect** on the Device page.
1. On the Device connection page, make a note of the **ID Scope**, the **Device ID**, and the **Primary Key**. You use these values later.

#### Deploy an IoT Edge device
1. Open SSH connection on your Nano device
1. Edit the IoT Edge `config.yaml` file:
    ```bash
    sudo vi /etc/iotedge/config.yaml
    ```
1. Scroll down until you see **# Manual provisioning configuration**. Comment out the next three lines as shown in the following snippet:
    ```YAML
    # Manual provisioning configuration
    #provisioning:
    #  source: "manual"
    #  device_connection_string: "<ADD DEVICE CONNECTION STRING HERE>"
    ```
1. Scroll down until you see **# DPS symmetric key provisioning configuration**. Uncomment the next eight lines as shown in the following snippet:
    ```YAML
    # DPS symmetric key provisioning configuration
    provisioning:
    source: "dps"
    global_endpoint: "https://global.azure-devices-provisioning.net"
    scope_id: "{scope_id}"
    attestation:
        method: "symmetric_key"
        registration_id: "{registration_id}"
        symmetric_key: "{symmetric_key}"
    ```
1. Replace `{scope_id}` with the ID Scope for you made a note of previously.
1. Replace `{registration_id}` with the Device ID you made a note of previously.
1. Replace `{symmetric_key}` with the Primary key you made a note of previously.
1. Save the changes.
1. Run the following command to restart the IoT Edge daemon:
    ```bash
    sudo systemctl restart iotedge
    ```
1. To check the status of the IoT Edge modules, run the following command:
    ```bash
    iotedge list
    ```
    The output looks like the following:
    ```bash
    NAME                 STATUS           DESCRIPTION      CONFIG
    NVIDIADeepStreamSDK  running          Up 1 hours        marketplace.azurecr.io/nvidia/deepstream-iot2-l4t:latest
    Upstreamer           running          Up 1 hours       yahanda1.azurecr.io/upstreamer:0.0.1-arm64v8
    edgeAgent            running          Up 1 hours        mcr.microsoft.com/azureiotedge-agent:1.0.9
    edgeHub              running          Up 1 hours        mcr.microsoft.com/azureiotedge-hub:1.0.9
    ```

# Usage

### View the real-time object detection via Real Time Streaming Protocol (RTSP).
1. Open VLC
1. Go to **Media > Open Network Stream**
Paste the default RTSP Video URL generated by deepstream, which follows the format `rtsp://your-nano-ip-address:8554/ds-test`
1. Click **Play**

### View the telemetry
1. Open your IoT Central application, and select the IoT Edge Devices you created previously.
1. You can see the telemetry on the **View** page

![](https://raw.githubusercontent.com/wiki/yahanda/decode20-demos/sample-results.jpg)


# Note

If you use your own AI model with Custom Vision, please see the instructions below.

### Create a Custom vision model
1. Go to http://customvision.ai and Sign-in
1. Create a new Project
1. Pick up your resource, if none select **create new** and select **SKU - F0** (F0 is free) or (S0)
1. Select **Project Type = Object Detection**
1. Select **Domains = General (Compact)**
1. Choose training images, upload and tag images, and train the detector. See the [Quickstart: How to build an object detector with Custom Vision](https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/get-started-build-detector) for further information.
1. Export the detector by going to the Performance tab, clicking on Export and choosing **ONNX**.
1. Download your custom AI model and unzip it.

### Replace files on the Jetson Nano device
1. Replace the model.onnx and labels.txt on the nano device with SCP.
    ```
    scp <unzipped-folder>/model.onnx username@your-nano-ip-address:/var/deepstream/custom_models/model.onnx
    scp <unzipped-folder>/label.txt username@your-nano-ip-address:/var/deepstream/custom_models/label.txt
    ```
1. Open the **/var/deepstream/custom_configs/msgconv_config_soda_cans.txt** file and update the **num-detected-classes** property in maps to the number of objects that you've trained your custom vision model for.

### Modify the Upstreamer module
1. Open `main.py` in **Upstreamer** module with VS Code.
1. Modify the `input1_listener` function as appropriate for your model output.
1. **Build and Push IoT Edge Solution** again by right clicking on `deployment.template.json` file.

### Update the interfaces in Azure IoT Central
1. Open your IoT Central application.
1. Update the interface and view of the device template as appropriate for your Upstreamer output.
1. Migrate the device to new template.
1. Run the following command to restart the IoT Edge daemon:
    ```bash
    sudo systemctl restart iotedge
    ```
1. To check the status of the IoT Edge modules, run the following command:
    ```bash
    iotedge list
    ```
    The output looks like the following:
    ```bash
    NAME                 STATUS           DESCRIPTION      CONFIG
    NVIDIADeepStreamSDK  running          Up 1 hours        marketplace.azurecr.io/nvidia/deepstream-iot2-l4t:latest
    Upstreamer           running          Up 1 hours       yahanda1.azurecr.io/upstreamer:0.0.1-arm64v8
    edgeAgent            running          Up 1 hours        mcr.microsoft.com/azureiotedge-agent:1.0.9
    edgeHub              running          Up 1 hours        mcr.microsoft.com/azureiotedge-hub:1.0.9
    ```