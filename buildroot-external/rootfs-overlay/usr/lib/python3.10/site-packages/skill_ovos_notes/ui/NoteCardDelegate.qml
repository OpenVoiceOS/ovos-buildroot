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

Controls.ItemDelegate {
    width: notesListView.cellWidth
    height: notesListView.height

    background: Rectangle {
        color: "transparent"
    }

    contentItem: Item {
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit / 2

        ColumnLayout {
            width: parent.width
            height: parent.height
            spacing: Mycroft.Units.gridUnit / 2

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignHCenter
                radius: 6
                color: "#FCFAF4"
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
                        anchors.bottomMargin: Mycroft.Units.gridUnit * 2
                        font.weight: Font.Medium
                        text: modelData.note_text
                        color: "#222"
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        triggerGuiEvent("ovos.notes.skill.open.selected.note", {"file_name": modelData.file_name})
                    }
                }

                Rectangle {
                    color: "#383838"
                    radius: 6
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom

                    anchors.leftMargin: Mycroft.Units.gridUnit * 1.2
                    anchors.rightMargin: Mycroft.Units.gridUnit * 1.2
                    height: Mycroft.Units.gridUnit * 2
                    layer.enabled: true
                    layer.effect: DropShadow {
                        radius: 8
                        samples: 16
                        color: Qt.rgba(0, 0, 0, 0.5)
                        transparentBorder: true
                        horizontalOffset: 0
                        verticalOffset: -4
                    }


                    Controls.Label {
                        wrapMode: Text.Wrap
                        font.family: "Noto Sans"
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font.weight: Font.Light
                        text: "Note #" + modelData.note_number
                        color: "#f9f1f1"
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: Mycroft.Units.gridUnit * 4
                Layout.alignment: Qt.AlignHCenter

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
                            triggerGuiEvent("ovos.notes.skill.open.selected.note", {"file_name": modelData.file_name})
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
                            triggerGuiEvent("ovos.notes.skill.remove.selected.note", {"file_name": modelData.file_name})
                        }
                    }
                }
            }
        }
    }
}
