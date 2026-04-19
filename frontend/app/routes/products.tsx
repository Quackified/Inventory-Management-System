import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/products";
import { api, getApiErrorMessage } from "../lib/api";
import { getStoredToken, getStoredUser, type AuthUser } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Products - Warehouse/Store Management" },
    { name: "description", content: "Manage products with pagination and actions" },
  ];
}

type ProductItem = {
  product_id: number;
  name: string;
  description: string | null;
  current_stock: number;
  unit_price: number;
  unit: string;
  warehouse: string;
  category: string;
  low_stock_threshold: number;
  expiry_date: string | null;
  expiry_status: string;
  manufactured_date: string | null;
  batch_number: string | null;
};

type ProductListResponse = {
  items: ProductItem[];
  page: number;
  page_size: number;
  total: number;
};

type MovementTab = "Stock-In" | "Stock-Out";

type MovementFormState = {
  type: MovementTab;
  quantity: string;
  warehouse_id: string;
  unit_price: string;
  remarks: string;
};

type ProductFormState = {
  name: string;
  description: string;
  current_stock: string;
  unit_price: string;
  unit: string;
  warehouse_id: string;
  category_id: string;
  low_stock_threshold: string;
  expiry_date: string;
  manufactured_date: string;
  batch_number: string;
};

type LookupItem = {
  warehouse_id?: number;
  category_id?: number;
  name: string;
};

const emptyForm: ProductFormState = {
  name: "",
  description: "",
  current_stock: "0",
  unit_price: "0",
  unit: "pcs",
  warehouse_id: "",
  category_id: "",
  low_stock_threshold: "10",
  expiry_date: "",
  manufactured_date: "",
  batch_number: "",
};

const emptyMovementForm: MovementFormState = {
  type: "Stock-In",
  quantity: "1",
  warehouse_id: "",
  unit_price: "",
  remarks: "",
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  }).format(value);
}

function normalizeDate(value: string) {
  return value ? value : null;
}

export default function ProductsRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [categories, setCategories] = useState<LookupItem[]>([]);
  const [warehouses, setWarehouses] = useState<LookupItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(8);
  const [totalProducts, setTotalProducts] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [actionMenuId, setActionMenuId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editProductId, setEditProductId] = useState<number | null>(null);
  const [deleteProductId, setDeleteProductId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [form, setForm] = useState<ProductFormState>(emptyForm);
  const [exporting, setExporting] = useState(false);
  const [movementOpen, setMovementOpen] = useState(false);
  const [movementProduct, setMovementProduct] = useState<ProductItem | null>(null);
  const [movementForm, setMovementForm] = useState<MovementFormState>(emptyMovementForm);
  const [movementSaving, setMovementSaving] = useState(false);
  const [movementError, setMovementError] = useState<string | null>(null);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(totalProducts / pageSize)), [pageSize, totalProducts]);
  const currentRole = user?.role ?? "";
  const canManage = currentRole === "Admin" || currentRole === "Manager";

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setLoading(true);
    Promise.all([
      api.get("/api/v1/products", { params: { page, page_size: pageSize, search: search || undefined } }),
      api.get("/api/v1/categories"),
      api.get("/api/v1/warehouses"),
    ])
      .then(([productsResponse, categoriesResponse, warehousesResponse]) => {
        setProducts((productsResponse.data as ProductListResponse).items ?? []);
        setTotalProducts((productsResponse.data as ProductListResponse).total ?? 0);
        setCategories(categoriesResponse.data.items ?? []);
        setWarehouses(warehousesResponse.data.items ?? []);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load products."));
      })
      .finally(() => setLoading(false));
  }, [navigate, page, pageSize, search]);

  function openCreateModal() {
    setEditProductId(null);
    setForm(emptyForm);
    setFormError(null);
    setFormOpen(true);
  }

  function openMovementModal(product: ProductItem, tab: MovementTab = "Stock-In") {
    setActionMenuId(null);
    setMovementProduct(product);
    setMovementForm({
      type: tab,
      quantity: "1",
      warehouse_id: "",
      unit_price: String(product.unit_price),
      remarks: "",
    });
    setMovementError(null);
    setMovementOpen(true);
  }

  function openEditModal(product: ProductItem) {
    setEditProductId(product.product_id);
    setForm({
      name: product.name,
      description: product.description ?? "",
      current_stock: String(product.current_stock),
      unit_price: String(product.unit_price),
      unit: product.unit,
      warehouse_id: "",
      category_id: "",
      low_stock_threshold: String(product.low_stock_threshold),
      expiry_date: product.expiry_date ?? "",
      manufactured_date: product.manufactured_date ?? "",
      batch_number: product.batch_number ?? "",
    });
    setFormError(null);
    setFormOpen(true);
  }

  function closeModal() {
    setFormOpen(false);
    setEditProductId(null);
    setFormError(null);
    setSaving(false);
  }

  function closeMovementModal() {
    setMovementOpen(false);
    setMovementProduct(null);
    setMovementError(null);
    setMovementSaving(false);
  }

  async function submitForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    if (!Number.isFinite(Number(form.current_stock)) || Number(form.current_stock) < 0) {
      setFormError("Current stock must be a valid number (0 or higher).");
      setSaving(false);
      return;
    }

    if (!Number.isFinite(Number(form.unit_price)) || Number(form.unit_price) < 0) {
      setFormError("Cost price must be a valid number (0 or higher).");
      setSaving(false);
      return;
    }

    if (!Number.isFinite(Number(form.low_stock_threshold)) || Number(form.low_stock_threshold) < 0) {
      setFormError("Low stock threshold must be a valid number (0 or higher).");
      setSaving(false);
      return;
    }

    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      current_stock: Number(form.current_stock),
      unit_price: Number(form.unit_price),
      unit: form.unit.trim(),
      warehouse_id: form.warehouse_id ? Number(form.warehouse_id) : null,
      category_id: form.category_id ? Number(form.category_id) : null,
      low_stock_threshold: Number(form.low_stock_threshold),
      expiry_date: normalizeDate(form.expiry_date),
      manufactured_date: normalizeDate(form.manufactured_date),
      batch_number: form.batch_number.trim() || null,
    };

    try {
      if (editProductId) {
        await api.put(`/api/v1/products/${editProductId}`, payload);
      } else {
        await api.post("/api/v1/products", payload);
      }
      closeModal();
      setPage(1);
      const refreshed = await api.get("/api/v1/products", {
        params: { page: 1, page_size: pageSize, search: search || undefined },
      });
      setProducts((refreshed.data as ProductListResponse).items ?? []);
      setTotalProducts((refreshed.data as ProductListResponse).total ?? 0);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Unable to save product."));
    } finally {
      setSaving(false);
    }
  }

  async function deleteProduct() {
    if (!deleteProductId) return;
    setSaving(true);
    setFormError(null);

    try {
      await api.delete(`/api/v1/products/${deleteProductId}`);
      setDeleteProductId(null);
      const refreshed = await api.get("/api/v1/products", {
        params: { page, page_size: pageSize, search: search || undefined },
      });
      setProducts((refreshed.data as ProductListResponse).items ?? []);
      setTotalProducts((refreshed.data as ProductListResponse).total ?? 0);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Unable to delete product."));
    } finally {
      setSaving(false);
    }
  }

  async function exportProducts() {
    setExporting(true);
    setError(null);
    try {
      const response = await api.get("/api/v1/exports/products", {
        responseType: "blob",
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = "products.xlsx";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Failed to export products."));
    } finally {
      setExporting(false);
    }
  }

  async function submitMovement(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!movementProduct) return;

    setMovementSaving(true);
    setMovementError(null);

    if (!Number.isFinite(Number(movementForm.quantity)) || Number(movementForm.quantity) <= 0) {
      setMovementError("Quantity must be a number greater than zero.");
      setMovementSaving(false);
      return;
    }

    if (movementForm.type === "Stock-In" && movementForm.unit_price && Number(movementForm.unit_price) < 0) {
      setMovementError("Unit price cannot be a negative number.");
      setMovementSaving(false);
      return;
    }

    const payload = {
      product_id: movementProduct.product_id,
      type: movementForm.type,
      quantity: Number(movementForm.quantity),
      remarks: movementForm.remarks.trim() || null,
      warehouse_id: movementForm.warehouse_id ? Number(movementForm.warehouse_id) : null,
      unit_price: movementForm.unit_price && movementForm.type === "Stock-In" ? Number(movementForm.unit_price) : null,
    };

    try {
      await api.post("/api/v1/transactions", payload);
      closeMovementModal();
      const refreshed = await api.get("/api/v1/products", {
        params: { page, page_size: pageSize, search: search || undefined },
      });
      setProducts((refreshed.data as ProductListResponse).items ?? []);
      setTotalProducts((refreshed.data as ProductListResponse).total ?? 0);
    } catch (requestError) {
      setMovementError(getApiErrorMessage(requestError, "Failed to record movement."));
    } finally {
      setMovementSaving(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden text-stone-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-7rem] top-[-6rem] h-80 w-80 rounded-full bg-emerald-300/32 blur-3xl" />
        <div className="absolute right-[-8rem] top-[8rem] h-96 w-96 rounded-full bg-teal-500/10 blur-3xl" />
        <div className="absolute bottom-[-10rem] right-[20%] h-96 w-96 rounded-full bg-[#10b981]/16 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] min-w-0 flex-col gap-4 px-3 py-4 sm:px-4 lg:px-6 lg:py-5">
        <header className="overflow-hidden rounded-2xl border border-white/60 bg-white/72 px-4 py-3 shadow-[0_22px_70px_rgba(16,185,129,0.08)] backdrop-blur-xl">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700">Warehouse/Store Management</p>
                <span className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-500">
                  Products
                </span>
              </div>
              <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Product Management</h1>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={openCreateModal}
                className="inline-flex items-center justify-center rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white shadow-[0_14px_30px_rgba(16,185,129,0.22)] transition hover:-translate-y-0.5 hover:brightness-110"
              >
                Add product
              </button>
              <button
                type="button"
                onClick={exportProducts}
                disabled={exporting}
                className="inline-flex items-center justify-center rounded-full border border-emerald-200 bg-white/85 px-5 py-2.5 text-sm font-semibold text-emerald-800 shadow-sm transition hover:-translate-y-0.5 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {exporting ? "Exporting..." : "Export XLSX"}
              </button>
            </div>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 shadow-sm">
            {error}
          </div>
        )}

        <section className="grid grid-cols-2 gap-2 lg:grid-cols-4">
            {[
              { label: "Total Products", value: totalProducts, accent: "from-stone-900 via-stone-800 to-stone-700" },
              { label: "Visible Page", value: page, accent: "from-emerald-700 via-emerald-600 to-teal-500" },
              { label: "Warehouses", value: warehouses.length, accent: "from-emerald-900 via-emerald-800 to-emerald-600" },
              { label: "Categories", value: categories.length, accent: "from-green-700 via-lime-600 to-lime-500" },
            ].map((card) => (
              <article key={card.label} className={`relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br ${card.accent} px-3 py-2.5 text-white shadow-[0_18px_40px_rgba(15,23,42,0.16)] backdrop-blur-xl`}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.22),transparent_38%)]" />
                <p className="relative truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">{card.label}</p>
                <h2 className="relative mt-1.5 truncate text-xl font-black tracking-tight text-white lg:text-2xl">{card.value}</h2>
              </article>
            ))}
        </section>

        <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
          <div className="flex flex-col gap-4 border-b border-emerald-100/80 p-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-emerald-700">Product inventory</p>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Catalog overview</h2>
              <p className="mt-2 text-sm text-stone-600">A modern table for product management, cost pricing, and stock visibility.</p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <label className="flex min-w-[240px] items-center gap-3 rounded-full border border-emerald-200 bg-white/90 px-4 py-2.5 shadow-sm">
                <span className="text-sm text-emerald-500">⌕</span>
                <input
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setPage(1);
                  }}
                  className="w-full bg-transparent text-sm outline-none placeholder:text-stone-400"
                  placeholder="Search products"
                />
              </label>
              <button
                type="button"
                onClick={() => {
                  setSearch("");
                  setPage(1);
                }}
                className="rounded-full border border-emerald-200 bg-white/90 px-4 py-2 text-sm font-semibold text-emerald-800 transition hover:border-emerald-300 hover:bg-emerald-50"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                <tr>
                  <th className="px-5 py-4 font-semibold">Name</th>
                  <th className="px-5 py-4 font-semibold">Stock</th>
                  <th className="px-5 py-4 font-semibold">Unit</th>
                  <th className="px-5 py-4 font-semibold">Threshold</th>
                  <th className="px-5 py-4 font-semibold">Warehouse</th>
                  <th className="px-5 py-4 font-semibold">Category</th>
                  <th className="px-5 py-4 font-semibold">Status</th>
                  <th className="px-5 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 bg-white">
                {products.map((product, index) => (
                  <tr key={product.product_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                    <td className="px-5 py-4">
                      <div className="max-w-[18rem]">
                        <p className="font-semibold text-stone-950">{product.name}</p>
                        <p className="mt-1 truncate text-xs text-stone-500">{product.description || "No description"}</p>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-stone-700">{product.current_stock}</td>
                    <td className="px-5 py-4 text-stone-700">{product.unit}</td>
                    <td className="px-5 py-4 text-stone-700">{product.low_stock_threshold}</td>
                    <td className="px-5 py-4 text-stone-700">{product.warehouse}</td>
                    <td className="px-5 py-4 text-stone-700">{product.category}</td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${
                          product.expiry_status === "Expired"
                            ? "bg-[linear-gradient(135deg,#b91c1c,#ef4444)]"
                            : product.current_stock <= product.low_stock_threshold
                              ? "bg-[linear-gradient(135deg,#a16207,#d97706)]"
                              : "bg-[linear-gradient(135deg,#047857,#10b981)]"
                        }`}
                      >
                        {product.expiry_status === "Expired"
                          ? "Expired"
                          : product.current_stock <= product.low_stock_threshold
                            ? "Low stock"
                            : "Active"}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="relative inline-block text-left">
                        <button
                          type="button"
                          onClick={() => setActionMenuId((current) => (current === product.product_id ? null : product.product_id))}
                          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-emerald-200 bg-white/90 text-lg font-bold text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-50"
                          aria-label={`Actions for ${product.name}`}
                        >
                          ⋯
                        </button>

                        {actionMenuId === product.product_id && (
                          <div className="absolute right-0 top-12 z-10 w-44 overflow-hidden rounded-2xl border border-emerald-100 bg-white/92 p-1 shadow-[0_20px_40px_rgba(16,185,129,0.14)] backdrop-blur-xl">
                            <button
                              type="button"
                              onClick={() => openMovementModal(product)}
                              className="flex w-full items-center rounded-xl px-4 py-2.5 text-left text-sm font-medium text-emerald-700 transition hover:bg-emerald-50"
                            >
                              Record movement
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setActionMenuId(null);
                                openEditModal(product);
                              }}
                              className="flex w-full items-center rounded-xl px-4 py-2.5 text-left text-sm font-medium text-stone-700 transition hover:bg-stone-100"
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setActionMenuId(null);
                                setDeleteProductId(product.product_id);
                              }}
                              className="flex w-full items-center rounded-xl px-4 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50"
                            >
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-4 border-t border-stone-200/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-stone-500">
              Page <span className="font-semibold text-stone-900">{page}</span> of <span className="font-semibold text-stone-900">{totalPages}</span>
              <span className="mx-2 text-stone-300">•</span>
              {loading ? "Loading data..." : `${totalProducts} total products`}
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
      </div>

      {formOpen && (
        <div className="fixed inset-0 z-20 overflow-y-auto bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="mx-auto flex min-h-full w-full items-start justify-center">
            <div className="flex w-full max-w-3xl max-h-[92vh] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <div className="flex items-center justify-between border-b border-stone-200 px-6 py-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">
                  {editProductId ? "Edit product" : "Add product"}
                </p>
                <h3 className="mt-2 text-2xl font-black tracking-tight text-stone-950">
                  {editProductId ? "Update inventory item" : "Create new inventory item"}
                </h3>
              </div>
              <button
                type="button"
                onClick={closeModal}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
              >
                ×
              </button>
            </div>

              <form className="grid gap-5 overflow-y-auto p-4 sm:p-6" onSubmit={submitForm}>
              <section className="grid gap-4 rounded-3xl border border-stone-200/80 bg-stone-50/70 p-5 md:grid-cols-2">
                <div className="md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Basic details</p>
                  <p className="mt-1 text-sm text-stone-600">Essential information shown in the catalog.</p>
                </div>

                <label className="block md:col-span-2">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Product name</span>
                  <input
                    value={form.name}
                    onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                    placeholder="Example product"
                  />
                </label>

                <label className="block md:col-span-2">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Description</span>
                  <textarea
                    value={form.description}
                    onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
                    className="min-h-28 w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                    placeholder="Short description"
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Current stock</span>
                  <input
                    type="number"
                    value={form.current_stock}
                    onChange={(event) => setForm((current) => ({ ...current, current_stock: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  />
                  <p className="mt-1 text-xs text-stone-500">Numbers only. Use whole numbers (e.g. 0, 5, 120).</p>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Cost price</span>
                  <input
                    type="number"
                    step="0.01"
                    value={form.unit_price}
                    onChange={(event) => setForm((current) => ({ ...current, unit_price: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  />
                  <p className="mt-1 text-xs text-stone-500">Numbers only. Decimal values are allowed (e.g. 24.75).</p>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Unit</span>
                  <input
                    value={form.unit}
                    onChange={(event) => setForm((current) => ({ ...current, unit: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                    placeholder="pcs"
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Low stock threshold</span>
                  <input
                    type="number"
                    value={form.low_stock_threshold}
                    onChange={(event) => setForm((current) => ({ ...current, low_stock_threshold: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  />
                  <p className="mt-1 text-xs text-stone-500">Numbers only. Set the minimum stock alert level.</p>
                </label>
              </section>

              <section className="grid gap-4 rounded-3xl border border-stone-200/80 bg-white/70 p-5 md:grid-cols-2">
                <div className="md:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Advanced details</p>
                  <p className="mt-1 text-sm text-stone-600">Optional inventory metadata and shelf-life information.</p>
                </div>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Warehouse</span>
                  <select
                    value={form.warehouse_id}
                    onChange={(event) => setForm((current) => ({ ...current, warehouse_id: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  >
                    <option value="">None</option>
                    {warehouses.map((warehouse) => (
                      <option key={warehouse.warehouse_id} value={warehouse.warehouse_id}>
                        {warehouse.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Category</span>
                  <select
                    value={form.category_id}
                    onChange={(event) => setForm((current) => ({ ...current, category_id: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  >
                    <option value="">None</option>
                    {categories.map((category) => (
                      <option key={category.category_id} value={category.category_id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Expiry date</span>
                  <input
                    type="date"
                    value={form.expiry_date}
                    onChange={(event) => setForm((current) => ({ ...current, expiry_date: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-amber-500 focus:ring-4 focus:ring-amber-100"
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Manufactured date</span>
                  <input
                    type="date"
                    value={form.manufactured_date}
                    onChange={(event) => setForm((current) => ({ ...current, manufactured_date: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-amber-500 focus:ring-4 focus:ring-amber-100"
                  />
                </label>

                <label className="block md:col-span-2">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Batch number</span>
                  <input
                    value={form.batch_number}
                    onChange={(event) => setForm((current) => ({ ...current, batch_number: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-amber-500 focus:ring-4 focus:ring-amber-100"
                    placeholder="Batch code"
                  />
                </label>
              </section>

              {formError && <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</p>}

              <div className="flex flex-wrap items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={closeModal}
                  className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {saving ? "Saving..." : "Save product"}
                </button>
              </div>
            </form>
            </div>
          </div>
        </div>
      )}

      {movementOpen && movementProduct && (
        <div className="fixed inset-0 z-20 overflow-y-auto bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="mx-auto flex min-h-full w-full items-start justify-center">
            <div className="flex w-full max-w-2xl max-h-[92vh] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <div className="flex items-start justify-between gap-4 border-b border-stone-200 px-6 py-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Record movement</p>
                <h3 className="mt-2 text-2xl font-black tracking-tight text-stone-950">{movementProduct.name}</h3>
                <p className="mt-1 text-sm text-stone-600">
                  Unit {movementProduct.unit} · Threshold {movementProduct.low_stock_threshold}
                </p>
              </div>
              <button
                type="button"
                onClick={closeMovementModal}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
              >
                ×
              </button>
            </div>

            <div className="border-b border-stone-200 bg-stone-50 px-6 pt-4">
              <div className="inline-flex rounded-full border border-stone-200 bg-white p-1">
                {(["Stock-In", "Stock-Out"] as MovementTab[]).map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    onClick={() =>
                      setMovementForm((current) => ({
                        ...current,
                        type: tab,
                        unit_price: tab === "Stock-In" ? current.unit_price || String(movementProduct.unit_price) : current.unit_price,
                      }))
                    }
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      movementForm.type === tab ? "bg-stone-950 text-white" : "text-stone-600 hover:bg-stone-100"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

              <form className="grid gap-4 overflow-y-auto p-4 sm:p-6 md:grid-cols-2" onSubmit={submitMovement}>
              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Quantity</span>
                <input
                  type="number"
                  min="1"
                  value={movementForm.quantity}
                  onChange={(event) => setMovementForm((current) => ({ ...current, quantity: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Warehouse</span>
                <select
                  value={movementForm.warehouse_id}
                  onChange={(event) => setMovementForm((current) => ({ ...current, warehouse_id: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                >
                  <option value="">None</option>
                  {warehouses.map((warehouse) => (
                    <option key={warehouse.warehouse_id} value={warehouse.warehouse_id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
              </label>

              {movementForm.type === "Stock-In" ? (
                <label className="block">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Unit price</span>
                  <input
                    type="number"
                    step="0.01"
                    value={movementForm.unit_price}
                    onChange={(event) => setMovementForm((current) => ({ ...current, unit_price: event.target.value }))}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  />
                </label>
              ) : (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                  Stock-Out will use the existing product pricing and deduct stock only.
                </div>
              )}

              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Remarks</span>
                <textarea
                  value={movementForm.remarks}
                  onChange={(event) => setMovementForm((current) => ({ ...current, remarks: event.target.value }))}
                  className="min-h-28 w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="Optional context"
                />
              </label>

              {movementError && <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 md:col-span-2">{movementError}</p>}

              <div className="flex flex-wrap items-center justify-end gap-3 md:col-span-2">
                <button
                  type="button"
                  onClick={closeMovementModal}
                  className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={movementSaving}
                  className="rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {movementSaving ? "Saving..." : movementForm.type === "Stock-In" ? "Save stock-in" : "Save stock-out"}
                </button>
              </div>
            </form>
            </div>
          </div>
        </div>
      )}

      {deleteProductId && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white p-6 shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Delete product</p>
            <h3 className="mt-3 text-2xl font-black tracking-tight text-stone-950">Are you sure?</h3>
            <p className="mt-3 text-sm leading-6 text-stone-600">
              This will soft-delete the selected product. It will remain in the database for transaction history.
            </p>
            {formError && <p className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</p>}
            <div className="mt-6 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setDeleteProductId(null)}
                className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={deleteProduct}
                disabled={saving}
                className="rounded-full bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {saving ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
