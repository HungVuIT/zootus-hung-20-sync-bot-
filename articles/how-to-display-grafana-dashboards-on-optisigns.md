---
title: "How to Display Grafana Dashboards on OptiSigns"
article_id: 55447693635731
url: https://support.optisigns.com/hc/en-us/articles/55447693635731-How-to-Display-Grafana-Dashboards-on-OptiSigns
section: "Others"
category: "Apps & Integrations"
updated_at: 2026-09-22T14:14:45Z
---

# How to Display Grafana Dashboards on OptiSigns

Article URL: https://support.optisigns.com/hc/en-us/articles/55447693635731-How-to-Display-Grafana-Dashboards-on-OptiSigns

### In this article, we'll walk you through setting up Grafana to display on your OptiSigns digital signs.

With the Grafana app, you can display a live Grafana dashboard on any OptiSigns screen.

Once set up, the dashboard renders automatically. It does not require a login on the screen, and it refreshes on a schedule you choose.

---

## What You'll Need

- An OptiSigns account with a [Pro Plus Plan or higher](https://www.optisigns.com/pricing)
- A Grafana instance, either [Grafana Cloud](https://grafana.com/products/cloud/) or self-hosted
- Admin rights in Grafana, so you can create a service account
- A dashboard you want to display
- An OptiSigns-enabled device
- A screen, set up and paired with OptiSigns

Within Grafana, you'll also need these two values:

- Your **Grafana URL**
- A **service-account token** with the **Viewer** role

We will show how to find them in the article below.

> **NOTE**The **Integrations** page is only available to team admins. If you are not a team admin, ask one to add the Grafana connection for you — you can still build the app yourself once the connection exists.

---

## Create a Service Account in Grafana

A service account is what OptiSigns uses to read your dashboard. It is a machine identity that belongs to your Grafana, separate from any person's login, so nobody's password ever reaches a screen.

The **Viewer** role is all OptiSigns needs. No need to give OptiSigns any more complex permissions.

### Create the Service Account

In Grafana, open **Administration**, then **Users and access**, then **Service accounts**.

![Grafana left nav with Administration and Users and access open, Service accounts highlighted](https://support.optisigns.com/hc/article_attachments/55447637222419)

Click **Add service account**.

![Grafana Service accounts page with the Add service account button highlighted](https://support.optisigns.com/hc/article_attachments/55447662957459)

Give it a **Display name** you will recognize later, set **Role** to **Viewer**, and click **Create**.

![Grafana Create service account form with the Role dropdown open and Viewer selected](https://support.optisigns.com/hc/article_attachments/55447652730899)

### Generate a Token

Open the service account you just created and click **Add service account token**.

![Grafana service account page with the Add service account token button highlighted](https://support.optisigns.com/hc/article_attachments/55447652798483)

Give the token a **Display name**. Leave **No expiration** selected, or set an expiration date if your security policy requires one. Then click **Generate token**.

![Grafana Add service account token dialog with No expiration set and Generate token highlighted](https://support.optisigns.com/hc/article_attachments/55447694278931)

Copy the token and store it somewhere safe. You will paste it into OptiSigns in the next step.

![Grafana token created dialog with the token value and Copy to clipboard highlighted](https://support.optisigns.com/hc/article_attachments/55447621366163)

> **IMPORTANT**
>
> The token is shown only once. If you lose it, you cannot recover it — you will need to generate a new one and update your OptiSigns connection.
>
> If you set an expiration date, your screens will stop updating when the token expires. Put a reminder in your calendar to generate a new token and update the connection in OptiSigns before that date.

---

## Add a Grafana Connection in OptiSigns

Now we will give OptiSigns the two values you just collected.

Go to **Integrations** under your main menu, then click the **Grafana** tab and click **Add Connection**.

![OptiSigns Integrations page on the Grafana tab with the Add Connection button highlighted](https://support.optisigns.com/hc/article_attachments/55447637926547)

Fill in the form:

![Add Grafana Connection form with name, URL, masked service-account token and connection test](https://support.optisigns.com/hc/article_attachments/55447669482259)

- **Name** — the name of the connection as displayed in OptiSigns. This will not display on your screen.
- **Grafana URL** — your Grafana's base URL, for example `https://acme.grafana.net`. Use the base URL only, not a link to a dashboard.
- **Service-account token (Viewer)** — the token you generated in Grafana.

OptiSigns stores the token encrypted and uses it only on our servers. It is never sent to a screen.

You can then hit **Test Connection** once all these fields are filled. You should receive a 200 notice (green) if the connection is successful. Click **Add** to save the connection.

> **NOTE**
>
> One connection is equal to one Grafana instance. If you have more than one, add a separate connection for each.

---

## How OptiSigns Renders Your Dashboard

OptiSigns has two ways to put a Grafana dashboard on a screen, and it picks the right one for you from the URL you entered. You do not need to choose.

- **Grafana Cloud** - We render the dashboard as an image, and the screen displays it. This is essentially a screenshot that is refreshed every few minutes. Any updates made to your dashboard will need to wait for a new screenshot to be pushed to your device.
- **Self-Hosted** - We render your dashboard live. As any changes are made, the screens automatically update.

### If You Use Grafana Cloud

There is nothing else to set up. Grafana Cloud manages the image renderer for you. Skip ahead to [Create a Grafana App in OptiSigns](#CreateAGrafanaAppInOptiSigns).

> **NOTE**Grafana Cloud does not support Live mode. Grafana Cloud tells browsers not to embed its pages, so a screen cannot load it directly. Image mode is the supported path, and it is the one OptiSigns selects for you.

### If You Self-Host Grafana

Self-hosted instances default to **Live** mode, which needs a one-time change to your Grafana configuration.

OptiSigns generates the exact configuration for your account. On the **Integrations** page, under your Grafana connection, find **Set up Live mode on your Grafana**. Pick the **grafana.ini** or **Docker / Kubernetes** tab to match how you run Grafana, click **Copy**, apply it to your Grafana, and restart. Then re-run the connection test.

It turns on two things:

- JWT authentication, so your Grafana accepts a signed token from OptiSigns instead of a password
- Embedding, so the dashboard can load inside a screen. Your own Grafana logins are unaffected.

> **IMPORTANT**
>
> Both halves are required. If embedding stays off, Grafana refuses to load in a screen and the connection test reports that embedding is disabled.

If you would rather use **Image** mode on a self-hosted instance, you need Grafana's image renderer **service** installed and configured. Note that the bundled renderer *plugin* was removed in Grafana 13, so the standalone service is the only option on current versions. See [Grafana's image rendering documentation](https://grafana.com/docs/grafana/latest/setup-grafana/image-rendering/). You can then switch the mode under **Advanced** on the app itself.

> **NOTE**Some display options rely on Grafana hiding its own time picker and variable bar, which needs Grafana 11.3 or newer. On older versions those controls may still be visible on the screen.

---

## Create a Grafana App in OptiSigns

Now that the connection exists, create the asset that your screens will play.

Open OptiSigns and go to **Files/Assets** → **Apps** → **Grafana**.

![OptiSigns Add App dialog with Grafana searched and the Grafana app tile highlighted](https://support.optisigns.com/hc/article_attachments/55447638131475)

The app opens with a live preview on the right, so you can see what the screen will show as you fill in the form.

![Grafana app settings with the Connect and Dashboard sections and the connection picker highlighted](https://support.optisigns.com/hc/article_attachments/55447621822483)

Under **Connect**:

- **Name** — the name of your Grafana app. This is for use in OptiSigns and will not display on your screen.
- **Grafana connection** — choose from any Grafana connections you've set up.

Under **Dashboard**:

- **Dashboard** — choose from a list of dashboards your service account can see on that connection.
- **Single panel ID (optional)** — leave this blank to show the whole dashboard. Enter a panel's ID to show just that one panel, filling the screen. You can find the ID in Grafana's URL when you view a single panel.

### Display Settings

Open the **Display** section to control how the dashboard looks.

![Grafana app Display section showing the Time range and Theme dropdowns](https://support.optisigns.com/hc/article_attachments/55447653502355)

- **Time range** — how far back the dashboard looks: Last 1 hour, Last 6 hours, Last 24 hours, or Last 7 days. The range always ends at the current moment.
- **Theme** — **Dark** or **Light**. Dark is usually the better choice on a wall-mounted screen.

In Image mode you will also see:

- **Refresh (seconds)** — how often the screen fetches a new render, from 30 to 3600 seconds. The default is 300. More frequent updates put more load on your Grafana.
- **Image quality** — **Standard** or **High (HiDPI)**. Use High for a 4K screen or when a panel's text looks soft.
- **Show "as of" freshness stamp** — adds a small timestamp so viewers can tell how current the data is.

### Advanced Settings

The **Advanced** section holds one setting most screens never need.

![Grafana app Advanced section showing the Render mode dropdown set to Live mode](https://support.optisigns.com/hc/article_attachments/55447638366995)

- **Render mode** — **Image mode (works on Cloud)** or **Live mode (self-hosted)**. OptiSigns sets this from your connection. Only change it if the mode it chose does not work on a particular screen.

Click **Save** when you're done. The dialog stays open so you can keep adjusting; click **Close** when you're finished.

---

## Deploying a Grafana App

You can deploy your new Grafana app as an individual asset, or as part of a Split Screen.

To get your new Grafana asset to a screen, go to the **Screens** tab, then click **Edit** on the screen you want to assign it to.

![OptiSigns Screens list row with the Edit button highlighted](https://support.optisigns.com/hc/article_attachments/55447653631379)

This brings up the **Edit Screen** dialog:

![Edit Screen dialog with Content Type set to Asset and a Change button beside the selected asset](https://support.optisigns.com/hc/article_attachments/55447653712915)

Here, select **Asset** under **Content Type**. If you already have an Asset, Playlist, or Schedule selected, you can hit **Change**.

Then select your created Grafana Asset.

Now hit **Save**. Your Grafana asset will now display on screen.

You can also deploy it as part of a split screen, allowing you to show other assets at the same time. See how in our Split Screen app article. It can also be displayed in a Playlist or Schedule.

### How Updates Will Appear Onscreen

In **Image** mode, the screen fetches a fresh render every refresh interval, so a change you make in Grafana appears within one interval. If a render fails, the screen keeps showing the last good picture rather than going blank, and marks it **data may be stale** once it falls too far behind.

In **Live** mode, the dashboard is running on the screen itself, so it updates on whatever refresh your Grafana dashboard is set to.

---

## Frequently Asked Questions

Here, we'll answer some frequently asked questions our customers have, and solve some common troubleshooting issues.

### The connection test says Grafana rejected this token. What's wrong?

The token is expired, has been revoked, or belongs to a different Grafana than the URL you entered. Generate a new service-account token in Grafana and update the connection. Also check that the **Grafana URL** points at the same instance the service account lives in.

### The connection test says it could not reach my Grafana URL. Is that a problem?

Not necessarily. It means our servers could not open your Grafana from the internet, which is normal for a self-hosted instance on a private network. Your screens may still be able to reach it on your own network, which is exactly what Live mode does. You can save the connection and test again later.

If you expected it to be reachable, check the URL for typos, make sure it is "https:", and confirm the certificate is issued by a public certificate authority. A self-signed certificate will fail.

### My dashboard list is empty, or I can't find my dashboard. How can I make it appear?

The service account can sign in but cannot see any dashboards. In Grafana, check that the service account's role is **Viewer** and that it has permission to view the folder the dashboard lives in. Then reopen the picker in OptiSigns.

Also make sure the connection you're using matches the Grafana instance where the dashboard lives.

### I entered my dashboard's link and OptiSigns won't accept it. Why?

The Grafana URL field takes the base URL of your Grafana — https://acme.grafana.net — not a link to a particular dashboard. You choose the dashboard separately, from the Dashboard dropdown on the app. Remove everything after the host name and try again.

### The connection test says there's no image renderer. What do I do?

Image mode renders through Grafana's image-renderer service, and your self-hosted Grafana doesn't have one configured. Install and configure the [image renderer service](https://grafana.com/docs/grafana/latest/setup-grafana/image-rendering/). Note the bundled renderer plugin was removed in Grafana 13, so the standalone service is the only option on current versions.

Alternatively, switch **Render mode** to Live under **Advanced** on the app, which needs no renderer.

### The connection test says embedding is disabled on my Grafana. How do I fix it?

Your Grafana is telling browsers not to load it inside another page, so a screen cannot display it in Live mode. Turn embedding on in your Grafana configuration — it is part of the block under **Set up Live mode on your Grafana** on the **Integrations** page — then restart Grafana and re-run the test.

If your Grafana also sends a Content-Security-Policy, its frame-ancestors setting has to allow embedding too.

### My screen says Dashboard unavailable. What does that mean?

The screen could not load your Grafana. The usual causes are:

- Your Grafana URL is http while the player runs over https. Browsers block that, and it can only be fixed by serving Grafana over https.
- The device cannot reach your Grafana. It is likely down, DNS doesn't resolve, or the screen's network blocks it.
- Live mode is configured but your Grafana is not yet accepting OptiSigns' signed token. Re-run the connection test to confirm.

### My screen is showing old data and says data may be stale. Why?

OptiSigns could not get a fresh render from Grafana, so it is showing the last good picture rather than a blank screen. Check that Grafana is up and that the service-account token has not expired or been revoked, then re-run the connection test.

### My Grafana dashboard used to display fine, but stopped all of a sudden. What's wrong?

Usually this is an expired or revoked service-account token. If you set an expiration date when you created it, check whether that date has passed. Generate a new token in Grafana and update your OptiSigns connection.

### That’s all!

OptiSigns is the leader in [digital signage software](https://www.optisigns.com/). If you have any additional questions, concerns or any feedback about OptiSigns, feel free to reach out to our support team at [support@optisigns.com](mailto:support@optisigns.com).
