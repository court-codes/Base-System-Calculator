/* Mirrors calculator_core.api_calculate for offline / file:// use. Keep in sync with Python. */
(function () {
  const DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  function checkInputs(numberInput, baseInput) {
    let s = numberInput;
    if (s.startsWith("-")) s = s.slice(1);
    const allowed = DIGITS.slice(0, baseInput);
    for (const ch of s.replace(/\./g, "")) {
      if (!allowed.includes(ch)) return false;
    }
    return true;
  }

  function validateBase(b) {
    if (b < 2 || b > 36) throw new Error("Base must be between 2 and 36.");
  }

  function convertToBase10(numberInput, baseInput) {
    let s = numberInput;
    let neg = false;
    if (s.startsWith("-")) {
      neg = true;
      s = s.slice(1);
    }
    if (!checkInputs(s, baseInput)) return null;
    let whole;
    let fraction;
    if (s.includes(".")) {
      [whole, fraction] = s.split(".");
    } else {
      whole = s;
      fraction = "";
    }
    let value = 0;
    const lw = whole.length;
    for (let x = 0; x < lw; x++) {
      const digitValue = DIGITS.indexOf(whole[x]);
      const power = lw - 1 - x;
      value += digitValue * baseInput ** power;
    }
    const lf = fraction.length;
    for (let y = 0; y < lf; y++) {
      const digitValue = DIGITS.indexOf(fraction[y]);
      const power = -(y + 1);
      value += digitValue * baseInput ** power;
    }
    return neg ? -value : value;
  }

  function convertFromBase10(value, desiredBase) {
    if (value === 0) return "0";
    let neg = false;
    if (value < 0) {
      neg = true;
      value = -value;
    }
    let wholePart = Math.trunc(value);
    let fractionPart = value - wholePart;
    let wholeResult = "";
    while (wholePart > 0) {
      const remainder = wholePart % desiredBase;
      wholeResult = DIGITS[remainder] + wholeResult;
      wholePart = Math.floor(wholePart / desiredBase);
    }
    let fractionResult = "";
    let count = 0;
    const maxPlaces = 15;
    while (fractionPart > 0 && count < maxPlaces) {
      fractionPart *= desiredBase;
      const digit = Math.floor(fractionPart);
      fractionResult += DIGITS[digit];
      fractionPart -= digit;
      count += 1;
    }
    let result = fractionResult ? `${wholeResult}.${fractionResult}` : wholeResult;
    if (neg) result = `-${result}`;
    return result;
  }

  function parseBase(s, fieldName) {
    const str = String(s ?? "").trim();
    if (!/^[0-9]+$/.test(str)) {
      throw new Error(`${fieldName} must be a whole number.`);
    }
    return parseInt(str, 10);
  }

  function apiCalculate(payload) {
    const op = String(payload.operation ?? "")
      .trim()
      .toLowerCase();
    try {
      if (op === "convert") {
        const numberInput = String(payload.number ?? "")
          .trim()
          .toUpperCase();
        const baseInput = parseBase(payload.fromBase, "Starting base");
        const desiredBase = parseBase(payload.toBase, "Target base");
        validateBase(baseInput);
        validateBase(desiredBase);
        const base10 = convertToBase10(numberInput, baseInput);
        if (base10 === null) {
          return { ok: false, error: "Invalid digits for the starting base." };
        }
        const finalValue = convertFromBase10(base10, desiredBase);
        return {
          ok: true,
          result: finalValue,
          expression: `${numberInput} (base ${baseInput}) → base ${desiredBase}`,
        };
      }

      if (
        op === "add" ||
        op === "subtract" ||
        op === "multiply" ||
        op === "divide"
      ) {
        const n1 = String(payload.num1 ?? "")
          .trim()
          .toUpperCase();
        const n2 = String(payload.num2 ?? "")
          .trim()
          .toUpperCase();
        const baseInput = parseBase(payload.base, "Base");
        validateBase(baseInput);
        const v1 = convertToBase10(n1, baseInput);
        const v2 = convertToBase10(n2, baseInput);
        if (v1 === null || v2 === null) {
          return { ok: false, error: "Invalid digits for this base." };
        }
        const sym = { add: "+", subtract: "−", multiply: "×", divide: "÷" }[op];
        let result;
        if (op === "add") result = v1 + v2;
        else if (op === "subtract") result = v1 - v2;
        else if (op === "multiply") result = v1 * v2;
        else {
          if (v2 === 0) return { ok: false, error: "Division by zero." };
          result = v1 / v2;
        }
        return {
          ok: true,
          result: convertFromBase10(result, baseInput),
          expression: `${n1} ${sym} ${n2} (base ${baseInput})`,
        };
      }

      if (op === "sqrt") {
        const numberInput = String(payload.number ?? "")
          .trim()
          .toUpperCase();
        const baseInput = parseBase(payload.base, "Base");
        validateBase(baseInput);
        const value = convertToBase10(numberInput, baseInput);
        if (value === null) {
          return { ok: false, error: "Invalid digits for this base." };
        }
        if (value < 0) {
          return {
            ok: false,
            error: "Cannot take square root of a negative number.",
          };
        }
        return {
          ok: true,
          result: convertFromBase10(Math.sqrt(value), baseInput),
          expression: `√${numberInput} (base ${baseInput})`,
        };
      }

      if (op === "nthroot") {
        const numberInput = String(payload.number ?? "")
          .trim()
          .toUpperCase();
        const baseInput = parseBase(payload.base, "Base");
        const nRaw = String(payload.n ?? "").trim();
        validateBase(baseInput);
        if (!/^[0-9]+$/.test(nRaw)) {
          return {
            ok: false,
            error: "Root degree must be a non-negative whole number.",
          };
        }
        const n = parseInt(nRaw, 10);
        if (n === 0) {
          return { ok: false, error: "Root degree cannot be zero." };
        }
        const value = convertToBase10(numberInput, baseInput);
        if (value === null) {
          return { ok: false, error: "Invalid digits for this base." };
        }
        if (value < 0 && n % 2 === 0) {
          return {
            ok: false,
            error: "Cannot take an even root of a negative number.",
          };
        }
        return {
          ok: true,
          result: convertFromBase10(Math.pow(value, 1 / n), baseInput),
          expression: `${n}√${numberInput} (base ${baseInput})`,
        };
      }

      return { ok: false, error: "Unknown operation." };
    } catch (e) {
      return { ok: false, error: e.message || String(e) };
    }
  }

  window.calculatorApiCalculate = apiCalculate;
})();
