/*
 * Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
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
import Mycroft 1.0 as Mycroft

Item {
    id: root
    property var code: sessionData.code
    property var backendurl: "account.mycroft.ai/pair"
    anchors.fill: parent
    property bool horizontalMode: root.width > root.height ? 1 :0

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2

        GridLayout {
            id: colLay
            anchors.fill: parent
            columns: horizontalMode ? 1 : 1
            columnSpacing: Kirigami.Units.largeSpacing
            Layout.alignment: horizontalMode ? Qt.AlignVCenter : Qt.AlignTop

            ColumnLayout {
                Layout.preferredWidth: horizontalMode ? parent.width / 1.5 : parent.width
                Layout.preferredHeight: horizontalMode ? parent.height : parent.height / 2
                Layout.alignment: horizontalMode ? Qt.AlignVCenter : Qt.AlignTop

                Kirigami.Heading {
                    id: sentence3
                    Layout.fillWidth: true
                    Layout.alignment: horizontalMode ? Qt.AlignVCenter | Qt.AlignLeft : Qt.AlignTop | Qt.AlignLeft
                    wrapMode: Text.WordWrap
                    elide: Text.ElideRight
                    font.weight: Font.Bold
                    font.pixelSize: horizontalMode ? root.width * 0.07 : root.height * 0.04
                    horizontalAlignment: Text.AlignHCenter
                    color: Kirigami.Theme.textColor
                    text: qsTr("Pair this device at")
                }
                Kirigami.Heading {
                    id: sentence3b
                    Layout.fillWidth: true
                    Layout.alignment: horizontalMode ? Qt.AlignVCenter | Qt.AlignLeft : Qt.AlignTop | Qt.AlignLeft
                    wrapMode: Text.WordWrap
                    elide: Text.ElideRight
                    font.weight: Font.Bold
                    font.pixelSize: horizontalMode ? root.width * 0.07 : root.height * 0.04
                    horizontalAlignment: Text.AlignHCenter
                    color: Kirigami.Theme.highlightColor
                    text: root.backendurl
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignTop
                    color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)

                    Kirigami.Heading {
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                        elide: Text.ElideRight
                        font.weight: Font.Bold
                        font.pixelSize: horizontalMode ? root.width * 0.12 : root.height * 0.05
                        color: Kirigami.Theme.highlightColor
                        text: root.code
                    }
                }
            }
        }
    }
}  
