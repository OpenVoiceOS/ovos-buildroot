import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import "../delegates" as Delegates

Delegates.BoxSimpleDelegate {
    boxIcon: "send_signal"
    iconColor: "#0be5b6"
    text: "Get the latest news and headlines"
    action: "play the latest news"
}
