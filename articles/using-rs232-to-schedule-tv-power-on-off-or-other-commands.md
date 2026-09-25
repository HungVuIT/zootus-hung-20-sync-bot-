---
title: "Using RS232 to Schedule TV Power On/Off or other commands"
article_id: 9061950942995
url: https://support.optisigns.com/hc/en-us/articles/9061950942995-Using-RS232-to-Schedule-TV-Power-On-Off-or-other-commands
section: "Device Management"
category: "Advanced Features"
updated_at: 2026-09-14T20:13:10Z
---

# Using RS232 to Schedule TV Power On/Off or other commands

Article URL: https://support.optisigns.com/hc/en-us/articles/9061950942995-Using-RS232-to-Schedule-TV-Power-On-Off-or-other-commands

With OptiSigns, you can schedule TV Power On/Off using the advanced schedule feature. There are 2 ways you can do it with OptiSigns depending on what devices you are using.

- If you are using a consumer-grade TV and an OptiStick, the TV Power On/Off is achieved through HDMI-CEC. See our [**Operational Schedule**](https://support.optisigns.com/hc/en-us/articles/28598173096723-How-To-Create-and-Use-Operational-Schedules-HDMI-CEC-RS-232)article for more information.
- If you are using a commercial-grade display, RS232 will be the option for you.

In this article, we will walk through how to set up the external communication for RS232 and use it to control your commercial display power on/off. It consists of 3 steps at a high level.

1. Set up RS232 connection for serial communication.
2. Configure the RS232 command for your display and set up the template
3. Create the Power On/Off Schedule

The same procedures can be used to send other RS232 compliant commands as well.

Supported devices/platforms: Windows, Linux, Raspberry Pi, OptiStick, and OptiSigns Pro/ProMax players.

RS232 controls do exist on certain built-in TVs (usually commercial grade) as well. You'll need to check your TV for it.

**1. Create RS-232 connection**

Go to the admin console and expand Advanced, click on the link for external communication. You can also use the link below.

<https://app.optisigns.com/app/s/external-coms>

Click **Connections**, then hit the "Add New" button to create a new RS232 connection.

![External Communications (RS232) page, Connections tab, with an arrow on the Add New button.](https://support.optisigns.com/hc/article_attachments/55411852508179)

In the **Add Connection** window, you can give a name to the connection and define the serial port to use, Baud Rate, Data bits, Stop bits, and Parity. This info is determined by the commercial display used. You should be able to get it from your TV user manual.  Flow control is normally not needed in this case, you can just leave it blank.

![Add Connection dialog: Name, COM port, Baud rate, Data bits, Stop bits, Parity and flow controls.](https://support.optisigns.com/hc/article_attachments/55411852508947)

Click **Save** once the configuration is complete.

To know which serial port is used, you will need to check it on your device. Using Windows as an example, you can find it in the device manager, it will list out the COM port available. On Linux/Raspberry Pi, the serial port is normally "/dev/ttyS0" or "/dev/ttyUSB0" if a USB serial adapter is used. On OptiSigns pre-configured Android Stick, you can use "USB0" as the serial port.

![Windows Device Manager with Ports (COM & LPT) expanded, showing a USB-to-Serial adapter on COM3.](https://support.optisigns.com/hc/article_attachments/9062308259731)

**2. Configure RS232 command and set up the template**

Go to the "Commands" tab, and click the "Add New" button.

![External Communications page, Commands tab selected, with an arrow on the Add New button.](https://support.optisigns.com/hc/article_attachments/55411873083027)

Set the RS232 command of your commercial display in the pop-up window. You can choose "asc ii" or "hex" encoding depending on your TV, and the end of line value can be set here accordingly as well. By default, it is set to "CR+LF".

You will need to create a command for Power On, and a command for Power Off.

![Add Command dialog with Name, Encoding, Value and Line Ending (EOL) fields.](https://support.optisigns.com/hc/article_attachments/55411852511763)

Once commands are created, go to the "Templates" tab. This is where you map the commands to the Power On/Off action. You only need to create a template if the commands are different. For example, if you are only using Samsung commercial TVs, which all have the same commands for power on/off, then you only need to create one template for it, it can be used on all the Samsung TVs you have deployed.

![External Communications page, Templates tab selected, with an arrow on the Add New button.](https://support.optisigns.com/hc/article_attachments/55411873085203)

Map the command to the actions. The actions will be used in the advanced schedule. Save it after the mapping is complete, then the template is ready for use.

![Add Template dialog with a Name field and two mapping rows pairing an action with a command.](https://support.optisigns.com/hc/article_attachments/55411852513043)

**3. Set up Power On/Off schedule**

Once the RS-232 configuration is complete, you will need to set up an Operational Schedule.

Go to the Edit Screens, then go to the **Operational Schedule** section. Hit **New**.

![Edit Screen dialog with the Operational Schedule picker open and an arrow on the New option.](https://support.optisigns.com/hc/article_attachments/55411873089427)

You'll see the Operational Schedule screen. Here, click anywhere you'd like to schedule a Power On/Off.

![Operational Schedule dialog: schedule list on the left, weekly calendar grid on the right.](https://support.optisigns.com/hc/article_attachments/55411852516755)

Once you've done this, you'll see this menu:

![Schedule event form showing Power State and Control Method, Volume, Brightness and RS232 Commands.](https://support.optisigns.com/hc/article_attachments/55411852517139)

Here, the relevant piece is **Power State**. Clicking this will show a drop-down:

![Control Method dropdown open, showing the Auto, HDMI-CEC and RS232 options with RS232 highlighted.](https://support.optisigns.com/hc/article_attachments/55411852517523)

To power your screen on or off using RS-232, there are two relevant options:

- **To Power Screen ON -** Choose **On**. You can also specify **RS232** in the Control Method menu. The first option will make use of RS-232 first, then HDMI-CEC as a fallback. The second will only utilize RS-232.
- **To Power Screen OFF -** Choose **Off**. You can also specify **RS232** in the Control Method menu. The first option will make use of RS-232 first, then HDMI-CEC as a fallback. The second will only utilize RS-232.

That's all! Now you have learned how to schedule TV power on/off using RS232.

If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com)
