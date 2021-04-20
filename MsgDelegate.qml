import QtQuick 2.0
import QtQuick.Controls 2.15

import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.4
import QtQuick.Layouts 1.11
import QtQuick.Window 2.11

ItemDelegate {
    id: root
    width: ListView.view.width
    anchors.leftMargin: 100
    anchors.rightMargin: 100
    highlighted: model.user_checked === false
    contentItem: ColumnLayout {
        RowLayout {
            width: parent.width
            Label {
                text: (new Date(model.msg_timestamp * 1000)).toLocaleString()
            }
            Item { Layout.fillWidth: true }
            Label {
                id: is_read
                text: if (model.user_checked === false) {"안읽음"} else {"읽음"}
            }
        }
        Label {
            text: model.msg_market
        }
        Label {
            text: model.msg_text
            Layout.fillWidth: true
            wrapMode: Label.WordWrap
        }
    }
    onClicked: {
        highlighted = false
        is_read.text = "읽음"
    }
}
