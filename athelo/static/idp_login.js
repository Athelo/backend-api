firebase.initializeApp(config);
function initApp() {
  firebase.auth().onAuthStateChanged(user => {
    if (user) {
      document.getElementById("message").innerHTML = "Welcome, " + user.email;
      document.getElementById('signInButton').innerText = 'Sign Out';
      document.getElementById('getTokenButton').disabled=false; 
      document.getElementById('tokenDisplay').innerText = ''
  }
  else {
      document.getElementById("message").innerHTML = "No user signed in.";
      document.getElementById('signInButton').innerText = 'Sign In with Google';
      document.getElementById('getTokenButton').disabled=true;
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
    .then(result => {})
    .catch(err => {
      console.log(`Error during sign out: ${err.message}`);
      window.alert(`Sign out failed. Retry or check your browser logs.`);
    });
}

// Toggle Sign in/out button
function toggle() {
  console.log('toggle triggered')
  if (!firebase.auth().currentUser) {
    signIn();
  } else {
    signOut();
  }
}

async function getPublicEndpoint() {
  console.log('sending get to /public')
  try {
      const response = await fetch('/public', {
        method: 'GET',
      });
      if (response.ok) {
        const text = await response.text();
        document.getElementById('publicEndpointMessage').innerText = text
      }
    } catch (err) {
      document.getElementById('publicEndpointMessage').innerText= `Error when submitting vote: ${err}`
      window.alert('Something went wrong... Please try again!');
    }
} 

async function getProtectedEndpoint() {
  console.log('sending get to /protected')
  console.log('sending get to /public')
  try {
      const response = await fetch('/protected', {
        method: 'GET',
        headers: {
          Authorization: 'Bearer ${token}',
        },
      });
      if (response.ok) {
        const text = await response.text();
        document.getElementById('protectedEndpointMessage').innerText = text
      }
    } catch (err) {
      document.getElementById('protectedEndpointMessage').innerText= `Error when submitting vote: ${err}`
      window.alert('Something went wrong... Please try again!');
    }
}