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
    contentItem: ColumnLayout {

        RowLayout {
            Label {
                text: (new Date(model.msg_timestamp * 1000)).toLocaleString()
            }
            Label {
                text: model.msg_market
            }
        }
        Label {
            text: model.msg_text
        }
    }
}