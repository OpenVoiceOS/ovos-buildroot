import QtQuick.Layouts 1.4
import QtQuick 2.9
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    color: "transparent"
    id: weatherItemBox
    property bool verticalMode: false

    RowLayout {
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit / 2

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.fillHeight: true

            Kirigami.Icon {
                id: weatherItemIcon
                source: Qt.resolvedUrl(getWeatherImagery(sessionData.weather_code))
                width: parent.height * 0.90
                height: width
                anchors.right: parent.right
                anchors.rightMargin: weatherItemBox.verticalMode ? Mycroft.Units.gridUnit / 2 : 0
                anchors.verticalCenter: parent.verticalCenter
                visible: true
                layer.enabled: true
                layer.effect: DropShadow {
                    verticalOffset: 4
                    color: idleRoot.shadowColor
                    radius: 11
                    spread: 0.4
                    samples: 16
                }
            }
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.fillHeight: true

            Text {
                id: weatherItem
                text: sessionData.weather_temp + "°"
                width: parent.width
                height: parent.height
                fontSizeMode: Text.Fit
                minimumPixelSize: parent.height / 2
                maximumLineCount: 1
                font.pixelSize: parent.height
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: weatherItemBox.verticalMode ? Text.AlignLeft : Text.AlignHCenter
                color: "white"
                visible: true
                layer.enabled: true
                layer.effect: DropShadow {
                    verticalOffset: 4
                    color: idleRoot.shadowColor
                    radius: 11
                    spread: 0.4
                    samples: 16
                }
            }
        }
    }
}
