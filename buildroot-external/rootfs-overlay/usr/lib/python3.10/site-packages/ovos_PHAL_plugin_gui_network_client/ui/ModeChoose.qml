import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0


Rectangle {
    id: root
    anchors.fill: parent
    color: Kirigami.Theme.backgroundColor
    property bool horizontalMode: root.width > root.height ? 1 : 0

    Rectangle {
        id: headerArea
        anchors.top: parent.top
        width: parent.width
        height: parent.height * 0.20
        color: Kirigami.Theme.highlightColor

        Label {
            id: headerAreaLabel
            text: "Setup Networking"
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            fontSizeMode: Text.Fit
            minimumPixelSize: 10
            font.pixelSize: 32
            color: Kirigami.Theme.textColor
        }
    }

    GridLayout {
        anchors.top: headerArea.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 32
        columns: root.horizontalMode ? 3 : 1

        Rectangle {
            id: gridItemOne
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: Kirigami.Theme.highlightColor
            border.width: 1
            radius: 5

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("/sounds/ui_sounds_clicked.wav"))
                    Mycroft.MycroftController.sendRequest("ovos.phal.balena.on.device", {})
                }

                onPressed: {
                    gridItemOne.color = Qt.rgba(1, 1, 1, 0.2)
                    onDisplayIconLabelBackground.color = Qt.darker(Kirigami.Theme.backgroundColor, 2)
                }
                onReleased: {
                    gridItemOne.color = "transparent"
                    onDisplayIconLabelBackground.color = Kirigami.Theme.highlightColor
                }
            }

            ColumnLayout {
                anchors.fill: parent

                Kirigami.Icon {
                    id: onDisplayIconType
                    source: Qt.resolvedUrl("icons/ondisplay.svg")
                    Layout.preferredWidth: root.horizontalMode ? (parent.width / 2) : (parent.height / 2)
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                    ColorOverlay {
                        anchors.fill: parent
                        source: parent
                        color: Kirigami.Theme.textColor
                    }
                }

                Rectangle {
                    id: onDisplayIconLabelBackground
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height * 0.40
                    Layout.alignment: Qt.AlignTop
                    color: Kirigami.Theme.highlightColor
                    radius: 5

                    Label {
                        id: onDisplayIconLabel
                        text: "On Display"
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.largeSpacing
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        fontSizeMode: Text.Fit
                        minimumPixelSize: 10
                        font.pixelSize: 32
                        color: Kirigami.Theme.textColor
                    }
                }
            }
        }

        Rectangle {
            id: gridItemTwo
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: Kirigami.Theme.highlightColor
            border.width: 1
            radius: 5

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("/sounds/ui_sounds_clicked.wav"))
                    Mycroft.MycroftController.sendRequest("ovos.phal.balena.on.mobile", {})
                }

                onPressed: {
                    gridItemTwo.color = Qt.rgba(1, 1, 1, 0.2)
                    onMobileIconLabelBackground.color = Qt.darker(Kirigami.Theme.backgroundColor, 2)
                }
                onReleased: {
                    gridItemTwo.color = "transparent"
                    onMobileIconLabelBackground.color = Kirigami.Theme.highlightColor
                }
            }

            ColumnLayout {
                anchors.fill: parent

                Kirigami.Icon {
                    id: onMobileIconType
                    source: Qt.resolvedUrl("icons/onmobile.svg")
                    Layout.preferredWidth: root.horizontalMode ? (parent.width / 2) : (parent.height / 2)
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    color: Kirigami.Theme.textColor

                    ColorOverlay {
                        anchors.fill: parent
                        source: parent
                        color: Kirigami.Theme.textColor
                    }
                }

                Rectangle {
                    id: onMobileIconLabelBackground
                    Layout.fillWidth: true
                    Layout.preferredHeight: parent.height * 0.40
                    Layout.alignment: Qt.AlignTop
                    color: Kirigami.Theme.highlightColor
                    radius: 5

                    Label {
                        id: onMobileIconLabel
                        text: "On Mobile"
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.largeSpacing
                        fontSizeMode: Text.Fit
                        minimumPixelSize: 10
                        font.pixelSize: 32
                        color: Kirigami.Theme.textColor
                    }
                }
            }
        }
    }
}
