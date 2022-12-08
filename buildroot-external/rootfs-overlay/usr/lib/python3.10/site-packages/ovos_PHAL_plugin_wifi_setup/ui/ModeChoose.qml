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

    function get_icon(icon_type) {
        if(icon_type == "onDevice") {
            return Qt.resolvedUrl("icons/ondisplay.svg")
        } else if(icon_type == "Remote") {
            return Qt.resolvedUrl("icons/onmobile.svg")
        } else {
            return Qt.resolvedUrl("icons/ongeneric.svg")
        }
    }

    Rectangle {
        id: headerArea
        anchors.top: parent.top
        width: parent.width
        height: parent.height * 0.20
        color: Kirigami.Theme.highlightColor

        Label {
            id: headerAreaLabel
            text: qstr("Setup Networking")
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
        anchors.bottom: footerArea.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 32
        columns: root.horizontalMode ? 3 : 1

        Repeater {
            id: clientsModelRepeater
            model: mainLoaderView.clientsModel

            delegate: Rectangle {
                id: gridItem
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"
                border.color: Kirigami.Theme.highlightColor
                border.width: 1
                radius: 5

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/ui_sounds_clicked.wav"))
                        Mycroft.MycroftController.sendRequest("ovos.phal.wifi.plugin.client.select", {"client": model.client, "id": model.id})
                    }

                    onPressed: {
                        gridItem.color = Qt.rgba(1, 1, 1, 0.2)
                        onDisplayIconLabelBackground.color = Qt.darker(Kirigami.Theme.backgroundColor, 2)
                    }
                    onReleased: {
                        gridItem.color = "transparent"
                        onDisplayIconLabelBackground.color = Kirigami.Theme.highlightColor
                    }
                }

                ColumnLayout {
                    anchors.fill: parent

                    Kirigami.Icon {
                        id: onDisplayIconType
                        source: root.get_icon(model.type)
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
                            text: model.display_text
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
        }
    }


    Rectangle {
        id: footerArea
        anchors.bottom: parent.bottom
        width: parent.width
        height: parent.height * 0.20
        color: Kirigami.Theme.highlightColor

        Kirigami.Separator {
            id: footerAreaSeparator
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: Kirigami.Theme.textColor
        }

        Button {
            id: footerAreaSkipButton
            anchors.top: footerAreaSeparator.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: Mycroft.Units.gridUnit * 1

            background: Rectangle {
                id: footerAreaSkipButtonBackground
                color: Kirigami.Theme.backgroundColor
                border.width: 1
                border.color: Kirigami.Theme.textColor
                radius: 4
            }

            contentItem: Item {
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.largeSpacing

                    Label {
                        id: onDisplayIconLabel
                        text: qsTr("Skip Setup")
                        Layout.preferredWidth: parent.width - parent.height * 0.8
                        Layout.fillHeight: true                        
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        fontSizeMode: Text.Fit
                        minimumPixelSize: 10
                        font.pixelSize: 32
                        color: Kirigami.Theme.textColor
                    }

                    Kirigami.Icon {
                        source: "arrow-right"
                        Layout.preferredWidth: parent.height * 0.8
                        Layout.preferredHeight: parent.height * 0.8
                    }
                }
            }

            onPressed: {
                footerAreaSkipButtonBackground.color = Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.5)
                footerAreaSkipButtonBackground.border.color = Kirigami.Theme.highlightColor
                footerAreaSkipButton.opacity = 0.8
            }

            onReleased: {
                footerAreaSkipButtonBackground.color = Kirigami.Theme.backgroundColor
                footerAreaSkipButtonBackground.border.color = Kirigami.Theme.textColor
                footerAreaSkipButton.opacity = 1
            }

            onClicked: {
                Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/ui_sounds_clicked.wav"))
                Mycroft.MycroftController.sendRequest("ovos.phal.wifi.plugin.skip.setup", {})
            }
        }
    }
}
