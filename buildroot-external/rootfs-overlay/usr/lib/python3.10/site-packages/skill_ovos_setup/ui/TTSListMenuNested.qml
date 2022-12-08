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
    id: ttsListView
    anchors.fill: parent
    property bool horizontalMode: root.width > root.height ? 1 : 0
    property var ttsEnginesModel: sessionData.tts_engines
    property int listmode: 0

    function get_image_on_supported_gender(gen) {
        if(gen == "male") {
            return Qt.resolvedUrl("icons/male.png")
        } else {
            return Qt.resolvedUrl("icons/female.png")
        }
    }

    function isOffline(check) {
        if(check) {
            return "Offline"
        } else {
            return "Online"
        }
    }

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        border.color: Kirigami.Theme.highlightColor
        border.width: 1
        width: parent.width * 0.80
        height: Mycroft.Units.gridUnit * 4
        anchors.centerIn: parent
        visible: qViewL.count > 0 ? 0 : 1
        enabled: qViewL.count > 0 ? 0 : 1
        z: 5

        Label {
            id: errorLabelOnEmptyList
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            text: qsTr("Error: TTS Engines Not Available")
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
                source: Qt.resolvedUrl("icons/tts.svg")
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
                text: qsTr("Configure Text to Speech")
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

        ScrollBar {
            id: listViewScrollBar
            anchors.right: parent.right
            anchors.rightMargin: Mycroft.Units.gridUnit
            anchors.top: middleArea.top
            anchors.bottom: middleArea.bottom
            policy: ScrollBar.AsNeeded
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
                font.pixelSize: horizontalMode ? (ttsListView.height > 600 ? topArea.height * 0.4 : topArea.height * 0.25) : topArea.height * 0.3
                text: qsTr("Text-To-Speech (TTS) is the process of converting strings of text into audio of spoken words")
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.largeSpacing
            }

            ListView {
                id: qViewL
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: ttsEnginesModel
                clip: true
                currentIndex: -1
                spacing: 5
                property int cellWidth: qViewL.width
                property int cellHeight: qViewL.height / 4.6

                ScrollBar.vertical: listViewScrollBar
                
                delegate: ItemDelegate {
                    width: qViewL.cellWidth
                    height: Math.max(qViewL.cellHeight, Kirigami.Units.gridUnit * 2)

                    background: Rectangle {
                        id: delegateSttListBg
                        radius: 10
                        color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: Qt.darker(Kirigami.Theme.textColor, 2.5)
                        border.width: 1
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        if(ttsListView.listmode  == 0) {
                            ttsListView.listmode = 1
                            qViewL.model = model.options
                        }

                        if(ttsListView.listmode == 1) {
                            triggerGuiEvent("mycroft.device.confirm.tts", {
                            "plugin_name": modelData.plugin_name,
                            "plugin_type": "tts",
                            "display_name": modelData.display_name,
                            "offline": modelData.offline,
                            "lang": modelData.lang,
                            "gender": modelData.gender,
                            "engine": modelData.engine,
                            })
                        }
                    }

                    onPressed: {
                        delegateSttListBg.color = Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.5)
                    }

                    onReleased: {
                        delegateSttListBg.color = Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                    }

                    Rectangle {
                        id: symb
                        anchors.left: parent.left
                        anchors.leftMargin: Kirigami.Units.smallSpacing
                        anchors.verticalCenter: parent.verticalCenter
                        height: Mycroft.Units.gridUnit
                        width: Mycroft.Units.gridUnit
                        color: Kirigami.Theme.highlightColor
                        radius: 6
                    }

                    Label {
                        id: cItm
                        anchors.left: symb.right
                        anchors.leftMargin: Kirigami.Units.largeSpacing
                        anchors.right: symbSuffGender.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        wrapMode: Text.WordWrap
                        anchors.margins: Kirigami.Units.smallSpacing
                        verticalAlignment: Text.AlignVCenter
                        color: Kirigami.Theme.textColor
                        font.capitalization: Font.AllUppercase
                        text: ttsListView.listmode  == 1 ? modelData.plugin_name + " | " + modelData.display_name : model.plugin_name
                    }

                    Rectangle {
                        id: symbSuffGender
                        anchors.right: symbSuff.left
                        anchors.rightMargin: Kirigami.Units.smallSpacing
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height - Kirigami.Units.largeSpacing
                        width: Mycroft.Units.gridUnit * 10
                        color: Kirigami.Theme.highlightColor
                        radius: 6
                        visible: ttsListView.listmode  == 1 ? 1 : 0
                        enabled: ttsListView.listmode  == 1 ? 1 : 0

                        Label {
                            id: cItmSuffGender
                            anchors.centerIn: parent
                            wrapMode: Text.WordWrap
                            anchors.margins: Kirigami.Units.smallSpacing
                            verticalAlignment: Text.AlignVCenter
                            color: Kirigami.Theme.textColor
                            font.capitalization: Font.AllUppercase
                            font.bold: true
                            text: modelData.gender
                        }
                    }

                    RowLayout {
                        visible: ttsListView.listmode  == 0 ? 1 : 0
                        enabled: ttsListView.listmode  == 0 ? 1 : 0
                        anchors.right: symbSuff.left
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.rightMargin: Kirigami.Units.smallSpacing
                        height: parent.height - Kirigami.Units.largeSpacing
                        width: Mycroft.Units.gridUnit * 14

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            radius: 6
                            visible: model.supports_male_voice
                            enabled: model.supports_male_voice

                            Image {
                                anchors.centerIn: parent                                
                                width: Kirigami.Units.iconSizes.medium
                                height: Kirigami.Units.iconSizes.medium
                                source: Qt.resolvedUrl("icons/male.svg")
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            radius: 6
                            visible: model.supports_female_voice
                            enabled: model.supports_female_voice

                            Image {
                                anchors.centerIn: parent                                
                                width: Kirigami.Units.iconSizes.medium
                                height: Kirigami.Units.iconSizes.medium
                                source: Qt.resolvedUrl("icons/female.svg")
                            }
                        }
                    }

                    Rectangle {
                        id: symbSuff
                        anchors.right: parent.right
                        anchors.rightMargin: Kirigami.Units.smallSpacing
                        anchors.verticalCenter: parent.verticalCenter
                        height: parent.height - Kirigami.Units.largeSpacing
                        width: Mycroft.Units.gridUnit * 10
                        color: Kirigami.Theme.highlightColor
                        radius: 6

                        Label {
                            id: cItmSuff
                            anchors.centerIn: parent
                            wrapMode: Text.WordWrap
                            anchors.margins: Kirigami.Units.smallSpacing
                            verticalAlignment: Text.AlignVCenter
                            color: Kirigami.Theme.textColor
                            font.capitalization: Font.AllUppercase
                            font.bold: true
                            visible: ttsListView.listmode  == 1 ? 1 : 0
                            enabled: ttsListView.listmode  == 1 ? 1 : 0
                            text: isOffline(modelData.offline)
                        }

                        RowLayout {
                            visible: ttsListView.listmode  == 0 ? 1 : 0
                            enabled: ttsListView.listmode  == 0 ? 1 : 0
                            anchors.fill: parent

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                                radius: 6
                                visible: model.supports_online_mode
                                enabled: model.supports_online_mode

                                Kirigami.Icon {
                                    anchors.centerIn: parent                                
                                    width: Kirigami.Units.iconSizes.medium
                                    height: Kirigami.Units.iconSizes.medium
                                    source: "network-connect"
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                                radius: 6
                                visible: model.supports_offline_mode
                                enabled: model.supports_offline_mode

                                Kirigami.Icon {
                                    anchors.centerIn: parent                                
                                    width: Kirigami.Units.iconSizes.medium
                                    height: Kirigami.Units.iconSizes.medium
                                    source: "network-disconnect"
                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            id: bottomArea
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: Kirigami.Units.gridUnit * 2
            color: Kirigami.Theme.highlightColor

            Label {
                anchors.fill: parent
                wrapMode: Text.WordWrap
                anchors.margins: Kirigami.Units.smallSpacing
                verticalAlignment: Text.AlignVCenter
                color: Kirigami.Theme.textColor
                text: qsTr("Select a TTS engine to view the available voices")
            }
        }
    }
} 
