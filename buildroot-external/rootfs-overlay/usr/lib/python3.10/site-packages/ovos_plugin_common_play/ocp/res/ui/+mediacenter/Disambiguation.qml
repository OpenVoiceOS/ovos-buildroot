/*
 * Copyright 2020 by Aditya Mehra <aix.m@outlook.com>
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

import QtQuick 2.9
import QtQuick.Controls 2.3 as Controls
import QtQuick.Layouts 1.3
import org.kde.kirigami 2.8 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft


Item {
    id: disambiguationViewPage
    property var disambiguationModel: sessionData.searchModel
    property Component emptyHighlighter: Item{}

    onFocusChanged: {
        if (focus) {
            disambiguationListView.forceActiveFocus()
        }
    }

    onDisambiguationModelChanged: {
        disambiguationListView.forceLayout()
    }

    function formatedDuration(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    ColumnLayout {
        id: playlistPlayerColumn
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading {
            id: watchItemList
            text: "Search Results"
            color: Kirigami.Theme.textColor
            level: 2
        }

        Kirigami.Separator {
            id: sept2
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            z: 100
        }

        ListView {
            id: disambiguationListView
            keyNavigationEnabled: true
            model: disambiguationModel.data
            focus: false
            interactive: true
            bottomMargin: delegate.controlBarItem.height + Kirigami.Units.largeSpacing
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Kirigami.Units.largeSpacing
            currentIndex: 0
            clip: true
            highlightRangeMode: ListView.StrictlyEnforceRange
            snapMode: ListView.SnapToItem
            KeyNavigation.down: playlistButtonTangle

            delegate: Controls.ItemDelegate {
                id: delegateItemCardTwo
                width: parent.width
                height: Kirigami.Units.gridUnit * 5

                background: Rectangle {
                    Kirigami.Theme.colorSet: Kirigami.Theme.Button
                    color: Kirigami.Theme.backgroundColor
                    border.color: delegateItemCardTwo.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                    border.width: delegateItemCardTwo.activeFocus ? 2 : 0
                    layer.enabled: true
                    layer.effect: DropShadow {
                        horizontalOffset: 1
                        verticalOffset: 2
                    }
                }


                contentItem: Item {
                    width: parent.width
                    height: parent.height

                    RowLayout {
                        id: delegateItem
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.smallSpacing
                        spacing: Kirigami.Units.largeSpacing

                        Image {
                            id: videoImage
                            source: modelData.image
                            Layout.preferredHeight: parent.height
                            Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                            fillMode: Image.Stretch
                        }

                        ColumnLayout {
                            Layout.fillWidth: true

                            Controls.Label {
                                id: videoLabel
                                Layout.fillWidth: true
                                text: modelData.track
                                wrapMode: Text.WordWrap
                                color: Kirigami.Theme.textColor
                            }
                            Controls.Label {
                                id: artistLabel
                                Layout.fillWidth: true
                                text: modelData.album
                                opacity: 0.8
                                color: Kirigami.Theme.textColor
                            }
                        }

                        Controls.Label {
                            id: durationTime
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            color: Kirigami.Theme.textColor
                            opacity: 0.8
                            text: formatedDuration(modelData.duration)
                        }

                        Kirigami.Separator {
                            Layout.fillHeight: true
                            Layout.preferredWidth: 1
                        }

                        Image {
                            id: songSource
                            Layout.preferredHeight: Kirigami.Units.iconSizes.huge + Kirigami.Units.largeSpacing
                            Layout.preferredWidth: Kirigami.Units.iconSizes.huge + Kirigami.Units.largeSpacing
                            Layout.alignment: Qt.AlignHCenter
                            fillMode: Image.PreserveAspectFit
                            source: modelData.source
                        }
                    }
                }

                Keys.onReturnPressed: {
                    clicked()
                }

                onClicked: {
                    triggerGuiEvent("search.play",
                    {"playlistData": modelData})
                }
            }
        }
    }
}
