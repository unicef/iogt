// idb.js - IndexedDB Helper
const DB_NAME = "offline-forms";
const STORE_NAME = "requests";

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);

        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
            }
        };

        request.onsuccess = event => {
            resolve(event.target.result);
        };

        request.onerror = event => {
            console.error("❌ IndexedDB Error:", event.target.error);
            reject(event.target.error);
        };
    });
}

// ✅ Properly save request with correct body handling
async function saveRequest(request) {
    const db = await openDB();
    const clonedRequest = request.clone();

    // ✅ Get headers as object
    const headersObj = {};
    for (let [key, value] of clonedRequest.headers.entries()) {
        headersObj[key] = value;
    }

    let body = null;
    const contentType = clonedRequest.headers.get("Content-Type") || "";

    try {
        if (contentType.includes("application/json")) {
            body = await clonedRequest.json();
        } else if (contentType.includes("application/x-www-form-urlencoded")) {
            body = await clonedRequest.text(); // Store raw URL-encoded body
        } else if (contentType.includes("multipart/form-data")) {
            // Optionally warn or skip: FormData can't be serialized directly
            console.warn("❗ Cannot store multipart/form-data offline safely");
        } else {
            body = await clonedRequest.text();
        }
    } catch (err) {
        console.error("❌ Failed to parse body:", err);
    }

    const requestData = {
        url: clonedRequest.url,
        method: clonedRequest.method,
        body: body,
        headers: headersObj,
        credentials: 'include', // ✅ Important for replaying with cookies
        timestamp: new Date().toISOString(), // optional
    };

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        const store = tx.objectStore(STORE_NAME);
        const addRequest = store.add(requestData);

        addRequest.onsuccess = () => {
            resolve();
        };

        addRequest.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

// ✅ Retrieve all stored requests
async function getAllRequests() {

    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readonly");
        const store = tx.objectStore(STORE_NAME);
        const req = store.getAll();

        req.onsuccess = () => {
            resolve(req.result);
        };

        req.onerror = () => {
            reject(req.error);
        };
    });
}

// ✅ Delete request after successful sync
async function deleteRequest(id) {
    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        const store = tx.objectStore(STORE_NAME);
        const req = store.delete(id);

        req.onsuccess = () => {
            resolve();
        };

        req.onerror = (event) => {
            reject(event.target.error);
        };
    });
}
