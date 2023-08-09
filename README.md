# mdpd-discordTrafficNotifer
This Discord bot obtains publicly available info from the MDPD traffic API to listen and post updated events to a selected channel.
https://traffic.mdpd.com/api/traffic | functioning as of August 2023.

# Self hosting:
* verify config.txt exists and has your bot token.
* verify servers_channels_config.txt exists.

# Adding our currently running instance to your server:
* Add the bot to your server using the OAUTH link:
* https://discord.com/login?redirect_to=%2Foauth2%2Fauthorize%3Fclient_id%3D1136545019264778242%26permissions%3D3072%26redirect_uri%3Dhttp%253A%252F%252Fdiscord.com%26response_type%3Dcode%26scope%3Dmessages.read%2520activities.write%2520bot
* Once added to the server, create a channel to send the notifications to then @ the bot and message !setup to provision the bot to the requested channel. 


# Todo:

* add the ability to be @ notified within the channel when an entry matches the set radius and zip code provided by a Discord user from within the channel
* "!alerts 33186 5 miles"
