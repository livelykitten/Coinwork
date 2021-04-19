import QtQuick 2.0
import QtQml.Models 2.15

ListModel {
    id: msgModel

    function add_item_sorted(new_item) {
        for (var i = 0; i < this.count; i++) {
            if (new_item.msg_timestamp >= this.get(i).msg_timestamp) {
                this.insert(i, new_item)
                return
            }
        }
        this.append(new_item)
    }

    ListElement {
        msg_timestamp: 1618730000
        msg_market: qsTr("")
        msg_text: qsTr("Welcome!!!")
    }

}
