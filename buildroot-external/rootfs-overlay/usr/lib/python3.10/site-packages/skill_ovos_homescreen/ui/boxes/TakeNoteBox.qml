import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import "../delegates" as Delegates

Delegates.BoxSimpleDelegate {
    boxIcon: "document-edit-sign"
    iconColor: "#5d58c9"
    text: "Dictate a quick note"
    action: "take a note"
}
