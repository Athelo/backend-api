function initApp() {
    firebase.initializeApp(config);
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            // User is signed in, see docs for a list of available properties
            // https://firebase.google.com/docs/reference/js/v8/firebase.User
            var uid = user.uid;
            curr_user = user
            document.getElementById('authButton').innerText = 'Sign Out';
            await getToken()
            // ...
        } else {
            window.location = "login"
            document.getElementById('authButton').innerText = 'Sign In';
        }
    });

}
window.onload = function () {
    initApp();
};



async function getPublicEndpoint() {
    await performGetAndUpdateElements('publicEndpointMessage', '/public/')
}

async function getProtectedEndpoint() {
    await performGetAndUpdateElements('protectedEndpointMessage', '/protected/')
}

async function performGetAndUpdateElements(element, endpoint) {
    document.getElementById(element).innerText = ''
    let req_headers = {}
    if (google_token !== null) {
        req_headers = {
            'Authorization': `Bearer ${google_token}`,
        }
    }
    try {
        await fetch(endpoint, {
            credentials: 'include',
            method: 'GET',
            headers: req_headers,
        }).then(async (response) => {
            if (response.ok) {
                let text = await response.text();
                document.getElementById(element).innerText = text
            } else {
                let text = await response.text();
                document.getElementById(element).innerText = `${response.status}: ${response.statusText}\n${text}`
            }
        });

    } catch (err) {
        document.getElementById(element).innerText = `Error when submitting vote: ${err}`
        window.alert(`Something went wrong... Please try again!\n${err}`);
    }
}

async function copyToken() {
    tokenVal = document.getElementById('tokenDisplay').value
    navigator.clipboard.writeText(tokenVal).then(function (x) {
        window.alert(`Copied ${tokenVal} to clipboard`)
    });
}
