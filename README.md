<a target="_blank" rel="noopener noreferrer" href="https://github.com/yusufyusie/yusufyusie/blob/main/line.gif">
  <img src="https://github.com/yusufyusie/yusufyusie/raw/main/line.gif" alt="divider" style="max-width: 100%; display: inline-block;"/>
</a>

<br><br>

<div align="center">
            
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Bebas+Neue&size=33&pause=5000&color=986EF7&background=FFFFFF00&center=true&vCenter=true&width=435&lines=Welcome+to+NeKoRoBOT.js!)](https://git.io/typing-svg)

</div>
<br>

<div align="center">
  
![GitHub Repo stars](https://img.shields.io/github/stars/NeKoRoSYS/NeKoRoBOT.js?style=for-the-badge&color=%23FFD700) ![Size](https://img.shields.io/github/repo-size/NeKoRoSYS/NeKoRoBOT.js?style=for-the-badge) ![GitHub last commit](https://img.shields.io/github/last-commit/NeKoRoSYS/NeKoRoBOT.js?style=for-the-badge) ![GitHub contributors](https://img.shields.io/github/contributors/NeKoRoSYS/NeKoRoBOT.js?style=for-the-badge) ![Discord](https://img.shields.io/discord/999633886994780201?style=for-the-badge&label=Discord&color=%235865F2)

</div>

</div>

<br>

This is a full-stack Discord.js Bot template that includes code for the frontend, backend, and the database of your choice—which in this case is MongoDB. I created this project as a means to learn basic web development concepts such as containerization, database management, and backend development. Additionally, I learned how to write in Typescript for this project!

<br>

<div align="center">
<a href="https://www.star-history.com/#nekorosys/NeKoRoBOT.js&type=date&legend=bottom-right">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=nekorosys/NeKoRoBOT.js&type=date&theme=dark&legend=bottom-right" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=nekorosys/NeKoRoBOT.js&type=date&legend=bottom-right" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=nekorosys/NeKoRoBOT.js&type=date&legend=bottom-right" />
 </picture>
</a>
</div>

<br>

<div align="center">
 
| **Table of Contents** |
| :---: |
| 💻 [Tech Stack](#tech-stack) |
| ⚡ [Features](#features) |
| 🤔 [Prerequisites](#prerequisites) |
| ⚙ [Getting Started](#getting-started) |

</div>

<br>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/yusufyusie/yusufyusie/blob/main/line.gif">
  <img src="https://github.com/yusufyusie/yusufyusie/raw/main/line.gif" alt="divider" style="max-width: 100%; display: inline-block;"/>
</a>

<br>

<h2 align="center">Sponsor Me!</h2>
<br>

<div align="center">
  
  <table>
    <tr>
      <td align="center" width="50%">
        <b>My Ethereum Wallet</b><br><br>
        <code>0x5C429b3fdc7E6F7a692C234358ba31492Feb651C</code><br><br>
        <img width="197" height="197" alt="Ethereum QR Code" src="https://github.com/user-attachments/assets/0474e85c-0bf9-4e80-90e4-47d883307221" /><br>
      </td>
      <td align="center" width="50%">
        <b>My Bitcoin Wallet</b><br><br>
        <code>bc1qw80kkgu8yp4mwzuzddygmnyamcjesfavwmer8a</code><br><br>
        <img width="197" height="197" alt="Bitcoin QR Code" src="https://github.com/user-attachments/assets/470db62b-dca0-4b10-a979-c2be1f8d8203" /><br>
      </td>
    </tr>
  </table>

  <p>or...</p>
  <a href="https://paypal.me/genecromarky" target="_blank" style="display: inline-block;">
    <img src="https://img.shields.io/badge/-Paypal_Me-6C3BAA?style=for-the-badge&logo=paypal&logoColor=000000&labelColor=39FF14" alt="Donate via PayPal" align="center"/>
  </a>
  <a href="https://ko-fi.com/nekorosys" target="_blank" style="display: inline-block;">
    <img src="https://img.shields.io/badge/-Buy_Me_Coffee-6C3BAA?style=for-the-badge&logo=ko-fi&logoColor=000000&labelColor=39FF14" alt="Donate via Ko-fi" align="center"/>
  </a>
</div>

<br>

<p align="center">Sponsoring me is not a must but will be immensely appreciated!</p>

<br>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/yusufyusie/yusufyusie/blob/main/line.gif">
  <img src="https://github.com/yusufyusie/yusufyusie/raw/main/line.gif" alt="divider" style="max-width: 100%; display: inline-block;"/>
</a>

<br>

<h2 align="center">Why choose NeKoRoBOT.js?</h2>
<br>

A lot of the Discord.js bot templates I've seen online are mainly designed for beginners. This project however, aims to accomodate intermediate to pro-level programmers who are more equipped to handle backend code. Compared to others, this project does not run by a monolithic architecture; it's built to be robust, modular, and scalable. I made it as generic as possible so that you can easily build on top of it with your own features in mind. NeKoRoBOT.js is built to be lean and unopinionated because every possible API interaction using the Discord bot counts and must be processed fast!

<h3>Why choose Python?</h3>

NeKoRoBOT.js is a stripped-down version of a proprietary Discord bot me and my friend made for a custom matchmaking platform for a shooter game. We chose the Python interpreting language as the bot's backend instead of putting everything on Node.js for the following reasons:
- To have clean separation of concerns. We want the frontend to only handle Discord.js and not mix database/connection logic with it too much. Everything has an abstraction layer to avoid spaghetti code. There are only like two or three instances where we need to pull back from the db using JavaScript, the rest is just the frontend pushing payloads from bot interactions.
- Abstraction, Scalability, and Maintainability. Everything can be replaced and reimplemented using different methods; we really just used Python and MongoDB for this case. Why? Because it's easy to read, inherently making it easier to maintain. With how we designed the abstraction layers and decoupled logic, the code is easier to understand and scale. If you really want to port the backend to a different language, you just have to follow and translate the current architecture over to the language you want.

<br>

<h2 align="center">Tech Stack</h2>
<br>

<div align="center">
  <table width="100%">
    <tr>
      <td align="center" valign="top" width="33%">
        <b>Frontend</b><br><br>
        <a href="https://nodejs.org" target="_blank"><img style="margin: 5px" src="https://nodejs.org/static/logos/jsIconGreen.svg" alt="Node.js" height="50"/></a>
        <a href="https://discord.js.org" target="_blank"><img style="margin: 5px" src="https://us1.discourse-cdn.com/flex026/uploads/nodered/original/3X/3/2/32c85336ea3508d2e46c735efbd71ef7c0fd36f1.png" alt="Discord.js" height="50"/></a>
        <a href="https://www.typescriptlang.org/" target="_blank"><img style="margin: 10px" src="https://profilinator.rishav.dev/skills-assets/typescript-original.svg" alt="TypeScript" height="50" /></a>  
        <a href="https://www.javascript.com/" target="_blank"><img style="margin: 5px" src="https://profilinator.rishav.dev/skills-assets/javascript-original.svg" alt="JavaScript" height="50"/></a>
      </td>
      
  <td align="center" valign="top" width="33%">
        <b>Backend</b><br><br>
        <a href="https://www.python.org/" target="_blank"><img style="margin: 5px" src="https://profilinator.rishav.dev/skills-assets/python-original.svg" alt="Python" height="50"/></a>  
        <a href="https://mongodb.com" target="_blank"><img style="margin: 5px" src="https://icon.icepanel.io/Technology/svg/MongoDB.svg" alt="MongoDB" height="50"/></a>  
      </td>
      
  <td align="center" valign="top" width="33%">
        <b>DevOps</b><br><br>
        <a href="https://docker.com/" target="_blank"><img style="margin: 5px" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/docker.png" height="50"/></a>  
        <a href="https://www.gnu.org/software/bash/" target="_blank"><img style="margin: 5px" src="https://profilinator.rishav.dev/skills-assets/gnu_bash-icon.svg" alt="Bash" height="50"/></a> 
      </td>
    </tr>
  </table>  
</div>

<br>

<h2 align="center">Features</h2>

- **Separation of Concerns** - Node.js only handles Discord.js, your frontend; on the other hand, the project uses a separate backend using Python and FastAPI.
- **Database-agnostic Backend** - Done via abstraction layer between the active DB implementation (currently MongoDB) and the data handlers. This makes it easier to swap from one database to another if necessary.
- **Stateless and Scalable**
  - Uses `valkey`, an open-source version of Redis to manage concurrency.
  - Uses FastAPI to handle WebSocket and REST endpoints. This makes it easier to integrate a dashboard later on.
- **Hardened Security**
  - Uses `.env` to hide secret variables and requires an API Token to securely establish a WebSocket connection from the bot to the database.
  - Uses `pydantic` to enforce data formats and avoid SQL injections and the like.
  - Has a server-side rate limiter.
  - Has a self-healing websocket bridge that uses ping hearbeats to wipe off dead connections and an exponential backoff to avoid spamming when attempting to reconnect. 
  - Has robust error-handling to make sure the bot doesn't crash when an error occurs across the entire stack.
- **Tag/Category-based Pagination for `/help`** - Commands can be configured to be organized according to their tag which is then handled automatically by the `/help` command by creating navigable pages via button components.
- **Example CRUD Commands** - Comes with generic Create, Read, Update, and Delete slash commands out of the box to demo how the Discord bot interacts with the Python database layer.
- **Deployable and Fully Containerized** - Install Docker on your remote server, build the project as images, and run.

<br>

<h2 align="center">Reminders and Limitations</h2>

- The codebase is hardened and production-ready but it is not secure over the internet. To ensure security, add another layer of protection by setting up `nginx` (webserver) and `certbot` (SSL certificates) on your Linux VPS if you intend to deploy this bot on remote servers.
- Make sure to sanitize the DB by using `motor` and passing structured dictionaries as data.
- Use `asyncio` for the Python backend so that heavy-duty processing won't block bot function.

<br>

<h2 align="center">Upcoming Features</h2>

- Autogen database schemaas via OpenAPI for the frontend to use, to reduce occurences of bugs and malformed/mismatched payloads
- GoLang reimplementation on another branch
- Dashboard powered by React.js w/ Tailwind CSS
- The man, the myth, the legend—Documentation!

<br>

<h2 align="center">Prerequisites</h2>

This template assumes you already...
- Know how to use **Docker** and **Docker Compose**.
- Know how to use **MongoDB**.
- Have registered an App at the Discord Developer Portal.
- Have **Node.js** and `npm` to install `package-lock.json` dependencies.
- Have a virutual environment for **Python** and `pip` to install dependencies from `requirements.txt`.
  - I recommend making a virtual environment within the `core` folder for there you can install the packages locally and run the database so that it won't mess with your global environment.

<br>

<h2 align="center">Getting Started</h2>

### Configuration
Before running the project, you must configure your environment variables.
- Rename the provided `ENVEXAMPLE` file to `.env` in the root directory.

Fill in the required credentials:
- `TOKEN`, `CLIENTID`, `GUILDID` (From the Discord Developer Portal)
`DBURI` (Your MongoDB connection string)
`APITOKEN` (Create a random, secure string for the WebSocket handshake between the bot and backend)

### Running with Docker
Because the bot is fully containerized, the fastest way to get both the frontend and backend running together is via Docker Compose.
```bash
# Build the images and spin up the containers in the background
docker-compose up --build -d
```

To view the live logs and verify that the WebSocket connection was established successfully:
```bash
docker-compose logs -f
```

### Running Manually
If you need to edit code and debug locally without rebuilding containers, run the services in two separate terminals.

**Terminal 1:** Start the Python Backend

```bash
cd core

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies and run
pip install -r requirements.txt
python main.py
```

**Terminal 2:** Start the Discord Bot Frontend

```bash
cd bot

# Install Node dependencies
npm install

# Build and run the bot 
npm run build
npm start
```

<br>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/yusufyusie/yusufyusie/blob/main/line.gif">
  <img src="https://github.com/yusufyusie/yusufyusie/raw/main/line.gif" alt="divider" style="max-width: 100%; display: inline-block;"/>
</a>
