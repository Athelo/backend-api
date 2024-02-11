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

  if (selectedFile == null) {
    window.alert("Please select a file")
    return
  }

  reader.readAsDataURL(selectedFile)

}




