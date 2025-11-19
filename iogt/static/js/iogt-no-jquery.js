const ready = (callback) => {
  if (document.readyState !== "loading") callback();
  else document.addEventListener("DOMContentLoaded", callback);
};

function showToast(message, type = "info") {
  const toast = document.getElementById("toast-notification");

  if (!toast) return;

  toast.textContent = message;

  // Set color
  switch (type) {
    case "success":
      toast.style.backgroundColor = "#4caf50";
      break;
    case "error":
      toast.style.backgroundColor = "#f44336";
      break;
    case "warning":
      toast.style.backgroundColor = "#ff9800";
      break;
    default:
      toast.style.backgroundColor = "#333";
  }

  toast.style.display = "block";
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";

  // Force reflow for iOS animation
  void toast.offsetHeight;

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-20px)";
  }, 3000);

  // Hide after transition
  setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

const init = () => {
  const show = (el) => (el.style.display = "");
  const hide = (el) => (el.style.display = "none");

  const externalLinkOverlay = document.querySelector("#external-link-overlay");
  externalLinkOverlay?.addEventListener("click", (event) => hide(event.target));

  const submitWhenOffline = gettext("You cannot submit when offline");

  const readContent = document.querySelectorAll(".complete");
  const commentLikeHolders = document.querySelectorAll(".like-holder");
  const replyLinks = document.querySelectorAll(".reply-link");
  const offlineAppBtns = document.querySelectorAll(".offline-app-btn");
  const chatbotBtns = document.querySelectorAll(".chatbot-btn");
  const questionnaireSubmitBtns = document.querySelectorAll(
    ".questionnaire-submit-btn"
  );

  // Save original button label
  questionnaireSubmitBtns.forEach((btn) => {
    const span = btn.querySelector("span");
    if (span && !span.dataset.originalLabel) {
      span.dataset.originalLabel = span.textContent.trim();
    }
  });

  const externalLinks = document.querySelectorAll(
    'a[href*="/external-link/?next="]'
  );
  const elementsToToggle = [
    ".download-app-btn",
    ".login-create-account-btn",
    ".change-digital-pin",
    ".comments__form",
    ".logout-btn",
    ".notification-pref-btn",
    ".progress-holder",
    ".report-comment",
    ".search-form-holder",
  ].flatMap((selector) => Array.from(document.querySelectorAll(selector)));

  const blockExternalLinks = (event) => {
    event.preventDefault();
    show(externalLinkOverlay);
  };

  const hideFooterMenu = () => {
    hide(document.querySelector(".footer-head"));
  };

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", (event) => {
      const data = event.data;
      if (!data) return;

      switch (data.type) {
        case "sync-success":
          showToast(`✅ Synced back offline filled form.`, "success");
          break;
        case "sync-failed":
          showToast(`⚠️ Offline form sync failed for: ${data.url}`, "error");
          break;
        case "sync-error":
          showToast(`❌ Sync error: ${data.error}`, "error");
          break;
      }
    });
  }

  const disableForOfflineAccess = () => {
    elementsToToggle.forEach(hide);
    replyLinks.forEach(hide);
    readContent.forEach((el) => el.classList.remove("complete"));
    commentLikeHolders.forEach((el) =>
      el.setAttribute("style", "display:none !important")
    );
    offlineAppBtns.forEach(show);
    chatbotBtns.forEach((btn) => {
      btn.style.pointerEvents = "none";
      btn.style.background = "#808080";
    });
    questionnaireSubmitBtns.forEach((btn) => {
      btn.style.pointerEvents = "all"; // ensure it's still clickable
      const span = btn.querySelector("span");
      if (span) {
        span.textContent =
          span.dataset.originalLabel || span.textContent.trim();
      }
    });
    externalLinks.forEach((link) =>
      link.addEventListener("click", blockExternalLinks)
    );
  };

  const enableForOnlineAccess = () => {
    elementsToToggle.forEach(show);
    readContent.forEach((el) => el.classList.add("complete"));
    commentLikeHolders.forEach((el) =>
      el.setAttribute("style", "display:inline-block !important")
    );
    replyLinks.forEach((el) =>
      el.setAttribute("style", "display:inline-block")
    );
    offlineAppBtns.forEach(hide);
    chatbotBtns.forEach((btn) => {
      btn.style.pointerEvents = "all";
      btn.style.background = "#F7F7F9";
    });
    questionnaireSubmitBtns.forEach((btn) => {
      btn.style.pointerEvents = "all";
      const span = btn.querySelector("span");
      if (span) {
        span.textContent =
          span.dataset.originalLabel || span.textContent.split("(")[0].trim();
      }
    });
    externalLinks.forEach((link) => {
      show(link);
      link.removeEventListener("click", blockExternalLinks);
    });
  };

  window.addEventListener("offline", () => {
    console.warn("🔌 Offline detected.");
    disableForOfflineAccess();
    if (getItem("offlineReady") === true) {
      setTimeout(() => location.reload(), 3000);
    }
  });

  window.addEventListener("online", enableForOnlineAccess);

  window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();

  hideFooterMenu();

  // Force re-check of online status
  fetch(window.location.href, { method: "HEAD", cache: "no-cache" })
    .then(() => {
      enableForOnlineAccess();
    })
    .catch(() => {
      console.warn("⚠️ Verified offline via HEAD request");
      disableForOfflineAccess();
    });
};

const download = (pageId) => {
  showToast("📥 Downloading…");

  fetch(`/page-tree/${pageId}/`)
    .then((resp) => {
      if (!resp.ok) {
        throw new Error(
          `Failed to fetch URLs for caching. Status: ${resp.status}`
        );
      }
      return resp.json();
    })
    .then((urls) => {
      if (!Array.isArray(urls) || urls.length === 0) {
        throw new Error("No URLs received for caching.");
      }

      return caches.open("iogt").then((cache) => {
        return Promise.all(
          urls.map((url) =>
            fetch(url, { method: "HEAD" })
              .then((response) => {
                if (response.ok) {
                  return cache.add(url).catch((error) => {
                    if (error.name === "QuotaExceededError") {
                      alert(
                        "⚠️ Your storage limit has been reached! Please free up space."
                      );
                      throw new Error(
                        "Storage full! Cannot cache more content."
                      );
                    }
                    throw error;
                  });
                } else {
                  console.warn(
                    `Skipping invalid URL: ${url} (Status: ${response.status})`
                  );
                }
              })
              .catch((err) =>
                console.warn(`Skipping ${url} due to error:`, err)
              )
          )
        );
      });
    })
    .then(() => {
      setItem("offlineReady", true); // ✅ Mark ready for offline
      showToast("✅ Content is now available offline!", "success");
      location.reload();
    })
    .catch((error) => {
      console.error("❌ Download error:", error);
      alert("⚠️ Download failed. Please try again.");
    });
};

function getItem(key, defaultValue = null) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? defaultValue;
  } catch {
    return defaultValue;
  }
}

const setItem = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

const registerPushNotification = (registration) => {
  if (!registration.showNotification) return;
  if (!"PushManager" in window) return;
  if (Notification.permission === "default") {
    Notification.requestPermission(function (permission) {
      if (permission === "granted") {
        subscribe(registration);
      }
    });
  } else if (Notification.permission === "granted") {
    subscribe(registration);
  }
};

const urlB64ToUint8Array = (base64String) => {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
};

const subscribe = (registration) => {
  registration.pushManager
    .getSubscription()
    .then((subscription) => {
      if (subscription) {
        sendSubscriptionToServer(subscription, "subscribe");
        return;
      }
      const vapidKey = document.querySelector(
        'meta[name="vapid-key"]'
      )?.content;
      const options = { userVisibleOnly: true };
      if (vapidKey) options.applicationServerKey = urlB64ToUint8Array(vapidKey);

      registration.pushManager
        .subscribe(options)
        .then((subscription) =>
          sendSubscriptionToServer(subscription, "subscribe")
        )
        .catch((error) => console.log("Error during subscribe()", error));
    })
    .catch((error) => console.log("Error during getSubscription()", error));
};

const sendSubscriptionToServer = (subscription, statusType) => {
  const browser = navigator.userAgent
    .match(/(firefox|msie|chrome|safari|trident)/gi)[0]
    .toLowerCase();
  const data = {
    status_type: statusType,
    subscription: subscription.toJSON(),
    browser: browser,
  };

  fetch("/webpush/subscribe/", {
    method: "POST",
    body: JSON.stringify(data),
    headers: { "content-type": "application/json" },
    credentials: "include",
  }).then(() => {
    setItem("isPushNotificationRegistered", statusType === "subscribe");
  });
};

const unSubscribePushNotifications = () => {
  const isPushNotificationRegistered = getItem(
    "isPushNotificationRegistered",
    false
  );
  if (
    isPushNotificationRegistered &&
    isAuthenticated &&
    "serviceWorker" in navigator
  ) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.pushManager.getSubscription().then((subscription) => {
        if (subscription) sendSubscriptionToServer(subscription, "unsubscribe");
      });
    });
  }
};

ready(init);

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("deleteModal");
  const confirmBtn = document.getElementById("confirmDelete");
  const cancelBtn = document.getElementById("cancelDelete");
  const deleteBtn = document.querySelector("#deleteAccountBtn a");
  deleteBtn.addEventListener("click", (e) => {
    e.preventDefault();
    modal.style.display = "block";
  });
  cancelBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
  confirmBtn.addEventListener("click", () => {
    modal.style.display = "none";
    fetch(deleteAccountUrl, {
      method: "Delete",
      headers: { "X-CSRFToken": csrfToken },
    })
      .then((res) => res.json())
      .then((response) => {
        if (response.success) {
          showToast("✅ Account deleted successfully.", "success");
          setTimeout(() => {
            window.location.replace(accountLoginUrl);
          }, 2000);
        } else {
          showToast("⚠️ Something went wrong while deleting the account.", "error");
        }
      })
      .catch(() => {
        showToast("❌ Error: Unable to delete account. Please try again.", "error");
      });
  });
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });
  document.querySelectorAll(".label-option").forEach(function (el) {
    function updateColor() {
        if (el.value === "") {
            el.classList.add("placeholder");
        } else {
            el.classList.remove("placeholder");
        }
    }
    updateColor();
    el.addEventListener("change", updateColor);
  });
});
