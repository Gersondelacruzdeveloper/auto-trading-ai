import { useEffect, useState } from "react";
import { Play, RefreshCcw, TrendingDown, TrendingUp } from "lucide-react";

import { api } from "./api";

import type { Trade, TradingBot } from "./types";

export default function App() {
  const [bots, setBots] = useState<TradingBot[]>([]);

  const [trades, setTrades] = useState<Trade[]>([]);

  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);

      const [botsResponse, tradesResponse] = await Promise.all([
        api.get("/bots/"),
        api.get("/trades/"),
      ]);

      setBots(botsResponse.data);

      setTrades(tradesResponse.data);
    } catch (error) {
      console.error(error);

      setMessage("Could not connect to backend.");
    } finally {
      setLoading(false);
    }
  };

const runBot = async (botId: number) => {
  try {
    setLoading(true);

    const response = await api.post(`/bots/${botId}/run/`);

    console.log("RUN BOT RESPONSE:", response.data);

    if (response.data?.message) {
      setMessage(response.data.message);
    } else {
      setMessage("Trade created successfully.");
    }

    await loadData();
  } catch (error) {
    console.error("RUN BOT ERROR:", error);
    setMessage("Bot failed to run. Check backend terminal.");
  } finally {
    setLoading(false);
  }
};
useEffect(() => {
  loadData();

  let socket: WebSocket | null = null;
  let shouldReconnect = true;

  const connectSocket = () => {
    socket = new WebSocket("ws://127.0.0.1:8000/ws/trades/");

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      console.log("Live data:", data);

      if (data.type === "live_trades") {
        setTrades(data.trades);
      }

      if (data.type === "error") {
        console.error("Backend websocket error:", data.message);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket closed");

      if (shouldReconnect) {
        setTimeout(() => {
          connectSocket();
        }, 2000);
      }
    };
  };

  connectSocket();

  return () => {
    shouldReconnect = false;

    if (socket) {
      socket.close();
    }
  };
}, []);

  const totalRisk = trades.reduce(
    (sum, trade) => sum + Number(trade.risk_amount || 0),
    0,
  );

  const totalPnl = trades.reduce(
    (sum, trade) => sum + Number(trade.pnl || 0),
    0,
  );

  const openTrades = trades.filter((trade) => trade.is_open).length;

  const buyTrades = trades.filter((trade) => trade.signal === "BUY").length;

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-10">
        <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="mb-2 text-sm font-bold uppercase tracking-[0.3em] text-emerald-400">
              Paper Trading System
            </p>

            <h1 className="text-3xl font-black md:text-5xl">
              AI Trading Dashboard
            </h1>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="
              inline-flex
              items-center
              justify-center
              gap-2
              rounded-2xl
              bg-white
              px-5
              py-3
              font-bold
              text-slate-950
            "
          >
            <RefreshCcw size={18} />
            Refresh
          </button>
        </header>

        {message && (
          <div className="mb-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-amber-200">
            {message}
          </div>
        )}

        {/* STATS */}

        <section className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-5">
          <StatCard title="Bots" value={bots.length.toString()} />

          <StatCard title="Open Trades" value={openTrades.toString()} />

          <StatCard title="BUY Signals" value={buyTrades.toString()} />

          <StatCard title="Total Risk" value={`$${totalRisk.toFixed(2)}`} />

          <StatCard title="Live PnL" value={`$${totalPnl.toFixed(2)}`} />
        </section>

        {/* BOTS */}

        <section className="mb-10">
          <h2 className="mb-4 text-2xl font-black">Trading Bots</h2>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
            {bots.map((bot) => (
              <div
                key={bot.id}
                className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl"
              >
                <div className="mb-5 flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-2xl font-black">{bot.name}</h3>

                    <p className="text-slate-400">{bot.symbol}</p>
                  </div>
                </div>

                <div className="mb-6 space-y-3">
                  <InfoRow label="Balance" value={`$${bot.balance}`} />

                  <InfoRow
                    label="Risk"
                    value={`${(bot.risk_per_trade * 100).toFixed(2)}%`}
                  />

                  <InfoRow label="Reward" value={`${bot.reward_ratio}:1`} />

                  <InfoRow
                    label="Profit Pot"
                    value={`$${Number(bot.profit_pot).toFixed(2)}`}
                  />

                  <InfoRow
                    label="Auto Close"
                    value={`$${Number(bot.auto_close_profit_amount).toFixed(2)}`}
                  />
                  <InfoRow
                    label="Max Loss"
                    value={`$${Number(bot.auto_close_loss_amount).toFixed(2)}`}
                  />
                </div>

                <button
                  onClick={() => runBot(bot.id)}
                  disabled={loading}
                  className="
                    flex
                    w-full
                    items-center
                    justify-center
                    gap-2
                    rounded-2xl
                    bg-emerald-500
                    px-5
                    py-3
                    font-black
                    text-slate-950
                  "
                >
                  <Play size={18} />
                  Run Bot
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* TRADES */}

        <section>
          <h2 className="mb-4 text-2xl font-black">Recent Trades</h2>

          <div className="overflow-hidden rounded-3xl border border-slate-800">
            <table className="w-full bg-slate-900 text-left text-sm">
              <thead className="bg-slate-900/80 text-slate-400">
                <tr>
                  <th className="p-4">Symbol</th>
                  <th className="p-4">Signal</th>
                  <th className="p-4">Entry</th>
                  <th className="p-4">Current</th>
                  <th className="p-4">PnL</th>
                  <th className="p-4">PnL %</th>
                  <th className="p-4">Stop</th>
                  <th className="p-4">Target</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>

              <tbody>
                {trades.map((trade) => (
                  <tr key={trade.id} className="border-t border-slate-800">
                    <td className="p-4 font-bold">{trade.symbol}</td>

                    <td className="p-4">
                      <SignalBadge signal={trade.signal} />
                    </td>

                    <td className="p-4">
                      ${Number(trade.entry_price).toFixed(2)}
                    </td>

                    <td className="p-4">
                      ${Number(trade.current_price).toFixed(2)}
                    </td>

                    <td
                      className={`p-4 font-bold ${
                        trade.pnl >= 0 ? "text-emerald-400" : "text-red-400"
                      }`}
                    >
                      ${Number(trade.pnl).toFixed(2)}
                    </td>

                    <td
                      className={`p-4 font-bold ${
                        trade.pnl_percent >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {Number(trade.pnl_percent).toFixed(2)}%
                    </td>

                    <td className="p-4">
                      ${Number(trade.stop_loss).toFixed(2)}
                    </td>

                    <td className="p-4">
                      ${Number(trade.take_profit).toFixed(2)}
                    </td>

                    <td className="p-4">
                      <span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-black text-sky-400">
                                          {trade.is_open
                        ? "OPEN"
                        : trade.closed_reason || "CLOSED"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>

      <p className="mt-2 text-3xl font-black">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-slate-950/60 px-4 py-3">
      <span className="text-slate-400">{label}</span>

      <span className="font-bold">{value}</span>
    </div>
  );
}

function SignalBadge({ signal }: { signal: Trade["signal"] }) {
  const isBuy = signal === "BUY";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-black ${
        isBuy
          ? "bg-emerald-500/15 text-emerald-400"
          : "bg-red-500/15 text-red-400"
      }`}
    >
      {isBuy ? <TrendingUp size={14} /> : <TrendingDown size={14} />}

      {signal}
    </span>
  );
}
