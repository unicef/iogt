// idb.js - IndexedDB Helper
const DB_NAME = "offline-forms";
const STORE_NAME = "requests";

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);

        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                console.log("🔧 Creating object store:", STORE_NAME);
                db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
            }
        };

        request.onsuccess = event => {
            console.log("✅ IndexedDB Opened Successfully");
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
    console.log("💾 Saving request to IndexedDB:", request.url);

    const db = await openDB();

    // ✅ Extract body properly
    let body;
    try {
        body = await request.clone().json();
    } catch {
        body = await request.clone().text();
    }

    const headersObj = {};
    for (let [key, value] of request.headers.entries()) {
        headersObj[key] = value;
    }

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        const store = tx.objectStore(STORE_NAME);

        const requestData = {
            url: request.url,
            method: request.method,
            body: body,
            headers: headersObj,
        };

        const addRequest = store.add(requestData);

        addRequest.onsuccess = () => {
            console.log("✅ Request successfully stored in IndexedDB!");
            resolve();
        };

        addRequest.onerror = (event) => {
            console.error("❌ Error storing request:", event.target.error);
            reject(event.target.error);
        };

        tx.oncomplete = () => console.log("✅ Transaction completed successfully!");
        tx.onerror = (event) => console.error("❌ Transaction failed:", event.target.error);
    });
}

// ✅ Retrieve all stored requests
async function getAllRequests() {
    console.log("📂 Retrieving all stored requests...");

    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readonly");
        const store = tx.objectStore(STORE_NAME);
        const req = store.getAll();

        req.onsuccess = () => {
            console.log("📦 Stored Requests:", req.result);
            resolve(req.result);
        };

        req.onerror = () => {
            console.error("❌ Error retrieving requests:", req.error);
            reject(req.error);
        };
    });
}

// ✅ Delete request after successful sync
async function deleteRequest(id) {
    console.log("🗑️ Deleting request with ID:", id);

    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        const store = tx.objectStore(STORE_NAME);
        const req = store.delete(id);

        req.onsuccess = () => {
            console.log("✅ Successfully deleted request from IndexedDB!");
            resolve();
        };

        req.onerror = (event) => {
            console.error("❌ Error deleting request:", event.target.error);
            reject(event.target.error);
        };
    });
}
