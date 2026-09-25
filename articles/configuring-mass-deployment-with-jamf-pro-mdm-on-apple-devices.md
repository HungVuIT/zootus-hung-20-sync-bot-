---
title: "Configuring Mass Deployment with Jamf Pro MDM on Apple Devices"
article_id: 31695220475283
url: https://support.optisigns.com/hc/en-us/articles/31695220475283-Configuring-Mass-Deployment-with-Jamf-Pro-MDM-on-Apple-Devices
section: "HW & Player Setup"
category: "How-to / FAQs"
updated_at: 2026-09-21T19:42:14Z
---

# Configuring Mass Deployment with Jamf Pro MDM on Apple Devices

Article URL: https://support.optisigns.com/hc/en-us/articles/31695220475283-Configuring-Mass-Deployment-with-Jamf-Pro-MDM-on-Apple-Devices

Efficiently managing digital signage across multiple devices is crucial for businesses to ensure smooth operations and consistent updates. OptiSigns, in conjunction with a Mobile Device Management (MDM) system, offers a streamlined process for mass enrolling your devices. This guide will walk you through the steps to distribute and manage OptiSigns digital signage software using a Jamf MDM system on Apple devices.

---

## Requirements

To proceed with this guide, please ensure that you have:

1. Jamf Pro MDM account.

2. OptiSigns.com credentials.

3. Apple devices running iOS or tvOS.

4. Access to Apple Business Manager or Apple School Manager.

---

## Step 1: Load OptiSigns App Inside Jamf MDM

Inside ABM (Apple Business Manager) volume purchase licenses of OptiSigns Digital Signage (It's free).

We assume that the ABM VPP account is linked to your Jamf Pro instance, otherwise, use this Jamf [Video Guide](https://trainingcatalog.jamf.com/volume-purchasing/637880) to do so.

After populating ABM apps into Jamf MDM, you should see OptiSigns Digital Signage app inside MDM Mobile Device Apps section, as shown below:

**![Jamf Pro Mobile Device Apps list showing the OptiSigns Digital Signage app, version 5.2.5, with 50 licences purchased.](https://support.optisigns.com/hc/article_attachments/31703018962963)**

---

## Step 2: OptiSigns App Enrollment with Jamf Pro MDM

Before deploying the app to devices, you can preconfigure it to have your device automatically enrolled into your OptiSigns account.

- This is not required, but if you are managing a large number of devices, this will make the deployment much easier.

To do this, navigate to the **mobile device apps section** in Jamf MDM → Click on the **OptiSigns Digital Signage app →** Select the **App Configuration** section → Complete the configuration as shown below:

![Jamf Pro App Configuration tab for OptiSigns, showing the Preferences plist with serialNo, accountId and screenName keys.](https://support.optisigns.com/hc/article_attachments/36280396747283)

Let's go through each section of the configuration:

![Close-up of the OptiSigns plist, with callouts 1, 2 and 3 marking the serialNo, accountId and screenName keys.](https://support.optisigns.com/hc/article_attachments/36280396752915)

1. **serialNo:** Serial number of the device, you can map this to a variable from your MDM.
2. **accountId:** This is your OptiSigns Account ID, you need to enter it manually.

Account ID can be found inside the OptiSigns portal, by visiting the[**Screens tab**](https://app.optisigns.com/app/screenManagement)→ Finding the screen you'd like→ Clicking **Edit** → Click **Advanced** → Click **More** → Click on the "**i**" button

![OptiSigns Edit Screen dialog with the 'i' info button at the bottom highlighted, shown magnified below the dialog.](https://support.optisigns.com/hc/article_attachments/55640659831571)

This will open your **Device Info**:

![OptiSigns device info dialog showing the JSON details, with the accountId field highlighted.](https://support.optisigns.com/hc/article_attachments/55640652722067)

3. **screenName** - This is the screen name that will appear on the OptiSigns portal, as shown in the screenshot below. Normally this is mapped to a variable from your MDM.

![OptiSigns screens list with the screen-name column highlighted, showing three screens: OptiStick, Screen 1 and Pro Player.](https://support.optisigns.com/hc/article_attachments/55640659833107)

---

## Step 3: Deployment

After completing the app configuration, you need to define the scope in Jamf MDM. Follow the Jamf [video guide](https://trainingcatalog.jamf.com/device-scope/552567), and assign VPP within Managed Distribution:

![Jamf Pro Managed distribution tab with 'Assign Content Purchased in Volume' ticked and 50 licences shown, 1 in use.](https://support.optisigns.com/hc/article_attachments/31704324293907)

Finally, you can check installation status in MDM:

![Jamf Pro device Management tab listing a pending 'Install App - OptiSigns Digital Signage 5.2.5' command.](https://support.optisigns.com/hc/article_attachments/31704776061075)

### That's all! Congratulations!

Now, you can enjoy OptiSigns Digital Signage across your Apple devices.
