---
title: "Tutorial: Create, Update, Add, Remove items from Playlists"
article_id: 4414558295955
url: https://support.optisigns.com/hc/en-us/articles/4414558295955-Tutorial-Create-Update-Add-Remove-items-from-Playlists
section: "OptiSigns API"
category: "Advanced Features"
updated_at: 2026-09-11T09:56:42Z
---

# Tutorial: Create, Update, Add, Remove items from Playlists

Article URL: https://support.optisigns.com/hc/en-us/articles/4414558295955-Tutorial-Create-Update-Add-Remove-items-from-Playlists

In this tutorial, we will walk through how to create a playlist and manage the assets assigned to the playlist through the API. Generally, it involves 4 steps.  Firstly, you will need to create a playlist. Secondly, you will need to add content to the playlist. Then you can update the playlist items to change the setting of the playlist items, e.g. change the play duration. Lastly, you can remove the contents from the playlist.

#### 1. Create a playlist

To create a playlist, you will need to use the savePlaylist mutation. And supply the playlist name as a arguments in the payload. If it runs successfully, it will return the requested data from the server, and an id will be assigned to the playlist. This id will be needed in the next step when assigning contents to the playlist.

```json
mutation {  savePlaylist(payload:{name:"demo_playlist"}){          _id,          name,          path,          assets{            _id,          	fileType,            filename,          	duration,          	appType          },          teamId,          tags  }}
```

![GraphQL editor running the savePlaylist mutation; the response returns the new playlist's _id and name demo_playlist.](https://support.optisigns.com/hc/article_attachments/36563851116179)

#### 2. Assign contents to the playlist

To assign the contents to the playlist, you can use the addPlaylistItems mutation. You will need to supply the playlist id retrieved from the above step, and also provide the asset id in the payload.

```json
mutation {  addPlaylistItems(_id:"4Xt7P6eYJGc4bXjR8",payload:{    ids: ["uRQynMhDsJ6QY35Wf",          "6744ff5add229e00123cf5e6"],    pos: 1  }){          	_id,          	fileType,          	filename,          	duration,          	appType  }}
```

![GraphQL editor running addPlaylistItems; the response lists the two assets added to the playlist with their durations.](https://support.optisigns.com/hc/article_attachments/36563843298579)

#### 3. Change the duration of the content in the playlist

To change the duration of the assets in the playlist, you can use the updatePlaylistItems mutation. You will need to supply the playlist id retrieved from the above step, and also provide the duration and position of the asset in the playlist that you want to apply the change to in the payload.

```json
mutation {  updatePlaylistItems(_id:"4Xt7P6eYJGc4bXjR8",payload:{    items:  [{item: {duration:15}, pos: [0,1]}]  }){            _id,            fileType,            filename,            duration,            appType  }}
```

![GraphQL editor running updatePlaylistItems; the response lists all three playlist items with their durations.](https://support.optisigns.com/hc/article_attachments/36563843301523)

Now, you can see the demo_playlist is created in the account with the selected assets. And the duration of the items are set to 15 seconds.

![OptiSigns playlist editor showing demo_playlist with three items; the first two are set to 15 sec.](https://support.optisigns.com/hc/article_attachments/55315418539411)

#### 4. Remove the content from the playlist

To remove the contents from the playlist, you can use the removePlaylistItems mutation. You will need to supply the playlist id retrieved from the above step, and also provide the position of the asset in the playlist that you want to remove in the payload.

```json
mutation {  removePlaylistItems(_id:"4Xt7P6eYJGc4bXjR8",payload:{pos: [0,1]}){            _id,            fileType,            filename,            duration,            appType  }}
```

![GraphQL editor running the removePlaylistItems mutation with the server's JSON response.](https://support.optisigns.com/hc/article_attachments/36563851134995)

Now you can see, the first 2 assets in the playlist are removed from the playlist.

![OptiSigns playlist editor showing demo_playlist with one item left, Houston Weather at 10 sec.](https://support.optisigns.com/hc/article_attachments/55315410793875)

**Previous Article - [Tutorial: Pair and Assign Content to Screen](https://support.optisigns.com/hc/en-us/articles/4414553099667-GraphQL-API-Tutorial-Pair-and-Assign-Content-to-Screen)**

**Next Article - [Tutorial: Creating or Updating Website Assets Using GraphQL](https://support.optisigns.com/hc/en-us/articles/36562094987795-Tutorial-Creating-or-Updating-Website-Assets-Using-GraphQL)**
