from typing import Optional

import discord
from discord import Member, VoiceState, Guild, CategoryChannel, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Bot, Context
from utils import VOICE_CHANNEL_ID, VOICE_CATEGORY_ID


def isChannelOwner():
    async def predicate(ctx: Context):
        channel = ctx.author.voice.channel
        if channel is None: return False
        cm = ctx.bot.get_cog("ChannelManager")
        if isinstance(cm, ChannelManager):
            if not cm.isTempVoiceChannel(channel): return False
            return channel.members[0].id.__eq__(ctx.author.id)
        return False

    return commands.check(predicate)


class ChannelManager(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.channel_id: int = VOICE_CHANNEL_ID
        self.category_id: int = VOICE_CATEGORY_ID
        self.temp_voice_channels: dict[int, list[int]] = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        # <-------------------------------- create / add member -------------------------------->#
        if self.channelExist(after.channel):
            if self.joinedCreateChannel(after.channel):  # create
                category: CategoryChannel = self.get_category(member.guild)
                if self.categoryExist(category):
                    guild: Guild = after.channel.guild
                    voice_channel: VoiceChannel = await self.create_voice_channel(member, guild, category)
                    self.temp_voice_channels.update({voice_channel.id: [member.id]})
                    await member.move_to(voice_channel)

            elif self.isTempVoiceChannel(after.channel):  # update
                self.addMember(member, after.channel.id)

        # <-------------------------------- delete / remove member -------------------------------->#
        if self.channelExist(before.channel) and self.isTempVoiceChannel(before.channel):
            if self.isChannelEmpty(before.channel):  # delete
                self.temp_voice_channels.pop(before.channel.id)
                await before.channel.delete()

            else:  # update
                self.removeMember(member, before.channel.id)

    @staticmethod
    def categoryExist(category: CategoryChannel) -> bool:
        return category is not None

    @staticmethod
    async def create_voice_channel(member: Member, guild: Guild, category: CategoryChannel) -> VoiceChannel:
        return await guild.create_voice_channel(f'{member.name}''s channel', category=category)

    @staticmethod
    def isChannelEmpty(channel: VoiceChannel) -> bool:
        return len(channel.members).__eq__(0)

    def get_category(self, guild: Guild) -> Optional[CategoryChannel]:
        for category in guild.categories:
            if category.id.__eq__(self.category_id):
                return category
        return None

    @staticmethod
    def channelExist(channel: VoiceChannel) -> bool:
        return channel is not None

    def joinedCreateChannel(self, channel: VoiceChannel) -> bool:
        return channel.id == self.channel_id

    def removeMember(self, member: Member, channel_id: int) -> None:
        self.temp_voice_channels.get(channel_id).pop(member.id)

    def addMember(self, member: Member, channel_id: int) -> None:
        self.temp_voice_channels.get(channel_id).append(member.id)

    def isTempVoiceChannel(self, channel: VoiceChannel) -> bool:
        return self.temp_voice_channels.__contains__(channel.id)

    def __isChannelOwner(self, channel: VoiceChannel, member: Member) -> bool:
        return self.getTempUsers(channel.id)[0] == member.id

    def getTempUsers(self, channel_id: int) -> list:
        return self.temp_voice_channels.get(channel_id)

    @commands.command()
    @isChannelOwner()
    async def kick_vc(self, ctx: Context, member: discord.Member):
        await ctx.author.voice.channel.members.pop(member.id)

    @commands.command()
    @isChannelOwner()
    async def lock(self, ctx: Context):
        await ctx.message.delete()
        if ctx.channel.permissions_for(ctx.guild.default_role).connect:
            await ctx.channel.set_permissions(target=ctx.guild.default_role, connect=False)
        else:
            await ctx.channel.set_permissions(target=ctx.guild.default_role, connect=True)

    @commands.command()
    @isChannelOwner()
    async def mute(self, ctx: Context, member: Member):
        await ctx.channel.set_permissions(member, speak=False)


async def setup(bot: Bot):
    await bot.add_cog(ChannelManager(bot))
