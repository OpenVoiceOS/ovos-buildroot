import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Item {
    id: appBarRoot
    implicitWidth: parentItem.width
    implicitHeight: parentItem.height
    opacity: opened ? 1 : 0
    enabled: opened ? 1 : 0
    property bool opened: false
    property var parentItem
    property var appsModel

    function open() {
        opened = true
    }

    function close() {
        opened = false
    }

    Keys.onEscapePressed: {
        opened = false
    }

    Image {
        id: backgroundImagePointer
        source: parentItem.skillBackgroundSource ? parentItem.skillBackgroundSource : Qt.resolvedUrl("wallpapers/default.jpg")
        fillMode: Image.PreserveAspectCrop
        anchors.fill: parent
        opacity: 0
        enabled: false
        visible: false
    }

    Control {
        id: appBarArea
        width: appBarRoot.opened ? (appBarRoot.parentItem.horizontalMode ? parent.width * 0.6 : parent.width * 0.8) : 0
        height: appBarRoot.opened ? (appBarRoot.parentItem.horizontalMode ? parent.height * 0.6 : parent.height * 0.5) : 0
        x: appBarRoot.opened ? ((parent.width - width) / 2) : 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 32
        opacity: appBarRoot.opened ? 1 : 0
        padding: 8
        z: enabled ? 3 : -2

        Behavior on opacity {
            OpacityAnimator {
                duration: Kirigami.Units.longDuration
                easing.type: Easing.InOutCubic
            }
        }

        background: Rectangle {
            radius: 6
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 1.0)

            Rectangle {
                anchors.fill: parent
                anchors.margins: 2
                radius: 5
                color: "transparent"
                border.width: 2
                border.color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.8)
            }

            FastBlur {
                id: dblur
                anchors.fill: parent
                anchors.margins: 6
                source: backgroundImagePointer
                radius: 84

                Rectangle {
                    anchors.fill: parent
                    color: Qt.darker(Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.5), 1.25)
                }
            }
        }

        contentItem: Item {

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 2

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 32

                    Rectangle {
                        id: launcherAreaHandler
                        width: appBarRoot.parentItem.horizontalMode ? Mycroft.Units.gridUnit * 3 : Mycroft.Units.gridUnit * 2
                        height: Mycroft.Units.gridUnit * 0.5
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                        radius: Mycroft.Units.gridUnit

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                                appBarRoot.close()
                            }

                            onPressed: {
                                launcherAreaHandler.color = Kirigami.Theme.highlightColor
                            }

                            onReleased:  {
                                launcherAreaHandler.color = Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                            }
                        }
                    }

                    Kirigami.Icon {
                        id: micListenIcon
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height
                        width: height
                        source: Qt.resolvedUrl("icons/mic-start.svg")
                        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                appBarRoot.close()
                                Mycroft.MycroftController.sendRequest("mycroft.mic.listen", {})
                                Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/start-listening.wav"))
                            }

                            onPressed: {
                                micListenIcon.color = Kirigami.Theme.highlightColor
                            }

                            onReleased:  {
                                micListenIcon.color = Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                            }
                        }
                    }
                }

                Kirigami.Separator {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                    color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
                }

                GridView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        visible: appBarRoot.opened ? 1 : 0 
                        enabled: appBarRoot.opened ? 1 : 0

                        id: repeaterAppsModel
                        clip: true
                        cellWidth: width / 3
                        cellHeight: height / 2
                        model: appsModel

                        ScrollBar.vertical: ScrollBar {
                        active: repeaterAppsModel.count > 6
                        snapMode: ScrollBar.SnapOnRelease
                        policy: ScrollBar.AsNeeded
                        }

                        delegate: AppEntry {
                            implicitWidth: repeaterAppsModel.cellWidth
                            implicitHeight: repeaterAppsModel.cellHeight
                        }
                }
            }
        }
    }
}