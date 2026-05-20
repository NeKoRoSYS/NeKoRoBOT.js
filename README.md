# NeKoROBOT.js

A full-stack Discord.js Bot template:

Tech Stack
- **Frontend:** TypeScript, Node.js (v20), Discord.js (v14)
- **Backend:** Python (v3.12+), WebSockets
- **Database:** MongoDB

## Features:
- **Database-agnostic Backend** - Done via abstraction layer between the active DB implementation (currently MongoDB) and the data handlers. This makes it easier to swap from one database to another if necessary.
- **Hardened Security** - Uses `.env` to hide secret variables and requires an API Token to securely establish a WebSocket connection from the bot to the database.
- **Example CRUD Commands** - Comes with generic Create, Read, Update, and Delete slash commands out of the box to demo how the Discord bot interacts with the Python database layer.
- **Deployable and Fully Containerized** - Install Docker on your remote server, build the project as images, and run.

## This template assumes you already..
- Know how to use **Docker** and **Docker Compose**.
- Know how to use **MongoDB**.
- Have registered an App at the Discord Developer Portal.
- Have **Node.js** and `npm` to install `package-lock.json` dependencies.
- Have a virutual environment for **Python** and `pip` to install dependencies in `requirements.txt`.
  - I recommend making a virtual environment within the `core` folder for there you can install the packages locally and run the database so that it won't mess with your global environment.

## Getting Started

### 1. Configuration
Before running the project, you must configure your environment variables.
- Rename the provided `ENVEXAMPLE` file to `.env` in the root directory.

Fill in the required credentials:
- `TOKEN`, `CLIENTID`, `GUILDID` (From the Discord Developer Portal)
`DBURI` (Your MongoDB connection string)
`APITOKEN` (Create a random, secure string for the WebSocket handshake between the bot and backend)

### 2. Running with Docker (Recommended)
Because the app is fully containerized, the fastest way to get both the frontend and backend running together is via Docker Compose.
```bash
# Build the images and spin up the containers in the background
docker-compose up --build -d
```

To view the live logs and verify that the WebSocket connection was established successfully:
```bash
docker-compose logs -f
```

### 3. Running Manually (Localhost)
If you need to edit code and debug locally without rebuilding containers, run the services in two separate terminals.

Terminal 1: Start the Python Backend

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

Terminal 2: Start the Discord Bot Frontend

```bash
cd bot

# Install Node dependencies
npm install

# Build and run the bot 
npm run build
npm start
```
