/*
 * CodeAlpha Portfolio Tracker — browser demo layer.
 *
 * This file is a lightweight, GitHub Pages-compatible MIRROR of the
 * weighted-average-cost logic implemented canonically in Python
 * (portfolio_tracker/portfolio.py, calculations.py). It exists only so the
 * demo can run as a static page; it is not the source of truth for the
 * accounting logic. See README.md -> "Architecture" for details.
 */

const PRICES = { TCS: 3500, INFY: 1650, RELIANCE: 2900, HDFCBANK: 1750, ITC: 450 };

const SEED_TRANSACTIONS = [
  { ticker: "TCS", type: "BUY", qty: 10, price: 3000 },
  { ticker: "TCS", type: "BUY", qty: 5, price: 3200 },
  { ticker: "INFY", type: "BUY", qty: 8, price: 1500 },
  { ticker: "TCS", type: "SELL", qty: 4, price: 3500 },
];

let transactions = structuredClone(SEED_TRANSACTIONS);

const $ = (id) => document.getElementById(id);

// Rebuilds holdings state from the full transaction history, mirroring
// Portfolio.buy()/sell() in the Python package (weighted-average cost).
function computeHoldings() {
  const holdings = {};
  for (const tx of transactions) {
    const holding = (holdings[tx.ticker] ??= { qty: 0, cost: 0, realized: 0 });
    if (tx.type === "BUY") {
      holding.qty += tx.qty;
      holding.cost += tx.qty * tx.price;
    } else {
      if (tx.qty > holding.qty) continue; // defensive: UI already blocks overselling
      const avgCost = holding.cost / holding.qty;
      holding.realized += (tx.price - avgCost) * tx.qty;
      holding.cost -= avgCost * tx.qty;
      holding.qty -= tx.qty;
    }
  }
  for (const ticker of Object.keys(holdings)) {
    if (!holdings[ticker].qty) delete holdings[ticker];
  }
  return holdings;
}

function money(amount) {
  return "₹" + Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function render() {
  const holdings = computeHoldings();
  const rows = Object.entries(holdings).map(([ticker, h]) => {
    const value = h.qty * PRICES[ticker];
    const pnl = value - h.cost;
    return { ticker, ...h, value, pnl, returnPct: h.cost ? (pnl / h.cost) * 100 : 0 };
  });

  const totalValue = rows.reduce((sum, r) => sum + r.value, 0);
  const totalInvested = rows.reduce((sum, r) => sum + r.cost, 0);
  const totalPnl = totalValue - totalInvested;
  const returnPercent = totalInvested ? (totalPnl / totalInvested) * 100 : 0;

  const metrics = [
    { label: "Invested", value: money(totalInvested) },
    { label: "Current value", value: money(totalValue) },
    { label: "P/L", value: money(totalPnl), positive: totalPnl >= 0 },
    { label: "Return", value: `${returnPercent.toFixed(2)}%`, positive: returnPercent >= 0 },
  ];

  $("metrics").innerHTML = metrics
    .map(
      (m) =>
        `<div class="metric"><span>${m.label}</span><strong class="${
          m.positive === undefined ? "" : m.positive ? "positive" : "negative"
        }">${m.value}</strong></div>`
    )
    .join("");

  $("count").textContent = `${rows.length} holding${rows.length === 1 ? "" : "s"}`;

  $("holdings").innerHTML = rows.length
    ? rows
        .map((r) => {
          const avgCost = r.cost / r.qty;
          const allocation = totalValue ? (r.value / totalValue) * 100 : 0;
          return `<tr>
            <td>${r.ticker}</td>
            <td>${r.qty}</td>
            <td>${money(avgCost)}</td>
            <td>${money(PRICES[r.ticker])}</td>
            <td>${money(r.value)}</td>
            <td class="${r.pnl >= 0 ? "positive" : "negative"}">${money(r.pnl)}</td>
            <td class="${r.returnPct >= 0 ? "positive" : "negative"}">${r.returnPct.toFixed(2)}%</td>
            <td>${allocation.toFixed(1)}%</td>
          </tr>`;
        })
        .join("")
    : `<tr><td class="empty" colspan="8">No holdings yet.</td></tr>`;
}

function showMessage(text, isError = false) {
  $("message").textContent = text;
  $("message").style.color = isError ? "#e0193f" : "#0a8f4c";
}

function populateTickerOptions() {
  const tickerSelect = $("ticker");
  tickerSelect.innerHTML = Object.keys(PRICES).map((k) => `<option>${k}</option>`).join("");
  $("price").value = PRICES[tickerSelect.value];
}

function initEventListeners() {
  $("ticker").addEventListener("change", () => {
    $("price").value = PRICES[$("ticker").value];
  });

  $("txForm").addEventListener("submit", (event) => {
    event.preventDefault();

    const tx = {
      type: $("type").value,
      ticker: $("ticker").value,
      qty: Number($("quantity").value),
      price: Number($("price").value),
    };

    if (!Number.isInteger(tx.qty) || tx.qty <= 0 || !(tx.price > 0)) {
      showMessage("Enter a valid quantity and price.", true);
      return;
    }

    const owned = computeHoldings()[tx.ticker]?.qty || 0;
    if (tx.type === "SELL" && owned < tx.qty) {
      showMessage(`Cannot sell ${tx.qty}; only ${owned} owned.`, true);
      return;
    }

    transactions.push(tx);
    showMessage(`${tx.type === "BUY" ? "Bought" : "Sold"} ${tx.qty} ${tx.ticker} @ ${money(tx.price)}.`);
    render();
  });

  $("resetBtn").addEventListener("click", () => {
    transactions = structuredClone(SEED_TRANSACTIONS);
    showMessage("Demo reset.");
    render();
  });
}

populateTickerOptions();
initEventListeners();
render();
