/*
 * Copyright 2018 Aditya Mehra <aix.m@outlook.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.5 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import Mycroft 1.0 as Mycroft

Item {
    id: backendViewPersonalHost
    anchors.fill: parent

    property bool horizontalMode: backendViewPersonalHost.width > backendViewPersonalHost.height ? 1 :0

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2

        Item {
            id: topArea
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: Kirigami.Units.largeSpacing
            anchors.rightMargin: Kirigami.Units.largeSpacing
            height: Kirigami.Units.gridUnit * 2

            Kirigami.Heading {
                id: brightnessSettingPageTextHeading
                level: 1
                wrapMode: Text.WordWrap
                anchors.centerIn: parent
                font.bold: true
                font.pixelSize: horizontalMode ? backendViewPersonalHost.width * 0.035 : backendViewPersonalHost.height * 0.040
                text: "Personal Backend Setup"
                color: Kirigami.Theme.highlightColor
            }
        }

        Item {
            anchors.top: topArea.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: bottomArea.top
            anchors.margins: Kirigami.Units.smallSpacing

            ColumnLayout {
                anchors.fill: parent
                spacing: Kirigami.Units.smallSpacing

                Kirigami.Separator {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                }


                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Kirigami.Units.smallSpacing
                }

                Label {
                    id: hostAddressLabel
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignLeft
                    color: Kirigami.Theme.textColor
                    wrapMode: Text.WordWrap
                    font.pixelSize: horizontalMode ? backendViewPersonalHost.width * 0.025 : backendViewPersonalHost.height * 0.030
                    text: "Address:"
                }

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Kirigami.Units.smallSpacing
                }

                Kirigami.Separator {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 1
                }

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Kirigami.Units.smallSpacing
                }

                TextField {
                    id: hostAddressField
                    Layout.fillWidth: true
                    Layout.preferredHeight: Mycroft.Units.gridUnit * 4
                    placeholderText: "Example: http://192.168.x.x:6712"
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
            }
        }

        RowLayout {
            id: bottomArea
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: Kirigami.Units.largeSpacing
            anchors.leftMargin: Kirigami.Units.largeSpacing
            anchors.rightMargin: Kirigami.Units.largeSpacing
            height: Kirigami.Units.gridUnit * 2

            Button {
                id: btnbaAccept
                Layout.fillWidth: true
                Layout.fillHeight: true

                background: Rectangle {
                    color: btnbaAccept.down ? "transparent" :  Kirigami.Theme.highlightColor
                    border.width: 3
                    border.color: Qt.darker(Kirigami.Theme.highlightColor, 1.2)
                    radius: 10

                    Rectangle {
                        width: parent.width - 12
                        height: parent.height - 12
                        anchors.centerIn: parent
                        color: btnbaAccept.down ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.backgroundColor, 1.25)
                        radius: 5
                    }
                }

                contentItem: Kirigami.Heading {
                    level: 3
                    wrapMode: Text.WordWrap
                    font.bold: true
                    color: Kirigami.Theme.textColor
                    text: "Confirm"
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }

                onClicked: {
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                    triggerGuiEvent("mycroft.device.local.setup.host.address", {"host_address": hostAddressField.text})
                }
            }
        }
    }
}

