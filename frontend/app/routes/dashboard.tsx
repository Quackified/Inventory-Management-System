import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { api } from "../lib/api";
import { getStoredToken } from "../lib/auth";
import type { Route } from "./+types/dashboard";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Warehouse/Store Management Dashboard" },
    { name: "description", content: "Inventory management dashboard" },
  ];
}

type DashboardSummary = {
  total_products: number;
  total_stock: number;
  total_inventory_value: number;
  low_stock_count: number;
  expired_count: number;
};

type ProductItem = {
  product_id: number;
  name: string;
  current_stock: number;
  warehouse: string;
  category: string;
  expiry_status: string;
};

type RecentTransactionItem = {
  transaction_id: number;
  product_name: string;
  type: string;
  quantity: number;
  transaction_date: string;
};

type WarehouseSummaryItem = {
  name: string;
  product_count: number;
  total_stock: number;
  total_value: number;
  expired_count: number;
  low_stock_count: number;
};

type ChartDataItem = {
  label: string;
  stock_in: number;
  stock_out: number;
};

export default function DashboardRoute() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [recentTransactions, setRecentTransactions] = useState<RecentTransactionItem[]>([]);
  const [warehouseSummary, setWarehouseSummary] = useState<WarehouseSummaryItem[]>([]);
  const [chartData, setChartData] = useState<ChartDataItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(5);
  const [totalProducts, setTotalProducts] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [today, setToday] = useState<{ day: string; date: string }>({ day: "--", date: "--" });
  const [chartsReady, setChartsReady] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setLoading(true);
    Promise.all([
      api.get("/api/v1/dashboard/summary"),
      api.get("/api/v1/products", { params: { page, page_size: pageSize } }),
      api.get("/api/v1/dashboard/recent-transactions", { params: { limit: 6 } }),
      api.get("/api/v1/dashboard/warehouse-summary"),
      api.get("/api/v1/dashboard/chart-data", { params: { period: "weekly" } }),
    ])
      .then(([summaryResponse, productsResponse, recentResponse, warehouseResponse, chartResponse]) => {
        setSummary(summaryResponse.data as DashboardSummary);
        setProducts((productsResponse.data.items ?? []) as ProductItem[]);
        setRecentTransactions((recentResponse.data ?? []) as RecentTransactionItem[]);
        setWarehouseSummary((warehouseResponse.data ?? []) as WarehouseSummaryItem[]);
        setChartData((chartResponse.data ?? []) as ChartDataItem[]);
        setTotalProducts(productsResponse.data.total ?? 0);
        setError(null);
      })
      .catch((requestError) => {
        setError(requestError instanceof Error ? requestError.message : "Failed to load dashboard");
      })
      .finally(() => setLoading(false));
  }, [navigate, page, pageSize]);

  useEffect(() => {
    const now = new Date();
    setToday({
      day: new Intl.DateTimeFormat("en-US", { weekday: "long" }).format(now),
      date: new Intl.DateTimeFormat("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
      }).format(now),
    });
    setChartsReady(true);
  }, []);

  const totalPages = Math.max(1, Math.ceil(totalProducts / pageSize));

  const chartSeries = useMemo(
    () =>
      chartData.map((item, index) => ({
        key: `${item.label}-${index}`,
        label: item.label,
        shortLabel: item.label.slice(0, 3),
        stock_in: item.stock_in,
        stock_out: item.stock_out,
      })),
    [chartData],
  );

  return (
    <main className="relative min-h-screen overflow-hidden text-stone-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-7rem] top-[-7rem] h-80 w-80 rounded-full bg-emerald-300/32 blur-3xl" />
        <div className="absolute right-[-7rem] top-[8rem] h-96 w-96 rounded-full bg-teal-500/10 blur-3xl" />
        <div className="absolute bottom-[-10rem] right-[18%] h-96 w-96 rounded-full bg-[#10b981]/16 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] min-w-0 flex-col gap-4 px-3 py-4 sm:px-4 lg:px-6 lg:py-5">
        <header className="rounded-xl border border-white/60 bg-white/72 px-4 py-3 shadow-[0_20px_60px_rgba(16,185,129,0.08)] backdrop-blur-xl">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-stone-500">Overview</p>
              <h1 className="mt-1 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Operations Dashboard</h1>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-stone-900">{today.day}</p>
              <p className="text-sm text-stone-600">{today.date}</p>
            </div>
          </div>
        </header>

        {error && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-5">
            {[
              { label: "Products", value: summary?.total_products ?? 0, accent: "from-stone-900 via-stone-800 to-stone-700" },
              { label: "Stock On Hand", value: summary?.total_stock ?? 0, accent: "from-emerald-700 via-emerald-600 to-teal-500" },
              { label: "Inventory Value", value: `PHP ${(summary?.total_inventory_value ?? 0).toLocaleString()}`, accent: "from-emerald-900 via-emerald-800 to-emerald-600" },
              { label: "Low Stock", value: summary?.low_stock_count ?? 0, accent: "from-green-700 via-lime-600 to-lime-500" },
              { label: "Expired", value: summary?.expired_count ?? 0, accent: "from-rose-700 via-red-600 to-orange-500" },
            ].map((card) => (
              <article key={card.label} className={`relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br ${card.accent} px-3 py-2.5 text-white shadow-[0_18px_40px_rgba(15,23,42,0.16)] backdrop-blur-xl`}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.22),transparent_38%)]" />
                <p className="relative truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">{card.label}</p>
                <h2 className="relative mt-1.5 truncate text-lg font-black tracking-tight text-white sm:text-xl lg:text-2xl">{card.value}</h2>
              </article>
            ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.45fr_1fr]">
          <article className="overflow-hidden rounded-xl border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
            <div className="flex flex-col gap-3 border-b border-stone-200/80 p-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Products</p>
                <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Recent inventory</h2>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
                  disabled={page === 1 || loading}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-stone-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Prev
                </button>
                <button
                  type="button"
                  onClick={() => setPage((currentPage) => Math.min(totalPages, currentPage + 1))}
                  disabled={page >= totalPages || loading}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-stone-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Name</th>
                    <th className="px-5 py-4 font-semibold">Stock</th>
                    <th className="px-5 py-4 font-semibold">Warehouse</th>
                    <th className="px-5 py-4 font-semibold">Category</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100 bg-white">
                  {products.map((product, index) => (
                    <tr key={product.product_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                      <td className="px-5 py-4 font-semibold text-stone-950">{product.name}</td>
                      <td className="px-5 py-4 text-stone-700">{product.current_stock}</td>
                      <td className="px-5 py-4 text-stone-700">{product.warehouse}</td>
                      <td className="px-5 py-4 text-stone-700">{product.category}</td>
                      <td className="px-5 py-4 text-stone-700">{product.expiry_status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <aside className="flex flex-col gap-4">
            <section className="rounded-xl border border-white/70 bg-white/82 p-4 shadow-[0_14px_30px_rgba(16,185,129,0.07)] backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Average movement</p>
                <span className="rounded-lg border border-stone-200 px-2.5 py-1 text-[11px] font-semibold text-stone-600">Weekly</span>
              </div>
              <div className="mt-3 rounded-xl border border-emerald-100 bg-emerald-50/70 p-3">
                {!chartsReady ? (
                  <p className="text-sm text-stone-500">Preparing charts...</p>
                ) : chartSeries.length === 0 ? (
                  <p className="text-sm text-stone-500">No chart data yet.</p>
                ) : (
                  <div className="h-52 w-full min-w-0">
                    <ResponsiveContainer width="100%" height="100%" minWidth={240} minHeight={180}>
                      <AreaChart data={chartSeries} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
                        <defs>
                          <linearGradient id="stockInFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#0f766e" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="#0f766e" stopOpacity={0.03} />
                          </linearGradient>
                          <linearGradient id="stockOutFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#16a34a" stopOpacity={0.28} />
                            <stop offset="95%" stopColor="#16a34a" stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#d6d3d1" vertical={false} />
                        <XAxis dataKey="shortLabel" tick={{ fill: "#57534e", fontSize: 11 }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fill: "#57534e", fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: "12px" }} />
                        <Area type="monotone" dataKey="stock_in" stroke="#0f766e" fill="url(#stockInFill)" strokeWidth={2.5} name="Stock In" />
                        <Area type="monotone" dataKey="stock_out" stroke="#16a34a" fill="url(#stockOutFill)" strokeWidth={2.5} name="Stock Out" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </section>

            <section className="rounded-xl border border-white/70 bg-white/82 p-4 shadow-[0_14px_30px_rgba(16,185,129,0.07)] backdrop-blur-xl">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">Connection</p>
              <p className="mt-2 text-sm text-stone-600">Backend: {import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001"}</p>
              <p className="mt-1 text-sm text-stone-600">Dashboard fetch: {loading ? "Loading..." : "Ready"}</p>
            </section>
          </aside>
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
          <article className="overflow-hidden rounded-xl border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
            <div className="border-b border-emerald-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">Stock flow</p>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Movement per day</h2>
            </div>
            <div className="h-72 min-w-0 p-4">
              {!chartsReady ? (
                <div className="flex h-full items-center justify-center text-sm text-stone-500">Preparing charts...</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%" minWidth={240} minHeight={220}>
                  <BarChart data={chartSeries} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#d6d3d1" vertical={false} />
                    <XAxis dataKey="shortLabel" tick={{ fill: "#57534e", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#57534e", fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: "12px" }} />
                    <Bar dataKey="stock_in" fill="#0f766e" radius={[4, 4, 0, 0]} name="Stock In" />
                    <Bar dataKey="stock_out" fill="#b45309" radius={[4, 4, 0, 0]} name="Stock Out" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </article>

          <article className="overflow-hidden rounded-xl border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
            <div className="border-b border-emerald-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">Recent transactions</p>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Latest activity</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Date</th>
                    <th className="px-5 py-4 font-semibold">Product</th>
                    <th className="px-5 py-4 font-semibold">Type</th>
                    <th className="px-5 py-4 font-semibold">Qty</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100 bg-white">
                  {recentTransactions.map((transaction, index) => (
                    <tr key={transaction.transaction_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                      <td className="px-5 py-4 text-stone-700">{transaction.transaction_date}</td>
                      <td className="px-5 py-4 font-semibold text-stone-950">{transaction.product_name}</td>
                      <td className="px-5 py-4 text-stone-700">{transaction.type}</td>
                      <td className="px-5 py-4 text-stone-700">{transaction.quantity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section className="overflow-hidden rounded-xl border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
          <div className="border-b border-emerald-100 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">Warehouse/store summary</p>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">{warehouseSummary.length} warehouses/stores loaded</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                <tr>
                  <th className="px-5 py-4 font-semibold">Warehouse/Store</th>
                  <th className="px-5 py-4 font-semibold">Products</th>
                  <th className="px-5 py-4 font-semibold">Stock</th>
                  <th className="px-5 py-4 font-semibold">Value</th>
                  <th className="px-5 py-4 font-semibold">Low/Exp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 bg-white">
                {warehouseSummary.map((entry, index) => (
                  <tr key={entry.name} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                    <td className="px-5 py-4 font-semibold text-stone-950">{entry.name}</td>
                    <td className="px-5 py-4 text-stone-700">{entry.product_count}</td>
                    <td className="px-5 py-4 text-stone-700">{entry.total_stock}</td>
                    <td className="px-5 py-4 text-stone-700">PHP {entry.total_value.toLocaleString()}</td>
                    <td className="px-5 py-4 text-stone-700">{entry.low_stock_count}/{entry.expired_count}</td>
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
