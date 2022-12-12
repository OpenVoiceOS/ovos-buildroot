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
import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import org.kde.kirigami 2.11 as Kirigami

Rectangle {
    id: alarmCardBoxView
    color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
    property alias alarmName: alarmCardLabel.text
    property alias alarmTime: alarmGraphicalIndicator.text
    property alias alarmExpired: alarmGraphicalIndicator.expired
    property alias alarmAmPm: alarmAmPmLabel.text
    radius: 6

    RowLayout {
        id: columnTwoRowLayoutOne
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height / 2

        Item {
            Layout.preferredWidth: parent.width / 2
            Layout.fillHeight: true
            Layout.margins: Mycroft.Units.gridUnit / 4

            Kirigami.Icon {
                id: alarmCardIcon
                width: parent.height * 0.8
                height: width
                anchors.centerIn: parent   
                source: "alarm-symbolic"
                color: Kirigami.Theme.textColor
            }
        }

        Label {
            id: alarmCardLabel
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Mycroft.Units.gridUnit / 4
            text: alarmCardBoxView.alarmName
            maximumLineCount: 1
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            minimumPixelSize: 5
            font.pixelSize: 42
            fontSizeMode: Text.Fit
            font.bold: true
            color: Kirigami.Theme.textColor
        }
    }

    RowLayout {
        id: columnTwoRowLayoutTwo
        anchors.top: columnTwoRowLayoutOne.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height / 2

        AlarmBoxControl {
            id: alarmGraphicalIndicator
            Layout.preferredWidth: parent.width / 2
            Layout.fillHeight: true
            Layout.margins: Mycroft.Units.gridUnit / 4
            text: alarmCardBoxView.alarmTime
            expired: alarmCardBoxView.alarmExpired
        }

        Label {
            id: alarmAmPmLabel
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Mycroft.Units.gridUnit / 4
            text: alarmCardBoxView.alarmAmPm
            maximumLineCount: 1
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            minimumPixelSize: 5
            font.pixelSize: 42
            fontSizeMode: Text.Fit
            font.bold: true
            color: Kirigami.Theme.textColor
        }
    }
}