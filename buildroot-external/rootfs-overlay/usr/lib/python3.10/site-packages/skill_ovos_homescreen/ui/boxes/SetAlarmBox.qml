import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import "../delegates" as Delegates

Delegates.BoxSimpleDelegate {
    boxIcon: "player-time"
    iconColor: "#FFBF00"
    text: "Set up an alarm to wake up on time"
    action: "create a new alarm for morning"
}
