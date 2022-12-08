/*
 * Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
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

import QtQuick 2.2
import QtQuick.Layouts 1.2
import org.kde.plasma.components 2.0 as PlasmaComponents
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.networkmanagement 0.2 as PlasmaNM
import org.kde.kirigami 2.5 as Kirigami
import Mycroft 1.0 as Mycroft

Kirigami.AbstractListItem {
    id: connectionSettingItem

    contentItem: Item {

        Kirigami.Icon {
            id: settingSvgIcon
            anchors.centerIn: parent            
            height: units.iconSizes.medium
            width: units.iconSizes.medium
            color: Kirigami.Theme.textColor
            source: "settings-configure"
        }
    }

    onClicked: {
        var connection_details
        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("../sounds/ui_sounds_clicked.wav"))
        
        if(model.ConnectionState == PlasmaNM.Enums.Activated) {
            var details = model.ConnectionDetails
            var details_list = details.toString().split(",")
            var connection_speed_index = details_list.indexOf("Connection speed") + 1
            var connection_speed = details_list[connection_speed_index]

            connection_details = {
                "networkName": model.ItemUniqueName,
                "networkSecurity": model.SecurityTypeString,
                "networkStrength": model.Signal,
                "networkSpeed": connection_speed,
            }
            Mycroft.MycroftController.sendRequest("ovos.phal.gui.display.connected.network.settings", {"connection_details": connection_details})
        } else if(model.ConnectionState == PlasmaNM.Enums.Deactivated) {
            connection_details = {
                "networkName": model.ItemUniqueName,
                "networkSecurity": model.SecurityTypeString,
                "networkStrength": model.Signal,
                "networkSpeed": ""
            }
            Mycroft.MycroftController.sendRequest("ovos.phal.gui.display.disconnected.network.settings", {"connection_details": connection_details}) 
        }
    }
}