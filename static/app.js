(function () {
  function calculateApiUrl() {
    try {
      const u = new URL(window.location.href);
      if (u.protocol === "http:" || u.protocol === "https:") {
        return new URL("api/calculate", u.href).href;
      }
    } catch (_) {
      /* ignore */
    }
    return null;
  }

  const form = document.getElementById("calc-form");
  const operation = document.getElementById("operation");
  const submitBtn = document.getElementById("submit-btn");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const resultExpression = document.getElementById("result-expression");
  const resultValue = document.getElementById("result-value");

  const groups = {
    convert: document.getElementById("group-convert"),
    binary: document.getElementById("group-binary"),
    sqrt: document.getElementById("group-sqrt"),
    nth: document.getElementById("group-nth"),
  };

  function showGroup(op) {
    Object.values(groups).forEach((el) => el.classList.add("hidden"));
    if (op === "convert") groups.convert.classList.remove("hidden");
    else if (
      op === "add" ||
      op === "subtract" ||
      op === "multiply" ||
      op === "divide"
    )
      groups.binary.classList.remove("hidden");
    else if (op === "sqrt") groups.sqrt.classList.remove("hidden");
    else if (op === "nthroot") groups.nth.classList.remove("hidden");
  }

  function hideMessages() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
    resultBox.classList.add("hidden");
  }

  function showError(msg) {
    resultBox.classList.add("hidden");
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }

  function showResult(expression, value) {
    errorBox.classList.add("hidden");
    resultExpression.textContent = expression;
    resultValue.textContent = value;
    resultBox.classList.remove("hidden");
  }

  function buildPayload(op) {
    if (op === "convert") {
      return {
        operation: "convert",
        number: document.getElementById("conv-number").value.trim(),
        fromBase: document.getElementById("conv-from").value.trim(),
        toBase: document.getElementById("conv-to").value.trim(),
      };
    }
    if (
      op === "add" ||
      op === "subtract" ||
      op === "multiply" ||
      op === "divide"
    ) {
      return {
        operation: op,
        num1: document.getElementById("bin-num1").value.trim(),
        num2: document.getElementById("bin-num2").value.trim(),
        base: document.getElementById("bin-base").value.trim(),
      };
    }
    if (op === "sqrt") {
      return {
        operation: "sqrt",
        number: document.getElementById("sqrt-number").value.trim(),
        base: document.getElementById("sqrt-base").value.trim(),
      };
    }
    if (op === "nthroot") {
      return {
        operation: "nthroot",
        number: document.getElementById("nth-number").value.trim(),
        base: document.getElementById("nth-base").value.trim(),
        n: document.getElementById("nth-n").value.trim(),
      };
    }
    return null;
  }

  operation.addEventListener("change", () => {
    showGroup(operation.value);
    hideMessages();
  });

  showGroup(operation.value);

  function calculateLocally(payload) {
    if (typeof window.calculatorApiCalculate !== "function") {
      return {
        ok: false,
        error: "Calculator script failed to load. Refresh the page.",
      };
    }
    return window.calculatorApiCalculate(payload);
  }

  async function runCalculation(payload) {
    const local = () => calculateLocally(payload);
    if (window.location.protocol === "file:") {
      return local();
    }
    const url = calculateApiUrl();
    if (!url) {
      return local();
    }
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const text = await res.text();
      let data;
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        return local();
      }
      if (typeof data.ok === "boolean") {
        return data;
      }
      return local();
    } catch {
      return local();
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessages();
    const op = operation.value;
    const payload = buildPayload(op);
    submitBtn.disabled = true;
    try {
      const data = await runCalculation(payload);
      if (data.ok) {
        showResult(data.expression || "", data.result);
      } else {
        showError(data.error || "Something went wrong.");
      }
    } finally {
      submitBtn.disabled = false;
    }
  });
})();
