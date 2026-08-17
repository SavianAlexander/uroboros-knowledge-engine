---
title: "Editing and uploading class recordings"
url: "https://wiki.eveuniversity.org/Editing_and_uploading_class_recordings"
pageid: 2757
source: "EVE University Wiki"
categories: ["Guides", "Needing updates", "Teaching Resources"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Editing and uploading class recordings

As you know, the **EVE University Class Library** is an invaluable knowledge base for new **capsuleer**s. This guide will illustrate, step-by-step, how to record, encode, edit and upload your class recordings. We encourage **unista**s to record classes they attend.

1. # Video Tutorial
Laura Karpinski has made a wonderful video tutorial covering all of the basics:  [Recording Classes for EVE University](https://www.youtube.com/watch?v=vrFPak7Ltco)

1. # Recording
  - In order to be able to record a class on mumble, you must be using at least **Mumble** version 1.2.3**

Recording a Class is simple enough; Once you join the class sub-channel under **Class.E-UNI** on Mumble, click the red button on your menu, select Mode: **downmix**, select your output format (for the purposes of this guide, it is assumed you're using .wav format.) When you're all set, hit **Start**. Please be informed that you can not join the channel **Class.E-UNI** directly, but you must join the sub-channel with the name of the class.

  - link=**

- Congratulations, barring the ever-present possibility of connection problems, you should now be successfully recording a class.

- unlike teamspeak, when using Mumble sound notifications will not be recorded even if you leave them on during the class. (tested in rc2)

  - Back to Top**

1. # Editing & Encoding
After you record the lecture, you might need to edit it: the class might have started late and you want to remove the first 2 mins or maybe you forgot to stop the recording and you recorded 30mins of silence. Whatever the reason, if you need to edit the file, you can use a software such as [Audacity](https://audacity.sourceforge.net/), its a free, multi-platform and easy to use program and in the following sections we'll demonstrate its use. You can always use other software if you prefer to do so.

  1. # Installing Audacity & Lame Encoder
Please download & install [Audacity](https://audacity.sourceforge.net/) and install the [lame encoder for audacity](https://audacity.sourceforge.net/help/faq_i18n?s=install&i=lame-mp3), we'll need it to export our class audio files into mp3 in later steps. You can download audacity from [this link](https://audacity.sourceforge.net/download/) and lame encoder for audacity from  [this link](https://lame.buanzo.com.ar/). Please check [this page](https://audacity.sourceforge.net/help/faq?s=install&item=lame-mp3) for instructions on properly installing the encoder. We will not provide the details of installing the software or the encoder as the steps or methods may vary between different platforms.

  - Back to Top**

  1. # Editing
  - link=**
- Once you have audacity installed and lame encoder is properly set, start the program, Go to **File > Open...** and select the .wav file you recorded with Mumble.

  - link=**
- This is how it looks when you open the file.

  - link=**
- Now it's time to edit the audio file. We may need to cut out some parts from the beginning if you started recorded earlier than class start. (and that's more preferable than missing some parts of the class, so whenever possible, you should start recording a bit early and then take these parts out) see the image below for the next step.
- **Select:** use this tool to select a part of the file. You can select **a point** to start playing from there, or you can select **an area** if you want to remove or move that selected area. If you want to remove a selection, just press **Delete** button on your keyboard or go to **Edit > Delete** from the menu panel. You cannot edit the file while it's **Playing** or **Paused**, so don't forget to stop it first. Please keep in mind that audacity can do more than simply deleting parts of the file, but these functions will not be covered in this guide.
- **Zoom tool:** you can use zoom tool to zoom in (left mouse click) or out (right mouse click) to more easily pinpoint a location.
- **File format information**

  - Back to Top**

  1. # Encoding
  - link=**
- When you're done editing the file, simply go to **File > Export...** from the menu panel to save the file in .mp3 format.

  - link=**
- Make sure you've selected filetype as MP3 and click options to specify encoding properties.

Bitrate Mode: Constant
Quality: 32kbps 22050Khz
Channel Mode: Joint Stereo

- We select **Joint Stereo** because it keeps the file Mono, like the original. Selecting Stereo might result with a stereo file (which is totally unnecessary) with bigger filesize.
- Please keep the filename in the following format

E-UNI <Class name>.mp3

    - Ex: E-UNI Introduction to EVE University.mp3** or **E-UNI Drones 101.mp3**
- Click **Save**

  - link=**
- You will be asked to edit the Metadata for the mp3 file. Please use the following format and don't add anything else. See the screenshot above.

Artist Name: <Instructor's name>
Track Title: <Class name>
Album Title: EVE University Class Library
Year: <year>
Comments: Recorded: <class date in YYYY.MM.DD format>

- Unfortunately, audacity can't add or edit the Artwork attribute, but if you want to add artwork (because it's cool) with other software, such as [Mp3tag](https://www.mp3tag.de/en/), this image is recommended.

Congratulations, depending on your CPU, it may take a couple of minutes for Audacity to export the file. Now it's time to upload this file to internet.

  - Back to Top**

1. # Uploading
You can use [EVE-Files](https://eve-files.com) to upload your EVE related files, or any other publicly accessible file storage service, e.g. Dropbox, Google Drive. Just remember that the file may need to be kept available for a very long time, so don't use a service that automatically deletes files after a short period of inactivity.

  - Back to Top**
