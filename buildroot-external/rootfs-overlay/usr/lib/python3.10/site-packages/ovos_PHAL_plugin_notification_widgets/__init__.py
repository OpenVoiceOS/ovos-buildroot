import time
from ovos_utils.log import LOG
from mycroft_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin


class OVOSNotificationWidgetsPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-notification-widgets", config=config)
        self.bus = bus
        self.bus.on("ovos.notification.api.request.storage.model",
                    self.notificationAPI_update_storage_model)
        self.bus.on("ovos.notification.api.set",
                    self.__notificationAPI_handle_display_notification)
        self.bus.on("ovos.notification.api.pop.clear",
                    self.__notificationAPI_handle_clear_notification_data)
        self.bus.on("ovos.notification.api.pop.clear.delete",
                    self.__notificationAPI_handle_clear_delete_notification_data)
        self.bus.on("ovos.notification.api.storage.clear",
                    self.__notificationAPI_handle_clear_notification_storage)
        self.bus.on("ovos.notification.api.storage.clear.item",
                    self.__notificationAPI_handle_clear_notification_storage_item)
        self.bus.on("ovos.notification.api.set.controlled",
                    self.__notificationAPI_handle_display_controlled)
        self.bus.on("ovos.notification.api.remove.controlled",
                    self.__notificationAPI_handle_remove_controlled)

        self.bus.on("ovos.widgets.display",
                    self.__widgetsAPI_handle_handle_widget_display)
        self.bus.on("ovos.widgets.remove",
                    self.__widgetsAPI_handle_handle_widget_remove)
        self.bus.on("ovos.widgets.update",
                    self.__widgetsAPI_handle_handle_widget_update)

        # Notifications Bits
        self.__notificationAPI_notifications_model = []
        self.__notificationAPI_notifications_storage_model = []

        LOG.info("Notification & Widgets Plugin Initalized")

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
            "callback_data": message.data.get("callback_data", {}),
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

    def __notificationAPI_handle_display_controlled(self, message):
        """ Get Controlled Notification """
        notification_message = {
            "sender": message.data.get("sender", ""),
            "text": message.data.get("text", ""),
            "style": message.data.get("style", "info"),
            "timestamp": time.time()
        }
        self.bus.emit(Message("ovos.notification.controlled.type.show",
                      data={"notification": notification_message}))

    def __notificationAPI_handle_remove_controlled(self, message):
        """ Remove Controlled Notification """
        self.bus.emit(Message("ovos.notification.controlled.type.remove"))

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

    def __notificationAPI_handle_clear_notification_storage_item(
            self, message):
        """ Clear Single Item From Notification Storage Model """
        LOG.info(
            "Notification API: Clear Single Item From Notification Storage Model")
        notification_data = message.data.get("notification", "")
        for i in range(
                len(self.__notificationAPI_notifications_storage_model)):
            if (
                self.__notificationAPI_notifications_storage_model[i]["sender"]
                == notification_data["sender"]
                and self.__notificationAPI_notifications_storage_model[i]["text"]
                == notification_data["text"]
            ):
                self.__notificationAPI_notifications_storage_model.pop(i)

        self.notificationAPI_update_storage_model()

    # Skills that can display widgets on the homescreen are: Timer, Alarm and
    # Media Player

    def __widgetsAPI_handle_handle_widget_display(self, message):
        """ Handle Widget Display """
        LOG.info("Widgets API: Handle Widget Display")
        widget_data = message.data.get("data", "")
        widget_type = message.data.get("type", "")
        if widget_type == "timer":
            self.bus.emit(Message("ovos.widgets.timer.display", data={
                "widget": widget_data}))
        elif widget_type == "alarm":
            self.bus.emit(Message("ovos.widgets.alarm.display", data={
                "widget": widget_data}))
        elif widget_type == "audio":
            self.bus.emit(Message("ovos.widgets.media.display", data={
                "widget": widget_data}))

    def __widgetsAPI_handle_handle_widget_remove(self, message):
        """ Handle Widget Remove """
        LOG.info("Widgets API: Handle Widget Remove")
        widget_data = message.data.get("data", "")
        widget_type = message.data.get("type", "")
        if widget_type == "timer":
            self.bus.emit(Message("ovos.widgets.timer.remove"))
        elif widget_type == "alarm":
            self.bus.emit(Message("ovos.widgets.alarm.remove"))
        elif widget_type == "audio":
            self.bus.emit(Message("ovos.widgets.media.remove"))

    def __widgetsAPI_handle_handle_widget_update(self, message):
        """ Handle Widget Update """
        LOG.info("Widgets API: Handle Widget Update")
        widget_data = message.data.get("data", "")
        widget_type = message.data.get("type", "")
        if widget_type == "timer":
            self.bus.emit(Message("ovos.widgets.timer.update", data={
                "widget": widget_data}))
        elif widget_type == "alarm":
            self.bus.emit(Message("ovos.widgets.alarm.update", data={
                "widget": widget_data}))
        elif widget_type == "audio":
            self.bus.emit(Message("ovos.widgets.media.update", data={
                "widget": widget_data}))
