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

    property var allNotes: sessionData.allNotesModel.allNotes

    onFocusChanged: {
        if(focus) {
            triggerGuiEvent("ovos.notes.skill.change.notes.mode", {"mode": 2})
        }
    }

    onVisibleChanged: {
        if(visible) {
            triggerGuiEvent("ovos.notes.skill.change.notes.mode", {"mode": 2})
        }
    }

    onAllNotesChanged: {
        console.log(allNotes)
    }

    Image {
        anchors.fill: parent
        anchors.margins: -Mycroft.Units.gridUnit * 2
        source: Qt.resolvedUrl("images/papercanvas.png")
        opacity: 0.2
        z: 1
    }

    ColumnLayout {
        id: headerLayout
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: Mycroft.Units.gridUnit * 3.5
        z: 2

        Rectangle {
            Layout.preferredWidth: Mycroft.Units.gridUnit * 20
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
                id: allNotesViewHeading
                level: 1
                text: "Your Recent Notes"
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
    }

    ListView {
        id: notesListView
        anchors.top: headerLayout.bottom
        anchors.bottom: homeBtn.top
        anchors.margins: Mycroft.Units.gridUnit / 8
        width: parent.width
        snapMode: ListView.SnapToItem
        spacing: Mycroft.Units.gridUnit / 2
        orientation: ListView.Horizontal
        clip: true
        model: sessionData.allNotesModel.allNotes
        z: 2

        Component.onCompleted: {
            notesListView.positionViewAtIndex(0, ListView.Beginning)
        }

        property real columns: 3.5
        readonly property real cellWidth: width / columns

        delegate: NoteCardDelegate {}

        move: Transition {
            SmoothedAnimation {
                property: "x"
                duration: Kirigami.Units.longDuration
            }
        }
    }

    Mycroft.AutoFitLabel {
        visible: notesListView.count == 0
        enabled: notesListView.count == 0
        anchors.centerIn: parent
        width: parent.width
        height: Mycroft.Units.gridUnit * 6
        wrapMode: Text.Wrap
        text: "Oops! No Personal Notes Available"
        color: "#222"
        z: 2
    }

    Kirigami.Separator {
        width: parent.width
        anchors.bottom: createBtn.top
        anchors.leftMargin: Mycroft.Units.gridUnit
        anchors.rightMargin: Mycroft.Units.gridUnit
        anchors.bottomMargin: Mycroft.Units.gridUnit / 2
        height: 1
        color: "#9f9f9f"
        z: 2
    }

    Rectangle {
        id: createBtn
        color: "#f9f1f1"
        radius: 10
        width: parent.width / 2.5
        height: Mycroft.Units.gridUnit * 3
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        border.color: "#222"
        border.width: 1
        z: 2
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
            source: "list-add"
            color: "#222"
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                triggerGuiEvent("ovos.notes.skill.add.note", {})
            }
        }
    }

    Rectangle {
        id: homeBtn
        color: "#f9f1f1"
        radius: 10
        width: parent.width / 2.5
        height: Mycroft.Units.gridUnit * 3
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        border.color: "#222"
        border.width: 1
        z: 2
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
                triggerGuiEvent("ovos.notes.skill.release.skill", {})
            }
        }
    }
}
