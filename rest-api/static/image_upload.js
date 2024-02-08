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

async function uploadImageJson() {
  let req_headers = {}
  if (google_token !== null) {
    req_headers = {
      'Authorization': `Bearer ${google_token}`,
      'Content-Type': 'application/json'
    }
  }
  const selectedFile = document.getElementById("fileInput").files[0];
  let fileString = null
  const reader = new FileReader();
  reader.addEventListener("load", async () => {
    fileString = reader.result
    try {
      await fetch("/api/v1/common/image/json/", {
        credentials: 'include',
        method: 'POST',
        headers: req_headers,
        body: JSON.stringify({
          "name": selectedFile.name,
          "data": fileString,
          "file_type": selectedFile.type
        })
      }).then(async (response) => {
        if (response.ok) {
          let data = await response.json();
          window.alert("File uploaded to " + data["url"])
        } else {
          let text = await response.text();
          window.alert(`${response.status}: ${response.statusText}\n${text}`)
        }
      });

    } catch (err) {
      window.alert(`Something went wrong... Please try again!\n${err}`);
    }
  })

  reader.readAsDataURL(selectedFile)


}


async function getToken() {
  if (curr_user == null) {
    window.alert("Please sign in to get a token.")
  }
  google_token = await firebase.auth().currentUser.getIdToken().catch((error) => {
    window.alert(error.message)
  })
}



