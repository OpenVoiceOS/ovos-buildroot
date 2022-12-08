import QtQuick.Layouts 1.4
import QtQuick 2.9
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    color: "transparent"

    WidgetsArea {
        id: widgetsRow
        anchors.left: parent.left
        anchors.right: weatherItemBox.left
        height: parent.height
        spacing: Mycroft.Units.gridUnit
    }

    WeatherArea {
        id: weatherItemBox
        anchors.right: parent.right
        anchors.rightMargin: Mycroft.Units.gridUnit * 0.50
        width: parent.width * 0.30
        height: parent.height
        visible: idleRoot.weatherEnabled
    }
}
