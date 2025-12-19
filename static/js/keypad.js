class Keypad {
  constructor(targetInput, container) {
    this.input = targetInput;
    this.container = container;
    this.render();
  }

  render() {
    const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "C", "0", "⌫"];
    this.container.innerHTML = "";
    keys.forEach((key) => {
      const btn = document.createElement("button");
      btn.className = "key" + (isNaN(key) ? " special" : "");
      btn.textContent = key;
      btn.addEventListener("click", () => this.handlePress(key));
      this.container.appendChild(btn);
    });
  }

  handlePress(key) {
    if (key === "C") {
      this.input.value = "";
      return;
    }
    if (key === "⌫") {
      this.input.value = this.input.value.slice(0, -1);
      return;
    }
    if (!isNaN(key)) {
      this.input.value += key;
    }
  }
}

window.Keypad = Keypad;


