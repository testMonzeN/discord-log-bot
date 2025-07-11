"""
Обработчик голосовых событий
"""

import discord
from .base_event_handler import BaseEventHandler


class VoiceEventHandler(BaseEventHandler):
    """Класс для обработки голосовых событий"""
    
    async def on_voice_state_update(self, member: discord.Member, 
                                  before: discord.VoiceState, 
                                  after: discord.VoiceState):
        """Обработка изменений голосового состояния"""
        if not self.is_feature_enabled("voice_activity"):
            return
            
        log_channel = self.get_log_channel(member.guild, 'voice_activity')
        
        if before.channel is None and after.channel is not None:
            embed = self.create_embed(
                title="🎧 Пользователь зашел в голосовой канал!",
                description=f"{member.mention} зашел в канал {after.channel.mention}.",
                color=discord.Color.blue()
            )
            await log_channel.send(embed=embed)
        
        elif before.channel is not None and after.channel is None:
            embed = self.create_embed(
                title="🚪 Пользователь вышел из голосового канала!",
                description=f"{member.mention} вышел из канала {before.channel.mention}.",
                color=discord.Color.orange()
            )
            await log_channel.send(embed=embed)
        
        elif (before.channel is not None and after.channel is not None 
              and before.channel != after.channel):
            embed = self.create_embed(
                title="🔀 Пользователь перешел в другой голосовой канал!",
                description=f"{member.mention} перешел из {before.channel.mention} в {after.channel.mention}.",
                color=discord.Color.purple()
            )
            await log_channel.send(embed=embed)
        
        if before.self_mute != after.self_mute and after.channel:
            if after.self_mute:
                embed = self.create_embed(
                    title="🎤 Микрофон выключен!",
                    description=f"{member.mention} выключил микрофон в канале {after.channel.mention}.",
                    color=discord.Color.red()
                )
            else:
                embed = self.create_embed(
                    title="🎤 Микрофон включен!",
                    description=f"{member.mention} включил микрофон в канале {after.channel.mention}.",
                    color=discord.Color.green()
                )
            await log_channel.send(embed=embed)
        
        if before.self_deaf != after.self_deaf and after.channel:
            if after.self_deaf:
                embed = self.create_embed(
                    title="🎧 Наушники выключены!",
                    description=f"{member.mention} выключил наушники в канале {after.channel.mention}.",
                    color=discord.Color.red()
                )
            else:
                embed = self.create_embed(
                    title="🎧 Наушники включены!",
                    description=f"{member.mention} включил наушники в канале {after.channel.mention}.",
                    color=discord.Color.green()
                )
            await log_channel.send(embed=embed)
        
        if not before.self_stream and after.self_stream and after.channel:
            embed = self.create_embed(
                title="📺 Началась демонстрация экрана!",
                description=f"{member.mention} начал демонстрацию экрана в {after.channel.mention}.",
                color=discord.Color.teal()
            )
            await log_channel.send(embed=embed)
        
        if before.self_stream and not after.self_stream and before.channel:
            embed = self.create_embed(
                title="🛑 Демонстрация экрана завершена!",
                description=f"{member.mention} закончил демонстрацию экрана в {before.channel.mention}.",
                color=discord.Color.dark_teal()
            )
            await log_channel.send(embed=embed) 