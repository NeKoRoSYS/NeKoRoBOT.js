declare global {
    namespace NodeJS {
        interface ProcessEnv {
            TOKEN: string;
            CLIENTID: string;
            GUILDID: string;
            DBURI: string;
            APIURL?: string;
            APITOKEN: string;
            JWTSECRET: string;
        }
    }
}
export {};