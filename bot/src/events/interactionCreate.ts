import { Events, Collection, Interaction, MessageFlagsBitField, ChatInputCommandInteraction, CacheType, ContextMenuCommandInteraction, AutocompleteInteraction, ModalSubmitInteraction, ButtonInteraction, ChannelType, ContainerBuilder, TextDisplayBuilder, SeparatorBuilder, MessageFlags } from 'discord.js';
import { BotClient } from '../structures/BotClient';
import { Command, ContextMenuCommand } from '../types/discord';
import { BackendError } from '../types/backend';

async function handleCooldown(client: BotClient, interaction: ChatInputCommandInteraction | ContextMenuCommandInteraction, command: Command): Promise<boolean> {
    if (!client.cooldowns.has(command.data.name)) {
        client.cooldowns.set(command.data.name, new Collection());
    }
    
    const now = Date.now();
    const timestamps = client.cooldowns.get(command.data.name)!;
    const defaultCooldownDuration = 3;
    const cooldownAmount = (command.cooldown ?? defaultCooldownDuration) * 1000;

    if (timestamps.has(interaction.user.id)) {
        const expirationTime = timestamps.get(interaction.user.id)! + cooldownAmount;
        if (now < expirationTime) {
            const expiredTimestamp = Math.round(expirationTime / 1000);
            
            try {
                await interaction.reply({
                    content: `Please wait, you are on a cooldown for \`${command.data.name}\`. You can use it again <t:${expiredTimestamp}:R>.`,
                    flags: [MessageFlagsBitField.Flags.Ephemeral],
                });
            } catch (err) { console.warn(`[Cooldown] Failed to reply:`, err); }
            return true;
        }
    }

    timestamps.set(interaction.user.id, now);
    setTimeout(() => timestamps.delete(interaction.user.id), cooldownAmount);
    return false;
}

async function handleError(error: unknown, interaction: any) {
    const isBackendError = error instanceof BackendError;
                
    if (!isBackendError) { console.error(`Error executing ${interaction.commandName}:`, error); }

    if (interaction.isAutocomplete()) {
        return; 
    }

    const content = isBackendError 
        ? (error as BackendError).message 
        : 'There was an error while executing this command!';
    
    const embed = new ContainerBuilder()
        .setAccentColor(0xFFA500)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent("**nexsplit | Error**"))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
            new TextDisplayBuilder().setContent(`${content}`),
        )

    const replyPayload = { 
        components: [embed], 
        flags: [MessageFlagsBitField.Flags.IsComponentsV2]
    };

    try {
        await interaction.deferred ? await interaction.editReply(replyPayload as any) :
              interaction.replied ? await interaction.followUp(replyPayload as any) :
              await interaction.reply(replyPayload as any);
    } catch (replyError) { 
        console.error('Failed to send error response to user:', replyError); 
    }
}

export default {
    name: Events.InteractionCreate,
    async execute(interaction: Interaction) {
        const client = interaction.client as BotClient;

        if (interaction.isChatInputCommand() || interaction.isContextMenuCommand() || interaction.isAutocomplete()) {
            const command = client.commands.get(interaction.commandName);

            if (!command) return;

            if (interaction.isAutocomplete()) {
                if (typeof command.autocomplete !== 'function') return;
                
                try { await command.autocomplete(interaction as any);
                } catch (error) { await handleError(error, interaction as any); }
                return;
            }
            
            const commandCooldown:boolean = await handleCooldown(client, interaction, command);
            if (commandCooldown == true) return;
            
            try { await command?.execute(interaction as any);
            } catch (error) { handleError(error, interaction as any); }
        } else if (interaction.isButton() || interaction.isModalSubmit() || interaction.isAnySelectMenu()) {
            if (interaction.isButton() && interaction.customId.startsWith('help_')) return; 
            
            const baseId = interaction.customId.includes(':') 
                ? interaction.customId.split(':')[0] 
                : interaction.customId;

            const component = interaction.isButton() ? client.buttons.get(baseId) :
                              interaction.isModalSubmit() ? client.modals.get(baseId) :
                              interaction.isAnySelectMenu() ? client.selectMenus.get(baseId) : undefined;
            
            if (!component) {
                console.warn(`No collection mapping found for Custom ID: "${interaction.customId}"`);
                return;
            }
            
            try {
                await component.execute(interaction as any);
            } catch (error) {
                handleError(error, interaction as any);
            }
        }
    }
};
