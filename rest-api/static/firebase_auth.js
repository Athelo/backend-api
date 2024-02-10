firebase.initializeApp(config);

let token = null;
let curr_user = null;
function initApp() {
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            document.getElementById("message").innerHTML = "Welcome, " + user.email;
            document.getElementById('googleSignInButton').innerText = 'Sign Out';
            document.getElementById('passwordAuthContainer').hidden = true
            document.getElementById('nav-mobile').hidden = false
            curr_user = user
        }
        else {
            document.getElementById("message").innerHTML = "";
            document.getElementById('googleSignInButton').innerText = 'Sign In with Google';
            document.getElementById('passwordAuthContainer').hidden = false
            document.getElementById('nav-mobile').hidden = true

            google_token = ''
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
            window.location = "/dev"
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
    email = document.getElementById('email').value
    password = document.getElementById('pass').value
    firebase.auth().signInWithEmailAndPassword(email, password)
        .then((result) => {
            console.log(`${result.user.displayName} logged in.`);
            window.alert(`Welcome ${result.user.displayName}!`);
            window.location = "/dev"
        })
        .catch((err) => {
            console.log(`Error during sign in: ${err.message}`);
            window.alert(`Sign in failed. Retry or check your browser logs.`);
        });

}