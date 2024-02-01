firebase.initializeApp(config);
let token = null;
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
      document.getElementById('tokenDisplay').innerText = ''
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
    document.getElementById('tokenDisplay').textContent = error.message
  })
  if (google_token) {
    document.getElementById('tokenDisplay').textContent = `${google_token}`
  } else {
    document.getElementById('tokenDisplay').textContent = 'Unable to get token'
  }

}

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
    window.alert('Something went wrong... Please try again!');
  }
}