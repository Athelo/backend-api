let google_token = null
function initApp() {
    firebase.initializeApp(config);
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            document.getElementById("message").innerHTML = "Welcome, " + user.email;
            document.getElementById('googleSignInButton').innerText = 'Sign Out';
            document.getElementById('passwordAuthContainer').hidden = true
            document.getElementById('authButton').innerText = 'Sign Out';
            await getToken()
            setSessionData()
        }
        else {
            document.getElementById("message").innerHTML = "";
            document.getElementById('googleSignInButton').innerText = 'Sign In with Google';
            document.getElementById('passwordAuthContainer').hidden = false
            document.getElementById('authButton').innerText = 'Sign In';
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

function passwordSignIn() {
    console.log("sign in")
    email = document.getElementById('inputEmail').value
    password = document.getElementById('inputPassword').value
    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((result) => {
            console.log(`${result.user.displayName} logged in.`);
            window.alert(`Welcome ${result.user.displayName}!`);
            window.location = "/dev"
        })
        .catch((error) => {
            console.log(`Error during sign in: ${err.message}`);
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


async function getToken() {
    google_token = await firebase.auth().currentUser.getIdToken().catch((error) => {
        document.getElementById('tokenDisplay').textContent = error.message
    })
}

