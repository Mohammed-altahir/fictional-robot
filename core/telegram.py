from telethon.sync import TelegramClient,connection
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from datetime import datetime
import os
import sqlite3
import socks


api_id = 13597632
api_hash = "7708edac10111050b8a59b02341d8f35"
phone = "249114704054"


async def init(apiID,apiHash,phone):
    client = TelegramClient(
        'session',
        apiID,
        apiHash
        )
    try:
        await client.connect()
    except sqlite3.OperationalError:
        print('[!] the client is already connected')
    if not await client.is_user_authorized():
        return False,client
    else: return True,client


async def main(client):
  entity = PeerChannel(int(1077589696))  # ashtarey channel id
  try:
      my_channel = await client.get_entity(entity)
  except:
      print('[!] disconnecting.....')
      await client.disconnect()
      print('[!] connecting.....')
      await client.connect()
  offset_id = 0
  limit = 100
  all_messages = []
  total_messages = 0
  total_count_limit = 0
  running = True
  while running:
      print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
      history = await client(GetHistoryRequest(
          peer=my_channel,
          offset_id=offset_id,
          offset_date=None,
          add_offset=0,
          limit=limit,
          max_id=0,
          min_id=0,
          hash=0
      ))
      if not history.messages:
          break

      messages = history.messages
      for message in messages:
          file = f'media/{message.id}'
          if message.to_dict()['date'].date() == datetime.now().date():
              if not os.path.isfile(file + ".jpg"):
                  await client.download_media(message, file)
              all_messages.append(message.to_dict())
              print(message.to_dict()['id'])
          else:
              running = False
              break

      offset_id = messages[len(messages) - 1].id
      total_messages = len(all_messages)
      if total_count_limit != 0 and total_messages >= total_count_limit:
          break
  return all_messages
