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
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Item {
    id: backendView
    anchors.fill: parent

    property bool horizontalMode: backendView.width > backendView.height ? 1 :0

    ListModel {
        id: backendFeatureList
        ListElement {
            text: QT_TR_NOOP("No Pairing Required")
        }
        ListElement {
            text: QT_TR_NOOP("Multiple configurable STT Options")
        }
        ListElement {
            text: QT_TR_NOOP("Multiple configurable TTS Options")
        }
        ListElement {
            text: QT_TR_NOOP("No internet needed")
        }
    }

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
                source: Qt.resolvedUrl("icons/nobackend.svg")
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
                text: qsTr("No Backend")
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
                horizontalAlignment: Text.AlignLeft
                color: Kirigami.Theme.textColor
                wrapMode: Text.WordWrap
                font.pixelSize: horizontalMode ? (backendView.height > 600 ? topArea.height * 0.4 : topArea.height * 0.25) : topArea.height * 0.3
                text: qsTr("Allows your device to work offline")
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.largeSpacing
            }

            ListView {
                id: qViewL
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: backendFeatureList
                clip: true
                currentIndex: -1
                spacing: 5
                property int cellWidth: qViewL.width
                property int cellHeight: qViewL.height / 4.6
                delegate: Rectangle {
                    width: qViewL.cellWidth
                    height: qViewL.cellHeight
                    radius: 10
                    color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)

                    Rectangle {
                        id: symb
                        anchors.left: parent.left
                        anchors.leftMargin: Kirigami.Units.smallSpacing
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height - Kirigami.Units.largeSpacing
                        width: Kirigami.Units.iconSizes.medium
                        color: Kirigami.Theme.highlightColor
                        radius: width
                    }

                    Label {
                        id: cItm
                        anchors.left: symb.right
                        anchors.leftMargin: Kirigami.Units.largeSpacing
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        wrapMode: Text.WordWrap
                        anchors.margins: Kirigami.Units.smallSpacing
                        verticalAlignment: Text.AlignVCenter
                        color: Kirigami.Theme.textColor
                        text: qsTr(model.text)
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
                    Layout.fillWidth: true
                    Layout.fillHeight: true

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
                                text: qsTr("Backend Selection")
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignLeft
                            }
                        }
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        triggerGuiEvent("mycroft.return.select.backend", {"page": "offline"})
                    }
                }

                Button {
                    id: btnba2
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    background: Rectangle {
                        color: btnba2.down ? "transparent" :  Kirigami.Theme.backgroundColor
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
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                source: "dialog-ok-apply"
                            }

                            Kirigami.Heading {
                                level: 2
                                Layout.fillHeight: true
                                Layout.alignment: Qt.AlignRight          
                                wrapMode: Text.WordWrap
                                font.bold: true
                                color: Kirigami.Theme.textColor
                                text: qsTr("Confirm")
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignRight
                            }
                        }
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        triggerGuiEvent("mycroft.device.confirm.backend", {"backend": "offline"})
                    }
                }
            }
        }
    }
} 
