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
    show("processing");
    processingText.textContent = translations[currentLang].processing_deposit;
    try {
      const res = await fetch("/api/v1/customer/deposit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ depositCode: depositInput.value }),
      });
      const data = await res.json();
      if (!res.ok || data.success === false) {
        throw new Error(data.message || "error");
      }
      successText.textContent = translations[currentLang].success_deposit;
      show("success");
      setTimeout(() => show("home"), 4000);
    } catch (err) {
      errorText.textContent = translations[currentLang].error_invalid;
      show("error");
    }
  }

  async function submitWithdraw() {
    if (!withdrawInput.value) return;
    show("processing");
    processingText.textContent = translations[currentLang].processing_withdraw;
    try {
      const res = await fetch("/api/v1/customer/withdraw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: withdrawInput.value }),
      });
      const data = await res.json();
      if (!res.ok || data.success === false) {
        throw new Error(data.message || "error");
      }
      successText.textContent = translations[currentLang].success_withdraw;
      show("success");
      setTimeout(() => show("home"), 4000);
    } catch (err) {
      errorText.textContent = translations[currentLang].error_invalid;
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

