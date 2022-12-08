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

import QtQuick.Layouts 1.12
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Item {
    id: backendView
    anchors.fill: parent
    property bool horizontalMode: backendView.width > backendView.height ? 1 : 0

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        anchors.fill: parent

        Rectangle {
            id: topArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: Kirigami.Units.gridUnit * 4
            color: Kirigami.Theme.highlightColor

            Kirigami.Icon {
                id: topAreaIcon
                source: "emblem-system-symbolic"
                width: Kirigami.Units.iconSizes.large
                height: width
                anchors.left: parent.left
                anchors.leftMargin: Mycroft.Units.gridUnit * 2
                anchors.verticalCenter: parent.verticalCenter

                ColorOverlay {
                    anchors.fill: parent
                    source: topAreaIcon
                    color: Kirigami.Theme.textColor
                }
            }

            Label {
                id: selectLanguageHeader
                anchors.left: topAreaIcon.right
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.leftMargin: Mycroft.Units.gridUnit
                text: qsTr("Select Your Backend")
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: topArea.height * 0.4
                elide: Text.ElideLeft
                maximumLineCount: 1
                color: Kirigami.Theme.textColor
            }

            Kirigami.Separator {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.largeSpacing
                height: 1
                color: Kirigami.Theme.textColor
            }
        }

        ColumnLayout {
            id: middleArea
            anchors.bottom: bottomArea.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: topArea.bottom
            anchors.margins: Mycroft.Units.gridUnit * 2
        
            Label {
                id: warnText
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                wrapMode: Text.WordWrap
                font.pixelSize: horizontalMode ? (backendView.height > 600 ? topArea.height * 0.4 : topArea.height * 0.25) : topArea.height * 0.3
                color: Kirigami.Theme.textColor
                text: qsTr("A backend provides services used by OpenVoiceOS Core")
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: horizontalMode ? Kirigami.Units.largeSpacing : 0
        
                GridLayout {
                    id: backendsGrid
                    anchors.fill: parent
                    z: 1
                    columns: horizontalMode ? 3 : 1
                    columnSpacing: Kirigami.Units.largeSpacing
                    Layout.alignment: Qt.AlignVCenter

                    BackendButton {
                        id: bt1
                        backendName: "Selene " + qsTr("Backend")
                        backendIcon: Qt.resolvedUrl("icons/selene.svg")
                        backendType: "selene"
                        horizontalMode: backendView.horizontalMode

                        Layout.preferredWidth: horizontalMode ? (parent.width / 3 - Kirigami.Units.gridUnit) : parent.width
                        Layout.fillHeight: true
                    }

                    BackendButton {
                        id: bt2
                        backendName: qsTr("Personal Backend")
                        backendIcon: Qt.resolvedUrl("icons/personal.svg")
                        backendType: "personal"
                        horizontalMode: backendView.horizontalMode
                        
                        Layout.preferredWidth: horizontalMode ? (parent.width / 3 - Kirigami.Units.gridUnit) : parent.width
                        Layout.fillHeight: true
                    }

                    BackendButton {
                        id: bt3
                        backendName: qsTr("No Backend")
                        backendIcon: Qt.resolvedUrl("icons/nobackend.svg")
                        backendType: "offline"
                        horizontalMode: backendView.horizontalMode

                        Layout.preferredWidth: horizontalMode ? (parent.width / 3 - Kirigami.Units.gridUnit) : parent.width
                        Layout.fillHeight: true
                    }
                }
            }
        }


        Rectangle {
            id: bottomArea
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Kirigami.Units.gridUnit * 3
            color: Kirigami.Theme.highlightColor

            RowLayout {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.largeSpacing

                Button {
                    id: btnba1
                    Layout.preferredWidth: backendView.horizontalMode ? parent.width / 2 : parent.width
                    Layout.fillHeight: true
                    enabled: sessionData.language_selection_enabled ? Boolean(sessionData.language_selection_enabled) : 0
                    visible: sessionData.language_selection_enabled ? Boolean(sessionData.language_selection_enabled) : 0

                    background: Rectangle {
                        color: btnba1.down ? "transparent" :  Kirigami.Theme.backgroundColor
                        border.width: 3
                        border.color: Kirigami.Theme.backgroundColor
                        radius: 3
                    }

                    contentItem: Item {
                        RowLayout {
                            anchors.centerIn: parent

                            Kirigami.Icon {
                                Layout.fillHeight: true
                                Layout.preferredWidth: height
                                Layout.alignment: Qt.AlignVCenter
                                source: "arrow-left"
                            }

                            Kirigami.Heading {
                                level: 2
                                Layout.fillHeight: true          
                                wrapMode: Text.WordWrap
                                font.bold: true
                                color: Kirigami.Theme.textColor
                                text: qsTr("Language Selection")
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                            }
                        }
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        triggerGuiEvent("mycroft.return.select.language", {})
                    }
                }
            }
        }
    }
}
