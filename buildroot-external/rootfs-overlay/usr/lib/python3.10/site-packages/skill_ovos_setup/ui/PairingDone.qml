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

import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        color: Kirigami.Theme.backgroundColor
        anchors.fill: parent

        ColumnLayout {
            anchors.fill: parent

            Kirigami.Heading {
                id: hey
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                horizontalAlignment: Text.AlignHCenter
                maximumLineCount: 1
                elide: Text.ElideRight
                fontSizeMode: Text.Fit
                minimumPixelSize: 8
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 50
                color: Kirigami.Theme.highlightColor
                text: "Hey Mycroft"
            }
            Kirigami.Heading {
                id: example1
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                fontSizeMode: Text.Fit
                minimumPixelSize: 8
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 35
                color: Kirigami.Theme.textColor
                text: "What's the\nweather?"
            }
            Kirigami.Heading {
                id: example2
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                fontSizeMode: Text.Fit
                minimumPixelSize: 8
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 35
                color: Kirigami.Theme.textColor
                text: "Tell me about\nAbraham Lincoln"
            }
            Kirigami.Heading {
                id: example3
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                fontSizeMode: Text.Fit
                minimumPixelSize: 8
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 35
                color: Kirigami.Theme.textColor
                text: "Play the News"
            }
        }
    }
}  
