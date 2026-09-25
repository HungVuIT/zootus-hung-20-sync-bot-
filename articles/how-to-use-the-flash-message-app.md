---
title: "How to Use the Flash Message App"
article_id: 360052827713
url: https://support.optisigns.com/hc/en-us/articles/360052827713-How-to-Use-the-Flash-Message-App
section: "Emergency Alert Apps"
category: "Apps & Integrations"
updated_at: 2026-09-10T16:43:35Z
---

# How to Use the Flash Message App

Article URL: https://support.optisigns.com/hc/en-us/articles/360052827713-How-to-Use-the-Flash-Message-App

### In this article, we'll explain how to use the Flash Message app to quickly take over your digital signs for announcements, quick messages, and more.

Flash Message App lets you quickly override your screens with a message. This is useful for for quick alerts and announcements.The Flash Message app lets you:

- Target flash a single or group of screens.
  - You can choose multiple individual screens, or choose screens via [tag groups](https://support.optisigns.com/hc/en-us/articles/38062664690195-Tagging-in-OptiSigns#ScreenTagging)
- Flash Assets, Playlists, or a Simple Message on your screens
- Flash immediately, or schedule when and how long your flash message should last

> **USE CASE**In a car dealership service waiting room, you could have your normal marketing playlist playing most of the time. When a customer's car is ready, the Flash Message app can interrupt the playlist with a message like: "Mr. Joe, your car is ready!" on the screens for a moment. Then, return to playing the normal playlist.

---

## What You'll Need

- An OptiSigns account - [**Standard Plan** or higher](https://www.optisigns.com/pricing)
- An [OptiSigns-enabled device](https://support.optisigns.com/hc/en-us/articles/360021855653-What-hardware-and-devices-are-supported)
- A screen, [set up and paired with OptiSigns](https://support.optisigns.com/hc/en-us/articles/18823504383891-OptiSigns-Getting-Started-Guide)

---

## Setting Up the Flash Message App

On the OptiSigns portal, go to **Files/Assets → Apps**.

![OptiSigns Files/Assets page with the Apps button highlighted in the left panel](https://support.optisigns.com/hc/article_attachments/55289118657299)

Select **Flash Message:**

![Add App dialog searching for Flash Message, with the Flash Message tile highlighted](https://support.optisigns.com/hc/article_attachments/55289118660243)

Set up your Flash Message:

![Flash Message setup form: settings on the left, live Preview pane on the right](https://support.optisigns.com/hc/article_attachments/55289118664083)

- **Name**: Name of your Flash Message App, this is the name in your asset list and will **not** be displayed on your screens.
- **Target:** Select the screens you want to target, or screens that has certain tags. Learn more about screens tagging [here](https://support.optisigns.com/hc/en-us/articles/360051746974).

  ![Target dropdown open, showing the Screens and Tags options](https://support.optisigns.com/hc/article_attachments/55289118664979)
- **Screens/Tags:** Select the tags or screens you want to target when message is activated.
- **Content Type:** Select what do you want to display when Flash Message app is activated. You can choose between a single **Asset**, a **Playlist**, or create a **Simple Message**.

  ![Content Type dropdown open, showing Asset, Playlist and Simple Message](https://support.optisigns.com/hc/article_attachments/55289129641491)

  - **Message Text:** If you select Simple Message, you can enter your message here. Note that any changes in this box should immediately be reflected in the Preview window on the right side of the screen.

    ![Simple Message fields: Message Title, Message Text, and the Theme Settings expander](https://support.optisigns.com/hc/article_attachments/55289118668691)
  - **Theme Settings:** Apply when Simple Message is chosen. These can be expanded.

    ![Theme Settings expanded, showing the Theme and Font Size dropdowns](https://support.optisigns.com/hc/article_attachments/55289129646995)

    - **Theme:** Choose a theme for your message. Pick between **Light**, **Dark**, or **Custom.** Choosing Custom will allow you to change the Text and Background color to whatever you like.
    - **Font Size:** Choose between Default, or Custom. When Custom is selected, will provide a new option: **Custom Font Size**.
      [**![Font Size set to Custom, with the unlabelled size box beside it set to 20](https://support.optisigns.com/hc/article_attachments/55289129648275)**](https://support.optisigns.com/hc/article_attachments/47648998745107)
    - **Custom:** Choose your font size.
- **Timezone:** Set the timezone for scheduling your flash message.
- **Status:** Shows when the Emergency Alert is Active or not. You can use this for seasonal or irregular potential Emergencies.

  ![Flash Time set to Immediately, with Start Time, End Time and Recurring Settings](https://support.optisigns.com/hc/article_attachments/55289129649427)
- **Flash Time:** Set when you want to flash. You can choose to flash **Immediately** or select **Schedule** to flash sometime in the future.
  - **Start Time / End Time:** Choose when to start and when to end your Flash Message.

    > **NOTE**For Start & End Times with Recurring Settings, the duration between start and end time must be less than 24 hours.
    >
    > It can be longer for one-time only messages.
- **Recurring Settings:** Choose whether or not you want this Flash Message to occur. When checked, additional options will appear:
  - **Repeat Every:** Lets you choose how often the Flash Message repeats. You can adjust this number, and choose from **Day, Week, Month,** or **Year**. When **Week, Month,** or **Year** is chosen, it will show what days it will **Repeat On**.

    **Week:**
    [![Repeat On weekday buttons, Monday to Sunday, with Thursday selected](https://support.optisigns.com/hc/article_attachments/55289118674579)](https://support.optisigns.com/hc/article_attachments/47648998750355)
    **Month:**
    [![Repeat Every set to 1 Month, with Repeat On showing the day of the month](https://support.optisigns.com/hc/article_attachments/55289118678931)](https://support.optisigns.com/hc/article_attachments/47648998754067)
    **Year:**
    [**![Repeat Every set to 1 Year, with Repeat On showing the date each year](https://support.optisigns.com/hc/article_attachments/55289129659027)**](https://support.optisigns.com/hc/article_attachments/47648998757395)
- **Ends:** Lets you choose when a recurring Flash Message will end. This can be **Never**, **On**, or **After**.
  - **Never:** The Flash Message will repeat as per above instructions and will not stop recurring until asset is changed.
  - **On:** Allows you to set a specific date at which time the Flash Message will stop recurring.
  - **After:** Allows you to set a specific number of recurrences after which the message will stop recurring.

> **NOTE**If the setup is Repeat: **Every 1 day** and Ends After: **1 occurrence**, this is equivalent to "run once only." It does not mean "repeat one more time." This essentially negates the **Recurring** **Settings** altogether.

- **Preview Window:** This shows how your Flash Message asset will look when pushed to a screen.
- **Orientation Options:** Change between Landscape and Portrait orientation for the Preview.

![Preview pane rendering the flash message, with Landscape and Portrait buttons](https://support.optisigns.com/hc/article_attachments/55289118684563)

Once you've Named your Flash Message App and configured the message the way you'd like it, hit **Save**.

When the Flash Message is activated, the screen tab will show that it's playing the Flash Message:

![Screens list row showing ASSIGNED: Flash Message: Cool Guy Message](https://support.optisigns.com/hc/article_attachments/47648969953939)

It will also be showed on your asset list as Activated, and when it will expire.

![Flash message asset card with an orange Expire in 3 minutes badge](https://support.optisigns.com/hc/article_attachments/47648969957779)

You can Expire it immediately by clicking **...** button and hitting **Expire Now.**

![Asset card menu open, with Expire Now at the top of the list](https://support.optisigns.com/hc/article_attachments/47648998765971)

You have created your Flash Message App, and know how to activate it.

## That's all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
