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

    property var welcome_words_model: ["Welkom", "Wellkumma", "أهلاً و سهلاً", "Ghini vinit!", "Bienveníu", "I ni sɛ", "Сәләм бирем!", "Прывiтанне", "Benvinguts", "歡迎", "Vítáme tĕ", "Velkommen", "Bienvenue", "Benvido", "Willkommen", "Καλώς Όρισες", "स्वागत", "ようこそ", "ಸುಸ್ವಾಗತ", "Bem-vindos", "መርሓባ"]

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        anchors.fill: parent

        GridLayout {
            anchors.fill: parent
            columns: 3

            Repeater {
                model: backendView.welcome_words_model
                delegate: Label {
                    text: modelData
                    font.pixelSize: 30
                    Layout.alignment: Qt.AlignHCenter
                    color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.2)
                    opacity: 0.8
                    layer.enabled: true
                    layer.effect: DropShadow {
                        color: Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                        horizontalOffset: 0
                        verticalOffset: 0
                        radius: 10
                        samples: 16
                    }
                }
            }
        }

        ColumnLayout {
            id: fullArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: Mycroft.Units.gridUnit * 1
            spacing: 8

            Label {
                id: welcomeHeader
                Layout.alignment: Qt.AlignHCenter | Qt.AlignTop                
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: qsTr("Welcome to OpenVoice OS")
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.weight: Font.ExtraBold
                font.pixelSize: horizontalMode ? fullArea.height * 0.12 : fullArea.width * 0.10
                elide: Text.ElideLeft
                maximumLineCount: 2
                color: Kirigami.Theme.textColor
                layer.enabled: true
                layer.effect: DropShadow {                    
                    horizontalOffset: 0
                    verticalOffset: 0
                    radius: 10
                    samples: 16
                    color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.4)
                    source: welcomeHeader
                }
            }

            Image {
                id: welcomePageImage
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.fillHeight: true
                source: Qt.resolvedUrl("icons/ovos-welcome.svg")
                fillMode: Image.PreserveAspectFit
                opacity: 0.9
                layer.enabled: true
                layer.effect: DropShadow {                    
                    horizontalOffset: 0
                    verticalOffset: 0
                    radius: 10
                    samples: 16
                    opacity: 0.9
                    color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.4)
                    source: welcomePageImage
                }                
            }

            Label {
                id: welcomeSubHeader
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                Layout.fillWidth: true                
                wrapMode: Text.WordWrap
                text: qsTr("Let's get your device set up")
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: horizontalMode ? fullArea.height * 0.09 : fullArea.width * 0.09
                elide: Text.ElideLeft
                maximumLineCount: 2
                color: Kirigami.Theme.textColor
                layer.enabled: true
                layer.effect: DropShadow {                    
                    horizontalOffset: 0
                    verticalOffset: 0
                    radius: 10
                    samples: 16
                    color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.4)
                    source: welcomeSubHeader
                }
            }
        }
    }
}