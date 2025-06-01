# Main code file of ttygram

import asyncio
import sys
import re
from telethon import TelegramClient, events

class Ttygram:
    def __init__(self):
        self.client = None
        self.current_chat = None
        self.api_id = 00000
        self.api_hash = '00000'
        self.phone_number = '00000'

    async def start(self):
        print("Welcome to Ttygram!")
        print("Type 'help' for show all commands")
        await self.connect()
        await self.command_loop()

    async def connect(self):
        self.client = TelegramClient('tg_session', self.api_id, self.api_hash)
        await self.client.start(phone=self.phone_number)

    async def get_user_input(self):
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: input("ttygram> ")
        )

    async def command_loop(self):
        while True:
            try:
                cmd_input = await self.get_user_input()
                cmd = cmd_input.strip()

                if not cmd:
                    continue

                if cmd.lower() == 'help':
                    self.show_help()
                elif cmd.lower() == 'a':
                    await self.show_all_chats()
                elif cmd.startswith('s u "'):
                    await self.select_chat_by_username(cmd[4:].strip('"'))
                elif cmd.startswith('s n "'):
                    await self.select_chat_by_name(cmd[4:].strip('"'))
                elif cmd.startswith('m "'):
                    if not self.current_chat:
                        print("Error: No chat selected! Use 's u/n <name>' first")
                        continue
                    message = cmd[3:-1] if cmd.endswith('"') else cmd[3:]
                    await self.send_message(message)
                elif cmd.lower() == 'sam':
                    if not self.current_chat:
                        print("Error: No chat selected! Use 's u/n <name>' first")
                        continue
                    await self.show_all_messages()
                elif cmd.lower() in ('q', 'exit'):
                    await self.client.disconnect()
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print("Unknown command. Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\nUse 'q' or 'exit' to quit properly")
            except Exception as e:
                print(f"Error: {str(e)}")

    def show_help(self):
        print("\nTtygram commands:")
        print("  a - show all chats/groups/channels")
        print('  s u "<username>" - select chat by username (e.g. s u "@channel")')
        print('  s n "<name>" - select chat by name (for private chats without username)')
        print('  m "<msg>" - send msg after selecting chat')
        print("  sam - show all msgs in selected chat")
        print("  q - exit from ttygram\n")

    async def show_all_chats(self):
        print("\nAll your chats:")
        async for dialog in self.client.iter_dialogs():
            entity = dialog.entity
            username = f" @{entity.username}" if hasattr(entity, 'username') and entity.username else ""
            print(f"  {dialog.name}{username} ({'user' if dialog.is_user else 'group' if dialog.is_group else 'channel'})")
        print()

    async def select_chat_by_username(self, username):
        try:
            if not username.startswith('@'):
                username = '@' + username
            target = await self.client.get_entity(username)
            print(f"✅ Selected {username} successfully!")
            self.current_chat = target
        except Exception as e:
            print(f"Error: {str(e)}")

    async def select_chat_by_name(self, name):
        try:
            target = None
            async for dialog in self.client.iter_dialogs():
                if dialog.name.lower() == name.lower():
                    target = dialog.entity
                    break
            
            if target:
                print(f"✅ Selected '{name}' successfully!")
                self.current_chat = target
            else:
                print(f"Error: Chat with name '{name}' not found")
        except Exception as e:
            print(f"Error: {str(e)}")

    async def send_message(self, text):
        try:
            await self.client.send_message(self.current_chat, text)
            name = getattr(self.current_chat, 'title', 
                  getattr(self.current_chat, 'first_name', 
                  getattr(self.current_chat, 'username', 'Unknown')))
            print(f"Message sent to {name} successfully!")
        except Exception as e:
            print(f"Error sending message: {str(e)}")

    async def show_all_messages(self):
        try:
            name = getattr(self.current_chat, 'title', 
                  getattr(self.current_chat, 'first_name', 
                  getattr(self.current_chat, 'username', 'Unknown')))
            print(f"\nAll messages in chat with {name}:")
            
            async for message in self.client.iter_messages(self.current_chat, limit=20):
                sender = message.sender
                if sender:
                    sender_name = getattr(sender, 'title', 
                                       getattr(sender, 'first_name', 
                                       getattr(sender, 'username', 'Unknown')))
                else:
                    sender_name = "Unknown"
                
                prefix = "You" if message.out else sender_name
                print(f"{prefix}: {message.text or '<media>'}")
            print()
        except Exception as e:
            print(f"Error loading messages: {str(e)}")

async def main():
    ttygram = Ttygram()
    await ttygram.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
