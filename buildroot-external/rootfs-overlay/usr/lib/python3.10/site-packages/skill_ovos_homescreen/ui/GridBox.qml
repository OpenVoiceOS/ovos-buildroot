import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQml.Models 2.12
import QtQuick.Window 2.12
import Mycroft 1.0 as Mycroft
import org.kde.kirigami 2.11 as Kirigami
import "code/dashmodel.js" as DashboardJS

Item {
    id: gridBoxRoot
    width: parent.width
    height: parent.height
    property var dashModel: sessionData.dashboard_model ? sessionData.dashboard_model : null
    property bool horizontalMode: width >= height ? 1 : 0

    onDashModelChanged: {
        DashboardJS.dashboard_spacing = 4
        DashboardJS.available_height.setActualHeight(flickableItem.height)
        DashboardJS.available_width.setActualWidth(flickableItem.width - (gridBoxRoot.horizontalMode ? Mycroft.Units.gridUnit * 4 : 0))

        if(dashModel) {
            DashboardJS.add_items_from_session(dashModel.collection)
            repeaterModel.model = DashboardJS.dashboard_model
        }
    }

    Kirigami.OverlaySheet {
        id: cardHoldOverlay
        parent: gridBoxRoot
        showCloseButton: false
        property var cardId
        title: qsTr("Edit Card")

        onSheetOpenChanged: {
            if (!sheetOpen) {
                cardId = ""
            }
        }

        contentItem: Item {
            implicitWidth: Mycroft.Units.gridUnit * 5
            implicitHeight: Mycroft.Units.gridUnit * 5

            RowLayout {
                anchors.fill: parent

                Button {
                    id: cardHoldRemoveButton
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: qsTr("Remove")

                    background: Rectangle {
                        color: cardHoldRemoveButton.pressed ? Kirigami.Theme.backgroundColor : Kirigami.Theme.highlightColor
                        radius: 6
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        triggerGuiEvent("ovos.homescreen.dashboard.remove.card", {"card_id": cardHoldOverlay.cardId})
                        DashboardJS.remove_item_by_id(cardHoldOverlay.cardId)
                        cardHoldOverlay.close()
                    }
                }
                Button {
                    id: cardHoldCloseButton
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    text: qsTr("Cancel")

                    background: Rectangle {
                        color: cardHoldCloseButton.pressed ? Kirigami.Theme.backgroundColor : Kirigami.Theme.highlightColor
                        radius: 6
                    }

                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                        cardHoldOverlay.close()
                    }
                }
            }
        }
    }

    Item {
        anchors.fill: parent
        anchors.rightMargin: gridBoxRoot.horizontalMode ? -Mycroft.Units.gridUnit * 2 : 0

        Flickable {
            id: flickableItem
            anchors.fill: parent
            anchors.rightMargin: gridBoxRoot.horizontalMode ? Mycroft.Units.gridUnit * 2 : 0
            clip: true
            contentWidth: gridBoxRoot.horizontalMode ? flow.implicitWidth : flow.width
            contentHeight: gridBoxRoot.horizontalMode ? flow.height : flow.implicitHeight

            onHeightChanged: {
                DashboardJS.available_height.setActualHeight(flickableItem.height)
                repeaterModel.update()
            }

            onWidthChanged: {
                DashboardJS.available_width.setActualWidth(flickableItem.width - (gridBoxRoot.horizontalMode ? Mycroft.Units.gridUnit * 4 : 0))
                repeaterModel.update()
            }

            Flow {
                id: flow
                width: flickableItem.width
                height: flickableItem.height
                spacing: 4
                flow: gridBoxRoot.horizontalMode ? Flow.TopToBottom : Flow.LeftToRight

                Repeater {
                    id: repeaterModel

                    delegate: MouseArea {
                        id: delegateRoot
                        width: gridBoxRoot.horizontalMode ? modelData.width : modelData.width * 2
                        height: modelData.height

                        property alias contentItem: contentLoader.item
                        property bool held: false
                        property int visualIndex: DelegateModel.itemsIndex
                        drag.target: held ? delegateContentItem : undefined

                        SequentialAnimation {
                            id: delegateClickAnimation
                            NumberAnimation {
                                target: delegateContentItem
                                property: "opacity"
                                from: 1
                                to: 0.5
                                duration: 150
                            }
                            NumberAnimation {
                                target: delegateContentItem
                                property: "opacity"
                                from: 0.5
                                to: 1
                                duration: 150
                            }
                        }

                        onDoubleClicked: {
                            delegateClickAnimation.start()
                            Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                            Mycroft.MycroftController.sendText(contentItem.action)
                        }

                        onPressAndHold: {
                            held = true
                            cardHoldOverlay.cardId = modelData.id
                            cardHoldOverlay.open()
                            delegateContentItem.opacity = 0.5
                        }

                        onReleased: {
                            if (held === true) {
                                held = false
                                delegateContentItem.opacity = 1
                                delegateContentItem.Drag.drop()
                            } else {
                                //action on release
                            }
                        }

                        Item {
                            id: delegateContentItem
                            anchors.fill: parent
                            anchors.margins: flow.spacing
                            Drag.active: delegateRoot.drag.active
                            Drag.source: delegateRoot
                            Drag.hotSpot.x: 36
                            Drag.hotSpot.y: 36

                            states: [
                                State {
                                    when: delegateContentItem.Drag.active

                                    ParentChange {
                                        target: delegateContentItem
                                        parent: flow
                                    }

                                    PropertyChanges {
                                        target: delegateContentItem
                                        anchors.fill: undefined
                                    }
                                }
                            ]

                            Loader {
                                id: contentLoader
                                anchors.fill: parent
                                anchors.margins: 16
                                source: modelData.url
                            }
                        }
                    }
                }
            }
        }
    }
}
