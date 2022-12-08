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
    id: alarmCardColumnThree
    color: Kirigami.Theme.backgroundColor
    property var alarmName
    property var alarmIndex
    property var alarmContext
    property var alarmExpired

    RowLayout {
        id: columnThreeRowLayout
        anchors.fill: parent
        anchors.bottomMargin: Mycroft.Units.gridUnit

        Button {
            id: snoozeButton
            Layout.fillWidth: true                    
            Layout.fillHeight: true
            enabled: alarmExpired ? 1 : 0

            background: Rectangle {
                id: snoozeButtonBackground
                color: Kirigami.Theme.highlightColor
                border.color: Qt.darker(Kirigami.Theme.highlightColor, 1.5)
                border.width: 1
                radius: 6
            }

            contentItem: RowLayout {
                Kirigami.Icon {
                    id: snoozeButtonIcon
                    Layout.preferredWidth: parent.height * 0.8
                    Layout.preferredHeight: width
                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                    source: "media-playback-pause"
                    color: Kirigami.Theme.textColor
                }
                Text {
                    text: "Snooze"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    minimumPixelSize: 5
                    font.pixelSize: 25
                    fontSizeMode: Text.Fit
                    font.bold: true
                    color: Kirigami.Theme.textColor
                }
            }
            onClicked: {
                Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                triggerGuiEvent("ovos.alarm.skill.snooze", {"alarmIndex": alarmIndex, "alarmContext": alarmContext, "alarmName": alarmName})
            }

            onPressed: {
                snoozeButtonBackground.color = Kirigami.Theme.backgroundColor
            }

            onReleased: {
                snoozeButtonBackground.color = Kirigami.Theme.highlightColor
            }
        }

        Button {
            id: cancelButton
            Layout.fillWidth: true                    
            Layout.fillHeight: true

            background: Rectangle {
                id: cancelButtonBackground
                color: Kirigami.Theme.highlightColor
                border.color: Qt.darker(Kirigami.Theme.highlightColor, 1.5)
                border.width: 1
                radius: 6
            }
            
            contentItem: RowLayout {
                Kirigami.Icon {
                    id: cancelButtonIcon
                    Layout.preferredWidth: parent.height * 0.8
                    Layout.preferredHeight: width
                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                    source: "dialog-cancel"
                    color: Kirigami.Theme.textColor
                }
                Text {
                    text: alarmExpired ? qsTr("Dismiss") : qsTr("Cancel")
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    minimumPixelSize: 5
                    font.pixelSize: 25
                    fontSizeMode: Text.Fit
                    font.bold: true
                    color: Kirigami.Theme.textColor
                }
            }
            onClicked: {
                Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                triggerGuiEvent("ovos.alarm.skill.cancel", {"alarmIndex": alarmIndex, "alarmContext": alarmContext, "alarmName": alarmName})
            }

            onPressed: {
                cancelButtonBackground.color = Kirigami.Theme.backgroundColor
            }

            onReleased: {
                cancelButtonBackground.color = Kirigami.Theme.highlightColor
            }
        }
    }
}