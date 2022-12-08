# Copyright 2021 Aditya Mehra <aix.m@outlook.com>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
from ovos_utils.log import LOG
from mycroft_bus_client import MessageBusClient, Message


class NotificationsGuiAPI():

    def __init__(self):
        """ Init """
        LOG.info("Notifications Service Started")
        client = MessageBusClient()
        client.on("ovos.notification.api.request.storage.model",
                  self.notificationAPI_update_storage_model)
        client.on("ovos.notification.api.set",
                  self.__notificationAPI_handle_display_notification)
        client.on("ovos.notification.api.pop.clear",
                  self.__notificationAPI_handle_clear_notification_data)
        client.on("ovos.notification.api.pop.clear.delete",
                  self.__notificationAPI_handle_clear_delete_notification_data)
        client.on("ovos.notification.api.storage.clear",
                  self.__notificationAPI_handle_clear_notification_storage)
        client.on("ovos.notification.api.storage.clear.item",
                  self.__notificationAPI_handle_clear_notification_storage_item)
        self.__notificationAPI_notifications_model = []
        self.__notificationAPI_notifications_storage_model = []
        self.bus = client
        client.run_forever()

    def notificationAPI_update_storage_model(self, message=None):
        """ Update Notification Storage Model """
        LOG.info("Notification API: Update Notification Storage Model")
        self.bus.emit(Message("ovos.notification.update_storage_model", data={"notification_model": {
            "storedmodel": self.__notificationAPI_notifications_storage_model,
            "count": len(self.__notificationAPI_notifications_storage_model)
        }}))

    def __notificationAPI_handle_display_notification(self, message):
        """ Get Notification & Action """
        LOG.info("Notification API: Display Notification")
        notification_message = {
            "sender": message.data.get("sender", ""),
            "text": message.data.get("text", ""),
            "action": message.data.get("action", ""),
            "type": message.data.get("type", ""),
            "style": message.data.get("style", "info"),
            "timestamp": time.time()
        }
        if notification_message not in self.__notificationAPI_notifications_model:
            self.__notificationAPI_notifications_model.append(
                notification_message)
            time.sleep(2)
            self.bus.emit(Message("ovos.notification.update_counter", data={
                          "notification_counter": len(self.__notificationAPI_notifications_model)}))
            self.bus.emit(Message("ovos.notification.notification_data", data={
                          "notification": notification_message}))
            self.bus.emit(Message("ovos.notification.show"))

    def __notificationAPI_handle_clear_notification_data(self, message):
        """ Clear Pop Notification """
        notification_data = message.data.get("notification", "")
        self.__notificationAPI_notifications_storage_model.append(
            notification_data)
        for i in range(len(self.__notificationAPI_notifications_model)):
            if (
                self.__notificationAPI_notifications_model[i]["sender"] == notification_data["sender"]
                and self.__notificationAPI_notifications_model[i]["text"] == notification_data["text"]
            ):
                if not len(self.__notificationAPI_notifications_model) > 0:
                    del self.__notificationAPI_notifications_model[i]
                    self.__notificationAPI_notifications_model = []
                else:
                    del self.__notificationAPI_notifications_model[i]
                break
        self.notificationAPI_update_storage_model()
        self.bus.emit(Message("ovos.notification.notification_data", data={
                      "notification": {}}))

    def __notificationAPI_handle_clear_delete_notification_data(self, message):
        """ Clear Pop Notification & Delete Notification data """
        LOG.info(
            "Notification API: Clear Pop Notification & Delete Notification data")
        notification_data = message.data.get("notification", "")

        for i in range(len(self.__notificationAPI_notifications_model)):
            if (
                self.__notificationAPI_notifications_model[i]["sender"] == notification_data["sender"]
                and self.__notificationAPI_notifications_model[i]["text"] == notification_data["text"]
            ):
                if not len(self.__notificationAPI_notifications_model) > 0:
                    del self.__notificationAPI_notifications_model[i]
                    self.__notificationAPI_notifications_model = []
                else:
                    del self.__notificationAPI_notifications_model[i]
                break

    def __notificationAPI_handle_clear_notification_storage(self, _):
        """ Clear All Notification Storage Model """
        self.__notificationAPI_notifications_storage_model = []
        self.notificationAPI_update_storage_model()

    def __notificationAPI_handle_clear_notification_storage_item(self, message):
        """ Clear Single Item From Notification Storage Model """
        LOG.info(
            "Notification API: Clear Single Item From Notification Storage Model")
        notification_data = message.data.get("notification", "")
        for i in range(len(self.__notificationAPI_notifications_storage_model)):
            if (
                self.__notificationAPI_notifications_storage_model[i]["sender"]
                == notification_data["sender"]
                and self.__notificationAPI_notifications_storage_model[i]["text"]
                == notification_data["text"]
            ):
                self.__notificationAPI_notifications_storage_model.pop(i)

        self.notificationAPI_update_storage_model()


def main():
    daemon = NotificationsGuiAPI()


if __name__ == "__main__":
    main()
