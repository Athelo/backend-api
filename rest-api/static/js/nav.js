function authButtonClick() {
    console.log("auth button click")
    if (user) {
        firebase
            .auth()
            .signOut()
            .catch(err => {
                console.log(`Error during sign out: ${err.message}`);
                window.alert(`Sign out failed. Retry or check your browser logs.`);
            });

    }
    window.location = "/login"
}
