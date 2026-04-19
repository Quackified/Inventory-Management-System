import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/transactions";
import { api, getApiErrorMessage } from "../lib/api";
import { getRoleHomePath, getStoredToken, getStoredUser, hasRoleAccess, type AuthUser } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Transactions - Warehouse/Store Management" },
    { name: "description", content: "Track and record stock movement" },
  ];
}

type TransactionItem = {
  transaction_id: number;
  product: string;
  type: "Stock-In" | "Stock-Out";
  quantity: number;
  unit_cost: number | null;
  total_cost: number | null;
  transaction_date: string;
  remarks: string | null;
  user: string;
  warehouse: string;
  category: string;
  batch: string;
};

function formatCurrency(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const numericValue = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(numericValue)) {
    return "-";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  }).format(numericValue);
}

type TransactionListResponse = {
  items: TransactionItem[];
  page: number;
  page_size: number;
  total: number;
};

type ProductLookup = {
  product_id: number;
  name: string;
};

type WarehouseLookup = {
  warehouse_id: number;
  name: string;
};

type TransactionFormState = {
  search: string;
};

export default function TransactionsRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [products, setProducts] = useState<ProductLookup[]>([]);
  const [warehouses, setWarehouses] = useState<WarehouseLookup[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [txnType, setTxnType] = useState("All");
  const [warehouseFilter, setWarehouseFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);
  const currentRole = user?.role ?? "";
  const canViewLogs = currentRole === "Admin" || currentRole === "Manager";

  useEffect(() => {
    setUser(getStoredUser());
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    if (!hasRoleAccess(user?.role, ["Admin", "Manager"])) {
      navigate(getRoleHomePath(user?.role), { replace: true });
      return;
    }

    Promise.all([api.get("/api/v1/products", { params: { page: 1, page_size: 100 } }), api.get("/api/v1/warehouses")])
      .then(([productsResponse, warehousesResponse]) => {
        setProducts(productsResponse.data.items ?? []);
        setWarehouses(warehousesResponse.data.items ?? []);
      })
      .catch(() => {
        setError("Failed to load transaction references.");
      });
  }, [isHydrated, navigate, user]);

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    if (!canViewLogs) {
      setTransactions([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    api
      .get("/api/v1/transactions", {
        params: {
          page,
          page_size: pageSize,
          warehouse_id: warehouseFilter || undefined,
          search: search || undefined,
          txn_type: txnType,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
        },
      })
      .then((response) => {
        const payload = response.data as TransactionListResponse;
        setTransactions(payload.items ?? []);
        setTotal(payload.total ?? 0);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load transactions."));
      })
      .finally(() => setLoading(false));
  }, [canViewLogs, isHydrated, page, pageSize, search, txnType, warehouseFilter, dateFrom, dateTo]);

  async function exportTransactions() {
    if (!canViewLogs) return;

    setExporting(true);
    setError(null);
    try {
      const response = await api.get("/api/v1/exports/transactions", {
        responseType: "blob",
        params: {
          warehouse_id: warehouseFilter || undefined,
          search: search || undefined,
          txn_type: txnType,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
        },
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = "transactions.xlsx";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Failed to export transactions."));
    } finally {
      setExporting(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden text-stone-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-[-7rem] h-80 w-80 rounded-full bg-[rgba(163,124,64,0.24)] blur-3xl" />
        <div className="absolute right-[-8rem] top-[8rem] h-96 w-96 rounded-full bg-[rgba(105,107,69,0.16)] blur-3xl" />
        <div className="absolute bottom-[-10rem] left-[18%] h-96 w-96 rounded-full bg-[rgba(57,32,7,0.08)] blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] min-w-0 flex-col gap-4 px-3 py-4 sm:px-4 lg:px-6 lg:py-5">
        <header className="overflow-hidden rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_22px_70px_rgba(57,32,7,0.08)] backdrop-blur">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-700">Warehouse/Store Management</p>
                <span className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-500">
                  Transactions
                </span>
              </div>
              <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Transaction Log</h1>
              <p className="mt-2 text-sm text-stone-600">Read-only movement history. Record stock changes from the Products page.</p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {canViewLogs && (
                <button
                  type="button"
                  onClick={exportTransactions}
                  disabled={exporting}
                  className="inline-flex items-center justify-center rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {exporting ? "Exporting..." : "Export XLSX"}
                </button>
              )}
            </div>
          </div>
        </header>

        {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">{error}</div>}

        <section className="grid grid-cols-2 gap-2 lg:grid-cols-4">
            {[
              {
                label: "Log Access",
                value: canViewLogs ? "Allowed" : "Restricted",
                accent: canViewLogs ? "from-stone-900 via-stone-800 to-stone-700" : "from-rose-700 via-red-600 to-orange-500",
              },
              { label: "Current Page", value: page, accent: "from-emerald-700 via-emerald-600 to-teal-500" },
              { label: "Total Logs", value: total, accent: "from-emerald-900 via-emerald-800 to-emerald-600" },
              { label: "Products", value: products.length, accent: "from-green-700 via-lime-600 to-lime-500" },
            ].map((card) => (
              <article key={card.label} className={`relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br ${card.accent} px-3 py-2.5 text-white shadow-[0_18px_40px_rgba(15,23,42,0.16)] backdrop-blur-xl`}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.22),transparent_38%)]" />
                <p className="relative truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">{card.label}</p>
                <h2 className="relative mt-1.5 truncate text-xl font-black tracking-tight text-white lg:text-2xl">{card.value}</h2>
              </article>
            ))}
        </section>

        {canViewLogs ? (
          <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
            <div className="flex flex-col gap-4 border-b border-stone-200/80 p-5 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Transaction logs</p>
                <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">History and filters</h2>
              </div>

              <div className="grid w-full gap-3 sm:grid-cols-2 lg:w-auto lg:grid-cols-5">
                <input
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-stone-400"
                  placeholder="Search product"
                />
                <select
                  value={txnType}
                  onChange={(event) => {
                    setTxnType(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2.5 text-sm outline-none"
                >
                  <option value="All">All types</option>
                  <option value="Stock-In">Stock-In</option>
                  <option value="Stock-Out">Stock-Out</option>
                </select>
                <select
                  value={warehouseFilter}
                  onChange={(event) => {
                    setWarehouseFilter(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2.5 text-sm outline-none"
                >
                  <option value="">All warehouses</option>
                  {warehouses.map((warehouse) => (
                    <option key={warehouse.warehouse_id} value={warehouse.warehouse_id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(event) => {
                    setDateFrom(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2.5 text-sm outline-none"
                />
                <input
                  type="date"
                  value={dateTo}
                  onChange={(event) => {
                    setDateTo(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2.5 text-sm outline-none"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Date</th>
                    <th className="px-5 py-4 font-semibold">Product</th>
                    <th className="px-5 py-4 font-semibold whitespace-nowrap w-36">Type</th>
                    <th className="px-5 py-4 font-semibold">Qty</th>
                    <th className="px-5 py-4 font-semibold">Cost Price</th>
                    <th className="px-5 py-4 font-semibold">Total Cost</th>
                    <th className="px-5 py-4 font-semibold">Warehouse</th>
                    <th className="px-5 py-4 font-semibold">User</th>
                    <th className="px-5 py-4 font-semibold">Remarks</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100 bg-white">
                  {transactions.map((transaction, index) => (
                    <tr key={transaction.transaction_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                      <td className="px-5 py-4 text-stone-700">{transaction.transaction_date}</td>
                      <td className="px-5 py-4 font-semibold text-stone-950">{transaction.product}</td>
                      <td className="px-5 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex whitespace-nowrap rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${
                            transaction.type === "Stock-In" ? "bg-emerald-700" : "bg-amber-700"
                          }`}
                        >
                          {transaction.type}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-stone-700">{transaction.quantity}</td>
                      <td className="px-5 py-4 text-stone-700">{formatCurrency(transaction.unit_cost)}</td>
                      <td className="px-5 py-4 text-stone-700">{formatCurrency(transaction.total_cost)}</td>
                      <td className="px-5 py-4 text-stone-700">{transaction.warehouse}</td>
                      <td className="px-5 py-4 text-stone-700">{transaction.user}</td>
                      <td className="px-5 py-4 text-stone-700">{transaction.remarks || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex flex-col gap-4 border-t border-stone-200/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-stone-500">
                Page <span className="font-semibold text-stone-900">{page}</span> of <span className="font-semibold text-stone-900">{totalPages}</span>
                <span className="mx-2 text-stone-300">•</span>
                {loading ? "Loading data..." : `${total} total logs`}
              </p>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
                  disabled={page === 1 || loading}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-stone-700 transition hover:border-stone-300 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Prev
                </button>
                <button
                  type="button"
                  onClick={() => setPage((currentPage) => Math.min(totalPages, currentPage + 1))}
                  disabled={page >= totalPages || loading}
                  className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-stone-700 transition hover:border-stone-300 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          </section>
        ) : (
          <section className="rounded-[2rem] border border-white/70 bg-white/82 p-8 text-center shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Access restricted</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-stone-950">Transaction logs are limited to Admin and Manager roles.</h2>
            <p className="mt-3 text-sm text-stone-600">Stock movement is now recorded from the Products page.</p>
          </section>
        )}
      </div>
    </main>
  );
}
