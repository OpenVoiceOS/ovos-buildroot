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

Mycroft.ProportionalDelegate {
    id: root
    property var spacingUnit: 30
    property var phone: sessionData.phone_image
    property var prompt: sessionData.prompt
    property var highlight: sessionData.highlight

    Row {
        spacing: spacingUnit
        Image {
            id: img
            source: Qt.resolvedUrl(phone)
            Layout.fillHeight: true
            height: root.height * 0.8
            fillMode: Image.PreserveAspectFit
            verticalAlignment: Image.AlignBottom
            anchors.bottom: parent.bottom
        }
        ColumnLayout {
            Kirigami.Heading {
                id: sentence
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                Layout.leftMargin: spacingUnit
                Layout.topMargin: 80
                horizontalAlignment: Text.AlignHLeft
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 38
                visible: !content.visible
                text: prompt
            }
            Kirigami.Heading {
                id: url
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft
                Layout.leftMargin: spacingUnit
                horizontalAlignment: Text.AlignHLeft
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: 36
                visible: !content.visible
                color: "#22a7f0"
                text: highlight
            }
        }
    }
}  
