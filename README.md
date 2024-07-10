<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/thesoftdiamond/Kazushin">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Kazushin</h3>

  <p align="center">
    Kazushin, a fork of <a href="https://github.com/adi-panda/Kuebiko">this project</a>, is a Twitch Chat Bot that reads chat and generates text-to-speech responses using OpenAI API and Google Cloud API. It comes with profanity detection, and more built-in.
    <br />
    <a href="https://kazushindocs.softdiamond.net/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/TheSoftDiamond/Kazushin/">View Demo</a>
    ·
    <a href="https://github.com/TheSoftDiamond/Kazushin/issues">Report Bug</a>
    ·
    <a href="https://github.com/TheSoftDiamond/Kazushin/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- [VLC](https://www.videolan.org/vlc/)
- [Python 3.12.0](https://www.python.org/downloads/release/python-3120/)

In order to install the prerequisites, you will need to run the following command in a command line:  
* pip
  ```sh
  pip install -r requirements.txt
  ```
  
### Installation

1. Clone the repo or fork it
   ```sh
   git clone https://github.com/TheSoftDiamond/Kazushin.git
   ```
2. Grab an OpenAI API key from [OpenAPIKey](https://openai.com/api/), and Twitch Token from [TwitchApps](https://twitchapps.com/tmi/)<br>
  2a. Strip the <b>oauth:</b> from the Twitch Token
3. Create a [Google Cloud Project with TTS Service enabled](https://cloud.google.com/) and download the JSON credentials file andd add it to root folder. See [here](https://github.com/TheSoftDiamond/Kazushin/wiki/Setting-up-Google.json) for more info.
4. Enter API Keys in creds.py:
  ```python
  # You're Twitch Token 
  TWITCH_TOKEN = ""
  # Your TWITCH Channel Name
  TWITCH_CHANNEL = ""
  # Your OpenAI API Key
  OPENAI_API_KEY = ""
  # Your Google Cloud JSON Path
  GOOGLE_JSON_PATH = ""
  # Your TWITCH BOT CHANNEL Token (Copy TWITCH_TOKEN if same channel as TWITCH_CHANNEL)
  BOT_ACCOUNT_TWITCH_OAUTH = ""
  # Your TWITCH BOT CHANNEL Name - This is the channel that will post messages to chat
  BOT_ACCOUNT_TWITCH_CHANNEL = ""
  # The channel to send the bot's messages to this channel
  SENDMESSAGE_TO_THIS_CHANNEL = ""
  ```
5. In settings.py, change the bot name and more settings:
```python
import sys #Do not remove this line

##### AI SPECIFIC Settings #####

# AI's Name 
AINAME = 'AINAME'
# Conversation History
CONVERSATION_LIMIT = 10

### TTS SETTING ###
#For more info on this section, see https://cloud.google.com/text-to-speech/docs/voices

#Language Code
languageCode = "en-US"
#Name of Voice Model 
voiceName = "en-US-Polyglot-1"
#Gender (Accepts MALE/FEMALE)
ssmlGender = "MALE"

##### REDEEM DETECTION SETTINGS #####

# Should the bot listen for a specific redeem?
doRedeem = True
# Redeem ID
redeemID = ''

##### BITS DETECTION SETTINGS #####

# Should the bot listen for bits donations?
doBits = True
# Lower Bits Detection Number 
bitsLookAtLowNumber = 100
# Higher Bits Detection Number
bitsLookAtHighNumber = sys.maxsize
#Cooldown Timer in seconds
cooldownBits = 120
#Log to Twitch Chat?
bitsMessageLogChat = True

##### MESSAGE DETECTION SETTINGS #####

# Should we listen in for raw messages with the prefix?
doRawMessages = False
# AI NAME to Detect
detectMSGName = 'AINAME'
# Prefix
prefix = '!'
#Cooldown Timer in seconds
cooldownMsg = 120
#Log to Twitch Chat?
rawMessageLogChat = True

##### MESSAGE SPECIFIC SETTINGS #####

# Should the bot send messages to chat?
PostMSGtoChat = True
# Should block list be on?
blockList = False
# Profanity Filter Check
doProfanityCheck = True
# Minimum message length of message to AI to get a response (not related to message detection events)
globalminimumLength = 3
# Max Message Length (200-500), but would recommend leaving it at 500
globalmaximumLength = 500

```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FEATURES -->
## Features
* Separate conversations per user.
* Coversation History (last 10 messages. for every user). Can be changed.
* Profanity Filter (Can be turned on and off)
* Detect Cheers. Customizable in amounts
* Listens for messages from chat
* Post the bot's messages in chat. (Can be turned on and off)
* Prevent certain users from interacting with bot (use blocklist.py) - Since Version 1.0.5

## Usage

After finishing installing Kazunshin, you will most likely want to do some <a href="">post-installation setup</a>. Then after that, you can run the main_usercontext.py file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [ ] Make the python bot have user prompt context on a per person basis.
  - [ ] Would require the user to create a file called prompt_chat_USERNAME.txt, otherwise uses default prompt if the file doesn't exist. As to prevent potential hundreds of files from being created if this feature was added..
- [x] Ability to block a list of users from interacting with the bot in chat.

See the [open issues](https://github.com/thesoftdiamond/kazushin/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Profanity Filter, by arhankundu99](https://github.com/arhankundu99/profanity-filter)
* [Kuebiko, by adi-panda](https://github.com/adi-panda/Kuebiko)
* [twitch_chat, by MariusPerle](https://github.com/MariusPerle/twitch_chat)
* [GPT4Local, by xtekky](https://github.com/xtekky/gpt4local)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/thesoftdiamond/kazushin/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/thesoftdiamond/kazushin.svg?style=for-the-badge
[forks-url]: https://github.com/thesoftdiamond/kazushin/network/members
[stars-shield]: https://img.shields.io/github/stars/thesoftdiamond/kazushin.svg?style=for-the-badge
[stars-url]: https://github.com/thesoftdiamond/kazushin/stargazers
[issues-shield]: https://img.shields.io/github/issues/thesoftdiamond/kazushin.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.webp
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
