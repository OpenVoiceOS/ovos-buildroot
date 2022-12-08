import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: boxDelegateRootItem
    color: Kirigami.Theme.backgroundColor
    border.color: Kirigami.Theme.highlightColor
    border.width: 1
    radius: 15
    z: 1
    layer.enabled: true
    layer.effect: DropShadow {
        transparentBorder: false
        horizontalOffset: 3
        verticalOffset: 3
        color: Qt.rgba(0, 0, 0, 0.50)
        spread: 0.2
        samples: 8
    }
    property var action: ""
    property alias boxIcon: headerIcon.source
    property alias heading: primaryBoxHeading.text
    property alias text: primaryBoxText.text
    property alias boxImage: mainIcon.source
    property color iconColor: "red"
    property color textColor: "white"

    property bool hasBoxIcon: headerIcon.source ? 1 : 0
    property bool hasHeading: primaryBoxHeading.text ? 1 : 0
    property bool hasText: primaryBoxText.text ? 1 : 0
    property bool hasBoxImage: mainIcon.source ? 1 : 0

    property int preferredCellHeight: 4
    property int preferredCellWidth: 4

    RowLayout {
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit / 2

        ColumnLayout {
            id: primaryContentBoxLayout
            Layout.preferredWidth: hasBoxImage ? parent.width * 0.60 : parent.width
            Layout.fillHeight: true

            Rectangle {
                id: headerIconItemBox
                Layout.fillWidth: true
                Layout.preferredHeight: parent.height * 0.35
                Layout.margins: -Mycroft.Units.gridUnit / 2.5
                radius: 15
                color: Kirigami.Theme.highlightColor

                Kirigami.Icon {
                    id: headerIcon
                    anchors.centerIn: parent
                    width: parent.height
                    height: width
                    color: Kirigami.Theme.backgroundColor
                }
            }

            Item {
                id: contentPrimaryItemBox
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: Mycroft.Units.gridUnit
                Layout.rightMargin: Mycroft.Units.gridUnit

                Kirigami.Heading {
                    id: primaryBoxHeading
                    anchors.top: parent.top
                    anchors.left: parent.left
                    elide: Text.ElideRight
                    maximumLineCount: 1
                    level: 3
                    color: Kirigami.Theme.textColor
                    enabled: hasHeading
                    visible: hasHeading
                }

                Label {
                    id: primaryBoxText
                    anchors.top: hasHeading ? primaryBoxHeading.bottom : parent.top
                    anchors.topMargin: Mycroft.Units.gridUnit / 2
                    anchors.left: parent.left
                    width: parent.width
                    height: parent.height
                    maximumLineCount: 3
                    elide: Text.ElideRight
                    wrapMode: Text.WordWrap
                    fontSizeMode: Text.Fit
                    minimumPixelSize: 10
                    font.pixelSize: 100
                    color: Kirigami.Theme.textColor
                }
            }
        }

        Item {
            id: contentSecondaryItemBox
            Layout.fillWidth: true
            Layout.fillHeight: true
            enabled: hasBoxImage
            visible: hasBoxImage

            Kirigami.Icon {
                id: mainIcon
                anchors.bottom: parent.bottom
                width: parent.height
                height: width
                color: boxDelegateRootItem.iconColor
            }
        }
    }
}
