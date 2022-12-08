import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Control {
    id: boxDelegateRootItem
    z: 1

    property var action: ""
    property int preferredCellWidth: 4
    property int preferredCellHeight: 4

    background: Rectangle {
        color: Kirigami.Theme.backgroundColor
        border.color: Kirigami.Theme.highlightColor
        border.width: 1
        radius: 15
        layer.enabled: true
        layer.effect: DropShadow {
            transparentBorder: false
            horizontalOffset: 3
            verticalOffset: 3
            color: Qt.rgba(0, 0, 0, 0.50)
            spread: 0.2
            samples: 8
        }
    }

    contentItem: Item {
        z: 2
    }
}
