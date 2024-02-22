
let google_token = null;
let appointments = null;
let selected_session = null
let selected_appt_id = null
let active_session = null

async function getAppointments() {
    appointments = {}
    appointmentSelection = document.getElementById("appointmentList")
    let req_headers = {}
    if (google_token !== null) {
        req_headers = {
            'Authorization': `Bearer ${google_token}`,
        }
    }
    try {
        await fetch("/api/v1/appointments/", {
            credentials: 'include',
            method: 'GET',
            headers: req_headers,
        }).then(async (response) => {
            if (response.ok) {
                let json = await response.json();
                items = json["results"]
                for (let i = 0; i < items.length; i++) {
                    appointmentSelection.options[i + 1] = new Option(items[i]["id"] + ": " + items[i]["start_time"], items[i]["id"])
                    appointments[items[i]["id"]] = items[i]
                }
            } else {
                message = await response.text()
                if (response.status == 404) {
                    window.alert(`Got result NOT_FOUND when fetching appointments. Is this user properly set up? (${message})`);
                } else {
                    window.alert('Something went wrong... Please try again!');
                }
                console.log(`Error fetching appointments: ${message}`)

            }
        });

    } catch (err) {
        window.alert('Something went wrong... Please try again!');
        return
    }
}


function updateAppointmentDisplay() {
    appointmentSelect = document.getElementById('appointmentList')
    appointmentDisplay = document.getElementById('appointmentDisplay')
    connectButton = document.getElementById('connectButton').disabled = false

    appointmentDisplay.textContent = createAppointmentDisplayString(appointments[appointmentSelect.value])
    selected_session = appointments[appointmentSelect.value]["vonage_session"]
    selected_appt_id = appointmentSelect.value

}

function createAppointmentDisplayString(appt) {
    let display = " "
    display += ("ID: " + appt["id"] + "\r\n")
    display += ("Start time: " + appt["start_time"] + "\r\n")
    display += ("End time: " + appt["end_time"] + "\r\n")
    display += ("Patient: " + appt["patient"]["display_name"] + "\r\n")
    display += ("Provider: " + appt["provider"]["display_name"] + "\r\n")
    return display
}


function handleError(error) {
    if (error) {
        alert(error.message);
    }
}


async function joinOpentokSession() {
    if (!google_token) {
        window.alert('Must sign in to connect')
        return
    }
    if (!selected_session) {
        window.alert("Must provide session id")
        return
    }
    let req_headers = {}
    if (google_token !== null) {
        req_headers = {
            'Authorization': `Bearer ${google_token}`,
        }
    }

    let ot_token = ""
    try {
        await fetch("/api/v1/appointment/" + selected_appt_id + "/vonage-appointment-details", {
            credentials: 'include',
            method: 'GET',
            headers: req_headers,
        }).then(async (response) => {
            if (response.ok) {
                let json = await response.json();
                ot_token = json["token"]
            } else {
                let text = await response.text();
                window.alert(`${response.status}: ${response.statusText}\n${text}`)
            }
        });

    } catch (err) {
        window.alert('Something went wrong... Please try again!');
        return
    }

    document.getElementById("connectButton").disabled = true;
    document.getElementById("disconnectButton").disabled = false;
    document.getElementById("videos").hidden = false;

    // Initialize an OpenTok Session object
    var session = OT.initSession(apiKey, selected_session);
    active_session = session

    // Subscribe to a newly created stream
    session.on('streamCreated', (event) => {
        const subscriberOptions = {
            insertMode: 'append',
            width: '480',
            height: '360'
            //style: { nameDisplayMode: "auto" }
        };
        session.subscribe(event.stream, 'subscriber', subscriberOptions, handleError);
    });

    session.on('sessionDisconnected', (event) => {
        console.log('You were disconnected from the session.', event.reason);
    });

    // initialize the publisher
    const publisherOptions = {
        insertMode: 'append',
        width: '480',
        height: '360',
        // name: "Test",
        // style: { nameDisplayMode: "auto" }
    };
    const publisher = OT.initPublisher('publisher', publisherOptions, handleError);
    // const publisher = OT.initPublisher('publisher', {
    //     name: "Test",
    //     style: { nameDisplayMode: "auto" }
    // }, handleError);

    // Connect to the session
    session.connect(ot_token, (error) => {
        if (error) {
            handleError(error);
        } else {
            // If the connection is successful, publish the publisher to the session
            session.publish(publisher, handleError);
        }
    });


}

async function leaveOpentokSession() {
    if (active_session) {
        active_session.disconnect();
        document.getElementById("disconnectButton").disabled = true;
        document.getElementById("connectButton").disabled = false;
        document.getElementById("videos").hidden = true;

        active_session = null;
    }

}
