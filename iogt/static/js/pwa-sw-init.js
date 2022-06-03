const installPWA = async () => {
    if ('serviceWorker' in navigator && confirm(consentMsg) === true) {
        try {
            await navigator.serviceWorker.register(PWA_SW_URL, {scope: '/'});
            alert(successMsg)
        } catch {
            alert(failMsg);
        }
    }
}
