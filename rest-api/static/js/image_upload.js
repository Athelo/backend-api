function initApp() {
  firebase.auth().onAuthStateChanged((user) => {
    if (user) {
      // User is signed in, see docs for a list of available properties
      // https://firebase.google.com/docs/reference/js/v8/firebase.User
      var uid = user.uid;

      // ...
    } else {
      // User is signed out
      // ...
    }
  });

}
window.onload = function () {
  initApp();
};

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



