(() => {
  const screens = {
    home: document.getElementById("screen-home"),
    deposit: document.getElementById("screen-deposit"),
    withdraw: document.getElementById("screen-withdraw"),
    processing: document.getElementById("screen-processing"),
    success: document.getElementById("screen-success"),
    error: document.getElementById("screen-error"),
  };

  const langBtn = document.getElementById("lang-toggle");
  let currentLang = localStorage.getItem("locker_lang") || "fr";

  const depositInput = document.getElementById("deposit-code");
  const withdrawInput = document.getElementById("withdraw-code");
  const depositStatus = document.getElementById("deposit-status");
  const withdrawStatus = document.getElementById("withdraw-status");
  const processingText = document.getElementById("processing-text");
  const successText = document.getElementById("success-text");
  const errorText = document.getElementById("error-text");

  new window.Keypad(depositInput, document.getElementById("deposit-keypad"));
  new window.Keypad(withdrawInput, document.getElementById("withdraw-keypad"));

  function setLang(lang) {
    currentLang = lang;
    localStorage.setItem("locker_lang", lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    langBtn.textContent = lang.toUpperCase();
    applyTranslations();
  }

  function applyTranslations() {
    const dict = translations[currentLang];
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });
  }

  function show(screen) {
    Object.values(screens).forEach((el) => el.classList.add("hidden"));
    screens[screen].classList.remove("hidden");
  }

  async function submitDeposit() {
    if (!depositInput.value) return;
    const trackingCode = depositInput.value;

    show("processing");
    processingText.textContent = translations[currentLang].processing_deposit;

    try {
      // Step 1: Request to open the locker
      const openRes = await fetch("http://localhost:3000/open-deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lockerId: 1,
          trackingCode: trackingCode
        }),
      });
      const openData = await openRes.json();

      if (!openRes.ok) {
        throw new Error(openData.message || "Locker unavailable");
      }

      // Show success message that locker is opening
      processingText.textContent = openData.message + " - " + translations[currentLang].place_package;

      // Simulate waiting for user to place package and close door (5 seconds)
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Step 2: Notify server that door is closed
      processingText.textContent = translations[currentLang].finalizing;
      const closeRes = await fetch("http://localhost:3000/close-deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lockerId: 1,
          closetId: 1,
          trackingCode: trackingCode
        }),
      });
      const closeData = await closeRes.json();

      if (!closeRes.ok) {
        throw new Error(closeData.message || "error");
      }

      // Show the generated password to the user
      successText.innerHTML = `
        <div style="font-size: 1.2em; margin-bottom: 1em;">${translations[currentLang].success_deposit}</div>
        <div style="font-size: 2em; font-weight: bold; color: #4CAF50; margin: 0.5em 0;">${closeData.password}</div>
        <div style="font-size: 0.9em; opacity: 0.8;">${translations[currentLang].save_password || 'Save this password to retrieve your package'}</div>
      `;
      show("success");

      // Clear input
      depositInput.value = "";

      setTimeout(() => show("home"), 8000);
    } catch (err) {
      console.error(err);
      errorText.textContent = err.message || translations[currentLang].error_invalid;
      show("error");
    }
  }

  async function submitWithdraw() {
    if (!withdrawInput.value) return;
    const password = withdrawInput.value;

    show("processing");
    processingText.textContent = translations[currentLang].processing_withdraw;

    try {
      // Step 1: Request to open the locker with password
      const openRes = await fetch("http://localhost:3000/open-withdraw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lockerId: 1,
          password: password
        }),
      });
      const openData = await openRes.json();

      if (!openRes.ok) {
        throw new Error(openData.message || "Invalid password");
      }

      // Show success message that locker is opening
      processingText.textContent = openData.message + " - " + translations[currentLang].take_package;

      // Simulate waiting for user to take package and close door (5 seconds)
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Step 2: Notify server that door is closed after withdrawal
      processingText.textContent = translations[currentLang].finalizing;
      const closeRes = await fetch("http://localhost:3000/close-withdraw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lockerId: 1,
          closetId: 1
        }),
      });
      const closeData = await closeRes.json();

      if (!closeRes.ok) {
        throw new Error(closeData.message || "error");
      }

      successText.textContent = translations[currentLang].success_withdraw;
      show("success");

      // Clear input
      withdrawInput.value = "";

      setTimeout(() => show("home"), 4000);
    } catch (err) {
      console.error(err);
      errorText.textContent = err.message || translations[currentLang].error_invalid;
      show("error");
    }
  }

  // Button bindings
  document.getElementById("btn-deposit").addEventListener("click", () => show("deposit"));
  document.getElementById("btn-withdraw").addEventListener("click", () => show("withdraw"));
  document.getElementById("deposit-back").addEventListener("click", () => show("home"));
  document.getElementById("withdraw-back").addEventListener("click", () => show("home"));
  document.getElementById("deposit-submit").addEventListener("click", submitDeposit);
  document.getElementById("withdraw-submit").addEventListener("click", submitWithdraw);
  document.getElementById("error-back").addEventListener("click", () => show("home"));

  langBtn.addEventListener("click", () => setLang(currentLang === "fr" ? "ar" : "fr"));

  // Init
  setLang(currentLang);
  show("home");
})();


