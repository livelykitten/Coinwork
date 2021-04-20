import QtQuick 2.0
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.11

Dialog {
    id: msgDialog
    title: "Alert!"
    standardButtons: Dialog.Ok
    width: 500
    modal: false

    property string recent_msg: '{"msg_market": "","msg_timestamp": 0,"msg_text": ""}'

    property int new_msg_num: 0

    contentItem: ColumnLayout {
        Label {
            text: JSON.parse(recent_msg).msg_market
        }
        Label {
            text: (new Date(JSON.parse(recent_msg).msg_timestamp * 1000)).toLocaleString()
        }
        Label {
            text: JSON.parse(recent_msg).msg_text
            Layout.fillWidth: true
        }
        Label {
            text: " At least " + new_msg_num.toString() + " messages arrived.\nCheck message box!"
            Layout.fillWidth: true
        }
    }

}
