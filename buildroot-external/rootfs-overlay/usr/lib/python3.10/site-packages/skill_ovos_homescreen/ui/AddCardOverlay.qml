import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    color: Qt.darker(Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.99), 1.25)
    radius: 6
    opacity: opened ? 1 : 0
    enabled: opened ? 1 : 0
    property bool opened: false
    layer.enabled: true
    layer.effect: DropShadow {
        anchors.fill: parent
        samples: 16
        color: Qt.rgba(0, 0, 0, 0.4)
        radius: 16
        verticalOffset: 0.0
        horizontalOffset: 0.0
        spread: 0.2
    }

    function open() {
        opened = true
        reset()
    }

    function close() {
        opened = false
        reset()
    }

    function reset() {
        headerTextField.text = ""
        descriptionTextField.text = ""
        actionTextField.text = ""
        iconSelector.selectedIcon = ""
    }

    Keys.onEscapePressed: {
        opened = false
    }

    ListModel {
        id: iconListModel
        ListElement { iconName: "alarm-symbolic" }
        ListElement { iconName: "folder-music-symbolic" }
        ListElement { iconName: "document-duplicate" }
        ListElement { iconName: "typewriter" }
        ListElement { iconName: "actor" }
        ListElement { iconName: "add-placemark" }
    }

    Item {
        anchors.fill: parent    
        anchors.margins: Mycroft.Units.gridUnit / 2
        
        Kirigami.Heading {
            id: addCardOverlayHeaderArea
            level: 2
            text: qsTr("Add Card")
            color: Kirigami.Theme.textColor
            anchors.top: parent.top
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.leftMargin: Mycroft.Units.gridUnit
        }

        Kirigami.Separator {
            id: addCardOverlayHeaderSept
            anchors.top: addCardOverlayHeaderArea.bottom
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            height: 1
        }

        Item {
            anchors.top: addCardOverlayHeaderSept.bottom
            anchors.bottom: addCardOverlayFooterSept.top
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.bottomMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: parent.right

            ColumnLayout {
                anchors.fill: parent

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        id: headerTextFieldBoxLabel
                        anchors.left: parent.left
                        width: Mycroft.Units.gridUnit * 10
                        height: parent.height
                        radius: 6
                        color: Kirigami.Theme.highlightColor

                        Text {                        
                            anchors.centerIn: parent
                            text: qsTr("Header")
                            color: Kirigami.Theme.textColor
                        }
                    }
                    TextField {
                        id: headerTextField
                        anchors.left: headerTextFieldBoxLabel.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.margins: Mycroft.Units.gridUnit / 2
                        color: Kirigami.Theme.textColor

                        background: Rectangle {
                            radius: 6
                            color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.25)
                            border.color: headerTextField.enabled ? Qt.lighter(Kirigami.Theme.highlightColor, 1.5) : "transparent"

                            Text {
                                anchors.centerIn: parent
                                visible: !headerTextField.focus && headerTextField.text == "" ? 1 : 0
                                text: qsTr("Card Header Text")
                                color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                            }
                        }
                    }
                }
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        id: bodyTextFieldBoxLabel
                        anchors.left: parent.left
                        width: Mycroft.Units.gridUnit * 10
                        height: parent.height
                        radius: 6
                        color: Kirigami.Theme.highlightColor

                        Label {
                            anchors.centerIn: parent
                            text: qsTr("Description")
                            color: Kirigami.Theme.textColor
                        }
                    }
                    TextField {
                        id: descriptionTextField
                        anchors.left: bodyTextFieldBoxLabel.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.margins: Mycroft.Units.gridUnit / 2
                        color: Kirigami.Theme.textColor

                        background: Rectangle {
                            radius: 6
                            color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.25)
                            border.color: descriptionTextField.enabled ? Qt.lighter(Kirigami.Theme.highlightColor, 1.5) : "transparent"

                            Text {
                                anchors.centerIn: parent
                                visible: !descriptionTextField.focus && descriptionTextField.text == "" ? 1 : 0
                                text: qsTr("Card Description Text")
                                color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                            }
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        id: actionTextFieldBoxLabel
                        anchors.left: parent.left
                        width: Mycroft.Units.gridUnit * 10
                        height: parent.height
                        radius: 6
                        color: Kirigami.Theme.highlightColor

                        Label {
                            anchors.centerIn: parent
                            text: qsTr("Utterance")
                            color: Kirigami.Theme.textColor
                        }
                    }
                    TextField {
                        id: actionTextField
                        anchors.left: actionTextFieldBoxLabel.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.margins: Mycroft.Units.gridUnit / 2
                        color: Kirigami.Theme.textColor


                        background: Rectangle {
                            radius: 6
                            color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.25)
                            border.color: actionTextField.enabled ? Qt.lighter(Kirigami.Theme.highlightColor, 1.5) : "transparent"

                            Text {
                                anchors.centerIn: parent
                                visible: !actionTextField.focus && actionTextField.text == "" ? 1 : 0
                                text: qsTr("Card Action Text")
                                color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                            }
                        }
                    }
                }
                
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        id: iconTextFieldBoxLabel
                        anchors.left: parent.left
                        width: Mycroft.Units.gridUnit * 10
                        height: parent.height
                        radius: 6
                        color: Kirigami.Theme.highlightColor

                        Label {
                            anchors.centerIn: parent
                            text: qsTr("Icon")
                            color: Kirigami.Theme.textColor
                        }
                    }
                    Rectangle {
                        id: iconSelector
                        anchors.left: iconTextFieldBoxLabel.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.margins: Mycroft.Units.gridUnit / 2
                        color: Qt.darker(Kirigami.Theme.backgroundColor, 2)
                        radius: 6
                        property string selectedIcon: ""

                        RowLayout {
                            anchors.fill: parent                            
                            anchors.margins: Mycroft.Units.gridUnit / 2

                            Repeater {
                                model: iconListModel

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 6
                                    color: iconSelector.selectedIcon == model.iconName ? Kirigami.Theme.highlightColor : "transparent"

                                    Kirigami.Icon {
                                        anchors.fill: parent
                                        source: model.iconName
                                        color: iconSelector.selectedIcon == model.iconName ? Kirigami.Theme.textColor : Kirigami.Theme.highlightColor
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                                            iconSelector.selectedIcon = model.iconName
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Kirigami.Separator {
            id: addCardOverlayFooterSept
            anchors.bottom: addCardOverlayFooterArea.top
            anchors.bottomMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            height: 1
        }

        RowLayout {
            id: addCardOverlayFooterArea
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Mycroft.Units.gridUnit * 4

            Button {
                Layout.fillHeight: true
                Layout.fillWidth: true 
                icon.name: "list-add"
                text: qsTr("Add")

                background: Rectangle {
                    color: Kirigami.Theme.highlightColor
                    radius: 6
                }

                onClicked: {
                    var card = {
                        header: headerTextField.text,
                        description: descriptionTextField.text,
                        icon: iconSelector.selectedIcon,
                        action: actionTextField.text,
                        iconColor: Kirigami.Theme.textColor
                    }
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                    triggerGuiEvent("ovos.homescreen.dashboard.generate.card", {"card": card})
                    close()
                }
            }
            Button {
                Layout.fillHeight: true
                Layout.fillWidth: true 
                icon.name: "window-close-symbolic"
                text: qsTr("Cancel")

                background: Rectangle {
                    color: Kirigami.Theme.highlightColor
                    radius: 6
                }

                onClicked: {
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                    close()
                }
            }
        }
    }
}
