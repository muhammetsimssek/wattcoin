import discord
from discord.ext import commands, tasks
import asyncio
import logging
from config import DISCORD_BOT_TOKEN, DISCORD_ALERTS_CHANNEL, EMBED_COLOR
from api_client import WattCoinAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wattcoin-bot')

class WattBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.api = WattCoinAPI()
        self.last_activity_id = None # To track seen alerts

    async def setup_hook(self):
        try:
            await self.load_extension('cogs.commands')
            logger.info("Cog loaded: commands")
        except Exception as e:
            logger.error(f"Failed to load extension commands: {e}")

        try:
            await self.tree.sync()
            logger.info("Slash commands synced")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
        
        if DISCORD_ALERTS_CHANNEL:
            self.alert_task.start()
            logger.info("Alert task started")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')

    @tasks.loop(minutes=5) # Poll every 5 minutes to avoid spamming/rate limits
    async def alert_task(self):
        if not DISCORD_ALERTS_CHANNEL:
            return

        channel = self.get_channel(DISCORD_ALERTS_CHANNEL)
        if not channel:
            try:
                channel = await self.fetch_channel(DISCORD_ALERTS_CHANNEL)
            except discord.NotFound:
                logger.error(f"Alerts channel {DISCORD_ALERTS_CHANNEL} not found.")
                return
            except discord.Forbidden:
                logger.error(f"Bot lacks permission to access alerts channel {DISCORD_ALERTS_CHANNEL}.")
                return
            except Exception as e:
                logger.error(f"Unexpected error fetching alerts channel: {e}")
                return

        try:
            activities = await self.api.get_alerts()
            if not activities:
                return

            if self.last_activity_id is None:
                # First run, just set the last ID to the latest one to avoid backlog spam
                if activities:
                    self.last_activity_id = activities[0].get('id')
                return

            new_activities = []
            for act in activities:
                if act.get('id') == self.last_activity_id:
                    break
                new_activities.append(act)

            if not new_activities:
                return

            # Update last activity ID to the newest one
            self.last_activity_id = activities[0].get('id')

            # Process new activities (oldest first)
            for act in reversed(new_activities):
                embed = self.format_activity_embed(act)
                if embed:
                    await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in alert task loop: {e}")

    def format_activity_embed(self, act):
        act_type = act.get('type')
        title = "New Activity"
        description = act.get('description', 'No details available.')
        
        if act_type == 'NEW_BOUNTY':
            title = "🆕 New Bounty Available!"
        elif act_type == 'PR_MERGED':
            title = "✅ Pull Request Merged"
        elif act_type == 'NEW_SOLUTION':
            title = "💡 New Solution Submitted"
        elif act_type == 'TIER_PROMOTION':
            title = "🏆 Tier Promotion!"
        
        embed = discord.Embed(title=title, description=description, color=EMBED_COLOR)
        if 'url' in act:
            embed.url = act['url']
        
        return embed

    @alert_task.before_loop
    async def before_alert_task(self):
        await self.wait_until_ready()

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables.")
    else:
        bot = WattBot()
        try:
            bot.run(DISCORD_BOT_TOKEN)
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
