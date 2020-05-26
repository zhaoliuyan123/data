import json
from package.token import username_id
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class MessagesConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def scope_token(self, token):
        user = username_id(token)
        return user

    async def connect(self):
        user = self.scope_token(self.scope['COOKIES']['token'])
        if user:
            # 加入聊天组
            await self.channel_layer.group_add(user, self.channel_name)
            await self.accept()
        else:
            # 未登录用户拒绝连接
            await self.close()

    async def receive_json(self, content, **kwargs):
        # 接收私信
        await self.send_json(content)

    async def disconnect(self, code):
        # 离开聊天组
        user = self.scope_token(self.scope['COOKIES']['token'])
        await self.channel_layer.group_discard(user, self.channel_name)

# from channels.consumer import SyncConsumer, AsyncConsumer
# from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
#
#
# class EchoConsumer(AsyncConsumer):
#     def websocket_connect(self, event):
#         self.send({
#             "type": "websocket.accept"
#         })
#
#     def websocket_receive(self, event):
#         self.send({
#             "type": "websocket.end",
#             "text": event["text"]
#         })
#
#
# class EchoAsyncConsumer(SyncConsumer):
#     async def websocket_connect(self, event):
#         await self.send({
#             "type": "websocket.accept"
#         })
#
#     async def websocket_receive(self, event):
#         # ORM 同步操作
#         # user = User.objects.get(username=username)
#         # ORM 异步操作
#         # from channels.db import database_sync_to_async
#         # user = await database_sync_to_async(User.objects.get(username=username))
#         await self.send({
#             "type": "websocket.end",
#             "text": event["text"]
#         })
#
#
# class MyConsumer(WebsocketConsumer):
#     def connect(self):
#         # 自定义出子协议
#         self.accept(subprotocol='you protocol')
#         self.close(code=403)
#
#     def receive(self, text_data=None, bytes_data=None):
#         self.send(text_data="imooc.com")  # 返回文本
#         self.send(bytes_data="imooc.com")  # 把字符串转换成二进制的帧返回
#         self.close()
#
#     def disconnect(self, code):
#         pass
#
#
# class MyAsyncConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         # 自定义出子协议
#         await self.accept(subprotocol='you protocol')
#         await self.close(code=403)
#
#     async def receive(self, text_data=None, bytes_data=None):
#         await self.send(text_data="imooc.com")  # 返回文本
#         await self.send(bytes_data="imooc.com")  # 把字符串转换成二进制的帧返回
#         await self.close()
#
#     async def disconnect(self, code):
#         pass
