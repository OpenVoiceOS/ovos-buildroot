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
        anchors.top: parent.top
        anchors.topMargin: Mycroft.Units.gridUnit
        anchors.horizontalCenter: parent.horizontalCenter
        height: parent.height / 2
        spacing: Mycroft.Units.gridUnit
        verticalMode: true
    }

    WeatherArea {
        id: weatherItemBox
        anchors.top: widgetsRow.bottom
        anchors.topMargin: -(Mycroft.Units.gridUnit + 8)
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        height: parent.height / 2
        visible: idleRoot.weatherEnabled
        verticalMode: true
    }
}
