/*
 * Copyright 2022 by Aditya Mehra <aix.m@outlook.com>
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
import QtQuick.Layouts 1.4
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0

Mycroft.CardDelegate {
    id: root
    skillBackgroundColorOverlay: "#E8ECEF"
    cardBackgroundOverlayColor: "#E8ECEF"
    cardRadius: 0
    fillWidth: true

    onFocusChanged: {
        if(focus) {
            triggerGuiEvent("ovos.notes.skill.change.notes.mode", {"mode": 1})
        }
    }

    onVisibleChanged: {
        if(visible) {
            triggerGuiEvent("ovos.notes.skill.change.notes.mode", {"mode": 1})
        }
    }

    Image {
        anchors.fill: parent
        anchors.margins: -Mycroft.Units.gridUnit * 2
        source: Qt.resolvedUrl("images/papercanvas.png")
        opacity: 0.2
        z: 1
    }

    ColumnLayout {
        anchors.bottom: bottomBarArea.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Mycroft.Units.gridUnit / 2

        Rectangle {
            Layout.preferredWidth: Mycroft.Units.gridUnit * 22
            Layout.preferredHeight: Mycroft.Units.gridUnit * 3
            radius: 10
            color: "#222"
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 16
                color: Qt.rgba(0, 0, 0, 0.5)
                transparentBorder: true
                horizontalOffset: 2
                verticalOffset: 2
            }

            Kirigami.Heading {
                id: personalNotesHeading
                level: 1
                text: "Your Personal Note #" + sessionData.noteNumber
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.weight: Font.Bold
                color: "white"
            }
        }

        Kirigami.Separator {
            Layout.fillWidth: true
            Layout.leftMargin: Mycroft.Units.gridUnit
            Layout.rightMargin: Mycroft.Units.gridUnit
            Layout.preferredHeight: 1
            color: "#9f9f9f"
        }

        Rectangle {
            color: "#FCFAF4"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.topMargin: Mycroft.Units.gridUnit / 2
            radius: 6
            border.color: "#222"
            border.width: 1
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 16
                color: "#000000"
                transparentBorder: true
                horizontalOffset: 0
                verticalOffset: 0
            }


            Image {
                anchors.fill: parent
                fillMode: Image.PreserveAspectCrop
                source: Qt.resolvedUrl("images/notebook.png")

                Mycroft.AutoFitLabel {
                    id: textFrameMainBody
                    wrapMode: Text.Wrap
                    font.family: "Noto Sans"
                    anchors.fill: parent
                    font.weight: Font.Medium
                    text: sessionData.personalNoteText
                    color: "#222"
                }
            }
        }
    }

    RowLayout {
        id: bottomBarArea
        width: parent.width
        height: Mycroft.Units.gridUnit * 4
        anchors.bottom: parent.bottom

        Rectangle {
            color: "#f9f1f1"
            radius: 10
            Layout.fillWidth: true
            Layout.preferredHeight: Mycroft.Units.gridUnit * 3
            border.color: "#222"
            border.width: 1
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 16
                color: "#000000"
                transparentBorder: true
                horizontalOffset: 0
                verticalOffset: 0
            }

            Kirigami.Icon {
                anchors.centerIn: parent
                width: parent.height * 0.6
                height: width
                source: "document-edit"
                color: "#222"
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    triggerGuiEvent("ovos.notes.skill.edit.current.note", {})
                }
            }
        }

        Rectangle {
            color: "#f9f1f1"
            radius: 10
            Layout.fillWidth: true
            Layout.preferredHeight: Mycroft.Units.gridUnit * 3
            border.color: "#222"
            border.width: 1
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 16
                color: "#000000"
                transparentBorder: true
                horizontalOffset: 0
                verticalOffset: 0
            }

            Kirigami.Icon {
                anchors.centerIn: parent
                width: parent.height * 0.6
                height: width
                source: "arrow-left"
                color: "#222"
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    triggerGuiEvent("ovos.notes.skill.reset.current.note", {})
                }
            }
        }

        Rectangle {
            color: "#f9f1f1"
            radius: 10
            Layout.fillWidth: true
            Layout.preferredHeight: Mycroft.Units.gridUnit * 3
            border.color: "#222"
            border.width: 1
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 16
                color: "#000000"
                transparentBorder: true
                horizontalOffset: 0
                verticalOffset: 0
            }

            Kirigami.Icon {
                anchors.centerIn: parent
                width: parent.height * 0.6
                height: width
                source: "edit-delete"
                color: "#222"
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    triggerGuiEvent("ovos.notes.skill.remove.current.note", {})
                }
            }
        }
    }
}
