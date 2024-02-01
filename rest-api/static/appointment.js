firebase.initializeApp(config);
let google_token = null;
let curr_user = null;
function initApp() {
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            document.getElementById("message").innerHTML = "Welcome, " + user.email;
            document.getElementById('signInButton').innerText = 'Sign Out';
            curr_user = user
            await getToken()
        }
        else {
            document.getElementById("message").innerHTML = "No user signed in.";
            document.getElementById('signInButton').innerText = 'Sign In with Google';
            google_token = ''
            curr_user = null
        }
    });
}
window.onload = function () {
    initApp();
};

function signIn() {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('https://www.googleapis.com/auth/userinfo.email');
    firebase
        .auth()
        .signInWithPopup(provider)
        .then(result => {
            // Returns the signed in user along with the provider's credential
            console.log(`${result.user.displayName} logged in.`);
            window.alert(`Welcome ${result.user.displayName}!`);
        })
        .catch(err => {
            console.log(`Error during sign in: ${err.message}`);
            window.alert(`Sign in failed. Retry or check your browser logs.`);
        });
}

function signOut() {
    firebase
        .auth()
        .signOut()
        .catch(err => {
            console.log(`Error during sign out: ${err.message}`);
            window.alert(`Sign out failed. Retry or check your browser logs.`);
        });
}

// Toggle Sign in/out button
function toggle() {
    if (!firebase.auth().currentUser) {
        signIn();
    } else {
        signOut();
    }
}

async function getToken() {
    if (curr_user == null) {
        window.alert("Please sign in to get a token.")
    }
    google_token = await firebase.auth().currentUser.getIdToken().catch((error) => {
        window.alert = error.message
    })
}
// Attach event handlers



async function createTokenForSession() {
    if (!google_token) {
        window.alert('Must sign in to connect')
        return
    }
    sessionId = document.getElementById("sessionInput").value
    if (!sessionId) {
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
        await fetch("/api/v1/appointment/18/vonage-appointment-details", {
            credentials: 'include',
            method: 'GET',
            headers: req_headers,
        }).then(async (response) => {
            if (response.ok) {
                let json = await response.json();
                document.getElementById("otTokenDisplay").innerText = json["token"]
                ot_token = json["token"]
            } else {
                let text = await response.text();
                document.getElementById("oTtokenDisplay").innerText = `${response.status}: ${response.statusText}\n${text}`
            }
        });

    } catch (err) {
        window.alert('Something went wrong... Please try again!');
        return
    }

    // Initialize an OpenTok Session object
    var session = OT.initSession(apiKey, sessionId);

    // Initialize a Publisher, and place it into the element with id="publisher"
    var publisher = OT.initPublisher('publisher');

    session.on({

        // This function runs when session.connect() asynchronously completes
        sessionConnected: function (event) {
            // Publish the publisher we initialzed earlier (this will trigger 'streamCreated' on other
            // clients)
            session.publish(publisher, function (error) {
                if (error) {
                    console.error('Failed to publish', error);
                }
            });
        },

        // This function runs when another client publishes a stream (eg. session.publish())
        streamCreated: function (event) {
            // Create a container for a new Subscriber, assign it an id using the streamId, put it inside
            // the element with id="subscribers"
            var subContainer = document.createElement('div');
            subContainer.id = 'stream-' + event.stream.streamId;
            document.getElementById('videoPanel').appendChild(subContainer);

            // Subscribe to the stream that caused this event, put it inside the container we just made
            session.subscribe(event.stream, subContainer, function (error) {
                if (error) {
                    console.error('Failed to subscribe', error);
                }
            });
        }

    });

    // Connect to the Session using the 'apiKey' of the application and a 'token' for permission
    session.connect(ot_token, function (error) {
        if (error) {
            console.error('Failed to connect', error);
        }
    });
}
