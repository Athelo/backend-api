let google_token = null

function signIn() {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('https://www.googleapis.com/auth/userinfo.email');
    firebase
        .auth()
        .signInWithPopup(provider)
        .then(result => {
            // Returns the signed in user along with the provider's credential
            console.log(`${result.user.displayName} logged in.`);
        })
        .catch(err => {
            console.log(`Error during Google sign in: ${err.message}`);
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

function passwordSignIn() {
    console.log("sign in")
    email = document.getElementById('inputEmail').value
    password = document.getElementById('inputPassword').value
    console.log(email)
    console.log(password)
    console.log(firebase)

    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((result) => {
            console.log(`${result.user.displayName} logged in.`);
            window.alert(`Welcome ${result.user.displayName}!`);
        })
        .catch((error) => {
            console.log(`Error during email/password sign in: ${error.message}`);
            console.error(error)
            window.alert(`Sign in failed. Retry or check your browser logs.`);
        });

}
async function setSessionData() {
    let req_headers = {}
    if (google_token !== null) {
        req_headers = {
            'Authorization': `Bearer ${google_token}`,
        }
    }
    try {
        await fetch("/login", {
            credentials: 'include',
            method: 'POST',
            headers: req_headers,
        }).then(async (response) => {
            if (!response.ok) {
                let text = await response.text();
                window.alert(`${response.status}: ${response.statusText}\n${text}`)
            }
        });

    } catch (err) {
        window.alert(`Something went wrong... Please try again!\n${err}`);
    }
}

async function clearSessionData() {
    let req_headers = {}
    if (google_token !== null) {
        req_headers = {
            'Authorization': `Bearer ${google_token}`,
        }
    }
    try {
        await fetch("/logout", {
            credentials: 'include',
            method: 'POST',
            headers: req_headers,
        }).then(async (response) => {
            if (!response.ok) {
                let text = await response.text();
                window.alert(`${response.status}: ${response.statusText}\n${text}`)
            }
        });

    } catch (err) {
        window.alert(`Something went wrong... Please try again!\n${err}`);
    }
}


