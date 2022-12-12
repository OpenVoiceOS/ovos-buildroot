import QtQuick 2.9
import QtQuick.Layouts 1.4
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.3
import org.kde.kirigami 2.8 as Kirigami
import Mycroft 1.0 as Mycroft

ItemDelegate {
    id: delegate
    
    readonly property bool isCurrent: {
        skillsListView.currentIndex == index && activeFocus && !skillsListView
        .moving
    }

    property int borderSize: Kirigami.Units.smallSpacing
    property int baseRadius: 4

    z: isCurrent ? 2 : 0
    
    leftPadding: Mycroft.Units.largeSpacing
    topPadding: Mycroft.Units.largeSpacing
    rightPadding: Mycroft.Units.largeSpacing
    bottomPadding: Mycroft.Units.largeSpacing

    leftInset: Mycroft.Units.largeSpacing
    topInset: Mycroft.Units.largeSpacing
    rightInset: Mycroft.Units.largeSpacing
    bottomInset: Mycroft.Units.largeSpacing
    
    implicitHeight: skillsListView.cellHeight
    
    background: Item {
        id: background
        
        Rectangle {
            id: frame
            anchors.fill: parent
            color: Kirigami.Theme.backgroundColor
            radius: delegate.baseRadius
            border.width: delegate.activeFocus ? 4 : 0
            border.color: delegate.activeFocus ? Kirigami.Theme.linkColor : "transparent"
            layer.enabled: true
            layer.effect: DropShadow {
                transparentBorder: false
                horizontalOffset: 2
                verticalOffset: 2
            }
        }
    }
    
    contentItem: ColumnLayout {
        spacing: Kirigami.Units.smallSpacing

        Item {
            id: imgRoot
            Layout.alignment: Qt.AlignTop
            Layout.fillWidth: true
            Layout.topMargin: -delegate.topPadding + delegate.topInset + extraBorder
            Layout.leftMargin: -delegate.leftPadding + delegate.leftInset + extraBorder
            Layout.rightMargin: -delegate.rightPadding + delegate.rightInset + extraBorder
            Layout.preferredHeight: width * 0.5625 + delegate.baseRadius
            property real extraBorder: 0

            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    x: imgRoot.x;
                    y: imgRoot.y
                    width: imgRoot.width
                    height: imgRoot.height
                    radius: delegate.baseRadius
                }
            }

            Image {
                id: img
                source: model.image ? model.image : "https://uroehr.de/vtube/view/img/skill-placeholder.png"
                anchors {
                    fill: parent
                    // To not round under
                    bottomMargin: delegate.baseRadius
                }
                opacity: 1
                fillMode: Image.PreserveAspectCrop
            }
            
            states: [
                State {
                    when: delegate.isCurrent
                    PropertyChanges {
                        target: imgRoot
                        extraBorder: delegate.borderSize
                    }
                },
                State {
                    when: !delegate.isCurrent
                    PropertyChanges {
                        target: imgRoot
                        extraBorder: 0
                    }
                }
            ]
            transitions: Transition {
                onRunningChanged: {
                    // Optimize when animating the thumbnail
                    img.smooth = !running
                }
                NumberAnimation {
                    property: "extraBorder"
                    duration: Kirigami.Units.longDuration
                    easing.type: Easing.InOutQuad
                }
            }
        }

        Kirigami.Heading {
            id: skillLabel
            Layout.fillWidth: true
            Layout.fillHeight: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.Wrap
            level: 3
            maximumLineCount: 2
            elide: Text.ElideRight
            color: Kirigami.Theme.textColor
            Component.onCompleted: {
                text = model.title
            }
        }
    }
    
    Keys.onReturnPressed: {
        clicked()
    }

    onClicked: {
        skillsListView.forceActiveFocus()
        skillsListView.currentIndex = index
        triggerGuiEvent("featured_tracks.play",
        {"title": model.title, "skill_id": model.skill_id})
    }
}
