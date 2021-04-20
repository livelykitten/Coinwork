import QtQuick 2.0
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.11

Dialog {
    id: alarmDialog
    title: "Add an alarm"
    standardButtons: Dialog.Ok | Dialog.Cancel
    modal: true

    property AlarmModel alarmModel

    contentItem: ColumnLayout {
        RowLayout {
            Label { text: "Enter d_ratio: " }
            TextField {
                id: d_ratio_input
                text: "15"
                validator: DoubleValidator {}
            }
            Label { text: "%" }
        }
        RowLayout{
            Label { text: "Enter d_time: ";Layout.fillWidth: true }
            TextField {
                id: d_time_min_input
//                Layout.fillWidth: true
                text: "15"
                validator: IntValidator {bottom: 0}
            }
            Label { text: "min";Layout.fillWidth: true }
            TextField {
                id: d_time_sec_input

                text: "30"
                validator: DoubleValidator {bottom: 0}
            }
            Label { text: "sec";Layout.fillWidth: true }
        }
        RowLayout {
            Layout.fillWidth: true
            Label { text: "Enter cooldown: " }
            TextField {
                id: cooldown_input
                text: "15"
                validator: IntValidator {bottom: 0}
            }
            Label { text: "min" }
        }

    }

    onAccepted: {
        try {
            const d_ratio = parseFloat(d_ratio_input.text) / 100
            const d_time = parseInt(d_time_min_input.text) * 60 + parseFloat(d_time_sec_input.text)
            const cooldown = parseInt(cooldown_input.text) * 60
            if (d_ratio === 0 || d_time <= 0 || cooldown <= 0) {
                throw 1
            }
        }
        catch (ev){
            return
        }
        finally {

            const cid = monitor.add_criteria(d_ratio, d_time, cooldown)

            alarmModel.append({
                                  "alarm_id": cid,
                                  "alarm_d_ratio": d_ratio,
                                  "alarm_d_time": d_time,
                                  "alarm_cooldown": cooldown
                              })
        }


    }

    onRejected: {
        alarmDialog.close()
    }

}
