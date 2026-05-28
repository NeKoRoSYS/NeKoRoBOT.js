import { Events } from 'discord.js';
import { BotClient } from '../structures/BotClient';
import { BackendService } from '../services/BackendService';

const APIURL = process.env.APIURL || 'http://localhost:8000/ws';

export default {
    name: Events.ClientReady,
    once: true,
    execute(client: BotClient) {
        console.log(`Ready! Logged in as ${client.user?.tag}`);
        client.wsRequests = new Map();

        const wsUrl = APIURL.replace(/^https?/, match => match === 'https' ? 'wss' : 'ws');

        if (client.user) {
            BackendService.getInstance().connect(client, wsUrl, client.user.id);
        } else {
            console.error("Failed to connect to backend: Client user is undefined.");
        }
    },
}; 