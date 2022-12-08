import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.4
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Button {
    id: controlButton
    Layout.preferredWidth: Mycroft.Units.gridUnit * 5
    Layout.fillHeight: true
    Layout.margins: Mycroft.Units.gridUnit * 0.1
    property alias buttonIcon: controlButtonContentIcon.source

    SequentialAnimation {
        id: controlButtonAnim

        PropertyAnimation {
            target: controlButtonBackground
            property: "color"
            Kirigami.Theme.colorSet: Kirigami.Theme.Button
            Kirigami.Theme.inherit: false
            to: Kirigami.Theme.highlightColor
            duration: 200
        }

        PropertyAnimation {
            target: controlButtonBackground
            property: "color"
            Kirigami.Theme.colorSet: Kirigami.Theme.Button
            Kirigami.Theme.inherit: false
            to: Kirigami.Theme.backgroundColor
            duration: 200
        }
    }

    onPressed: {
        controlButtonAnim.running = true;
    }

    contentItem: Item {
        Kirigami.Icon {
            id: controlButtonContentIcon
            width: Kirigami.Units.iconSizes.smallMedium
            height: width
            anchors.centerIn: parent

            ColorOverlay {
                source: parent
                anchors.fill: parent
                color: Kirigami.Theme.textColor
            }
        }
    }

    background: Rectangle {
        id: controlButtonBackground
        radius: 5
        Kirigami.Theme.colorSet: Kirigami.Theme.Button
        Kirigami.Theme.inherit: false
        color:  Kirigami.Theme.backgroundColor
        border.width: 1
        border.color: Kirigami.Theme.highlightColor
    }
}