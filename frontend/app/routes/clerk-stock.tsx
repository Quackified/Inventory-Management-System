import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/clerk-stock";
import { api, getApiErrorMessage } from "../lib/api";
import { getRoleHomePath, getStoredToken, getStoredUser, type AuthUser } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Stock Flow - Warehouse/Store Management" },
    { name: "description", content: "Batch-aware stock-in and stock-out workflow" },
  ];
}

type ProductItem = {
  product_id: number;
  name: string;
  current_stock: number;
  unit: string;
  unit_price: number;
  low_stock_threshold: number;
  expiry_status: string;
};

type ProductListResponse = {
  items: ProductItem[];
  total: number;
};

type ProductBatchItem = {
  batch_id: number;
  batch_number: string;
  manufactured_date: string | null;
  expiry_date: string | null;
  expiry_status: string;
  quantity_on_hand: number;
};

type ProductBatchListResponse = {
  items: ProductBatchItem[];
};

type ExpiryActionItem = {
  batch_id: number;
  product_id: number;
  product_name: string;
  warehouse: string;
  batch_number: string;
  expiry_date: string | null;
  expiry_status: string;
  quantity_on_hand: number;
  days_overdue: number;
};

type ExpiryActionListResponse = {
  items: ExpiryActionItem[];
};

type AllocationPreviewItem = {
  batch_id: number;
  batch_number: string;
  quantity: number;
  available: number;
  expiry_date: string | null;
};

type MovementType = "Stock-In" | "Stock-Out";
type OperationalHealth = "Critical" | "Needs Attention" | "Low Stock" | "Active";
type StatusFilter = "All" | OperationalHealth;
type OrderBy = "Priority" | "NameAsc" | "StockAsc" | "StockDesc";

const PAGE_SIZE = 10;

function getOperationalHealth(
  product: ProductItem,
  hasExpiredBatch: boolean,
  hasQuarantinedBatch: boolean,
): OperationalHealth {
  if (hasExpiredBatch || product.expiry_status === "Expired") return "Critical";
  if (hasQuarantinedBatch || product.expiry_status === "Quarantined" || product.expiry_status === "At Risk" || product.expiry_status === "Disposed") {
    return "Needs Attention";
  }
  if (product.current_stock <= product.low_stock_threshold) return "Low Stock";
  return "Active";
}

function getHealthRank(health: OperationalHealth): number {
  if (health === "Critical") return 0;
  if (health === "Needs Attention") return 1;
  if (health === "Low Stock") return 2;
  return 3;
}

function getOperationalBadgeClasses(health: OperationalHealth) {
  if (health === "Critical") return "bg-[linear-gradient(135deg,#b91c1c,#ef4444)]";
  if (health === "Needs Attention") return "bg-[linear-gradient(135deg,#b45309,#f59e0b)]";
  if (health === "Low Stock") return "bg-[linear-gradient(135deg,#a16207,#d97706)]";
  return "bg-[linear-gradient(135deg,#047857,#10b981)]";
}

function shouldShowOperationalWarning(health: OperationalHealth) {
  return health !== "Active";
}

function getStatusBadgeClasses(status: string, isLowStock: boolean) {
  if (status === "Expired") return "bg-[linear-gradient(135deg,#b91c1c,#ef4444)]";
  if (status === "At Risk") return "bg-[linear-gradient(135deg,#b45309,#f59e0b)]";
  if (status === "Quarantined") return "bg-[linear-gradient(135deg,#334155,#475569)]";
  if (status === "Disposed") return "bg-[linear-gradient(135deg,#52525b,#3f3f46)]";
  if (isLowStock) return "bg-[linear-gradient(135deg,#a16207,#d97706)]";
  return "bg-[linear-gradient(135deg,#047857,#10b981)]";
}

function getStatusDisplay(status: string, isLowStock: boolean) {
  if (status === "Expired") return "Expired";
  if (status === "At Risk") return "At Risk";
  if (status === "Quarantined") return "Quarantined";
  if (status === "Disposed") return "Disposed";
  if (isLowStock) return "Low stock";
  return "Active";
}

function allocateFefo(quantity: number, batches: ProductBatchItem[]): AllocationPreviewItem[] {
  let remaining = quantity;
  const sorted = [...batches].sort((a, b) => {
    const left = a.expiry_date ?? "9999-12-31";
    const right = b.expiry_date ?? "9999-12-31";
    if (left !== right) return left.localeCompare(right);
    return a.batch_id - b.batch_id;
  });

  const allocations: AllocationPreviewItem[] = [];
  for (const batch of sorted) {
    if (remaining <= 0) break;
    const take = Math.min(batch.quantity_on_hand, remaining);
    if (take <= 0) continue;
    allocations.push({
      batch_id: batch.batch_id,
      batch_number: batch.batch_number,
      quantity: take,
      available: batch.quantity_on_hand,
      expiry_date: batch.expiry_date,
    });
    remaining -= take;
  }

  return allocations;
}

export default function ClerkStockRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("All");
  const [orderBy, setOrderBy] = useState<OrderBy>("Priority");
  const [currentPage, setCurrentPage] = useState(1);

  const [movementOpen, setMovementOpen] = useState(false);
  const [movementType, setMovementType] = useState<MovementType>("Stock-In");
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(null);
  const [quantity, setQuantity] = useState("1");
  const [remarks, setRemarks] = useState("");
  const [unitPrice, setUnitPrice] = useState("");
  const [batchNumber, setBatchNumber] = useState("");
  const [manufacturedDate, setManufacturedDate] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [batches, setBatches] = useState<ProductBatchItem[]>([]);
  const [expiryActions, setExpiryActions] = useState<ExpiryActionItem[]>([]);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchReviewOpen, setBatchReviewOpen] = useState(false);
  const [batchReviewLoading, setBatchReviewLoading] = useState(false);
  const [batchReviewProduct, setBatchReviewProduct] = useState<ProductItem | null>(null);
  const [batchReviewItems, setBatchReviewItems] = useState<ProductBatchItem[]>([]);
  const [expiryLoading, setExpiryLoading] = useState(false);
  const [expiryActionSavingId, setExpiryActionSavingId] = useState<number | null>(null);
  const [movementSaving, setMovementSaving] = useState(false);
  const [movementError, setMovementError] = useState<string | null>(null);

  const expiredBatchProductIds = useMemo(
    () => new Set(expiryActions.filter((item) => item.expiry_status === "Expired").map((item) => item.product_id)),
    [expiryActions],
  );

  const quarantinedBatchProductIds = useMemo(
    () => new Set(expiryActions.filter((item) => item.expiry_status === "Quarantined").map((item) => item.product_id)),
    [expiryActions],
  );

  const visibleProducts = useMemo(() => {
    const normalized = search.trim().toLowerCase();
    if (!normalized) return products;
    return products.filter((item) => item.name.toLowerCase().includes(normalized));
  }, [products, search]);

  const filteredProducts = useMemo(() => {
    if (statusFilter === "All") return visibleProducts;
    return visibleProducts.filter((item) =>
      getOperationalHealth(
        item,
        expiredBatchProductIds.has(item.product_id),
        quarantinedBatchProductIds.has(item.product_id),
      ) === statusFilter,
    );
  }, [visibleProducts, statusFilter, expiredBatchProductIds, quarantinedBatchProductIds]);

  const sortedProducts = useMemo(() => {
    const list = [...filteredProducts];
    if (orderBy === "NameAsc") {
      list.sort((a, b) => a.name.localeCompare(b.name));
      return list;
    }
    if (orderBy === "StockAsc") {
      list.sort((a, b) => a.current_stock - b.current_stock || a.name.localeCompare(b.name));
      return list;
    }
    if (orderBy === "StockDesc") {
      list.sort((a, b) => b.current_stock - a.current_stock || a.name.localeCompare(b.name));
      return list;
    }

    list.sort((a, b) => {
      const rankDiff = getHealthRank(
        getOperationalHealth(
          a,
          expiredBatchProductIds.has(a.product_id),
          quarantinedBatchProductIds.has(a.product_id),
        ),
      ) - getHealthRank(
        getOperationalHealth(
          b,
          expiredBatchProductIds.has(b.product_id),
          quarantinedBatchProductIds.has(b.product_id),
        ),
      );
      if (rankDiff !== 0) return rankDiff;
      return a.name.localeCompare(b.name);
    });
    return list;
  }, [filteredProducts, orderBy, expiredBatchProductIds, quarantinedBatchProductIds]);

  const totalPages = Math.max(1, Math.ceil(sortedProducts.length / PAGE_SIZE));

  const pagedProducts = useMemo(() => {
    const safePage = Math.min(currentPage, totalPages);
    const start = (safePage - 1) * PAGE_SIZE;
    return sortedProducts.slice(start, start + PAGE_SIZE);
  }, [sortedProducts, currentPage, totalPages]);

  const lowStockCount = useMemo(
    () => products.filter((item) =>
      getOperationalHealth(
        item,
        expiredBatchProductIds.has(item.product_id),
        quarantinedBatchProductIds.has(item.product_id),
      ) === "Low Stock").length,
    [products, expiredBatchProductIds, quarantinedBatchProductIds],
  );
  const expiredProductCount = useMemo(
    () => products.filter((item) =>
      getOperationalHealth(
        item,
        expiredBatchProductIds.has(item.product_id),
        quarantinedBatchProductIds.has(item.product_id),
      ) === "Critical").length,
    [products, expiredBatchProductIds, quarantinedBatchProductIds],
  );

  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter, orderBy]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const stockOutQuantity = Number(quantity);
  const previewAllocations = useMemo(() => {
    if (movementType !== "Stock-Out") return [];
    if (!Number.isFinite(stockOutQuantity) || stockOutQuantity <= 0) return [];
    return allocateFefo(stockOutQuantity, batches);
  }, [batches, movementType, stockOutQuantity]);

  const previewAllocatedTotal = useMemo(
    () => previewAllocations.reduce((sum, row) => sum + row.quantity, 0),
    [previewAllocations],
  );

  useEffect(() => {
    const token = getStoredToken();
    const currentUser = getStoredUser();

    if (!token || !currentUser) {
      navigate("/login", { replace: true });
      return;
    }

    setUser(currentUser);
    if (!getStoredUser() || !["Admin", "Manager", "Clerk"].includes(currentUser.role)) {
      navigate(getRoleHomePath(currentUser.role), { replace: true });
      return;
    }

    setLoading(true);
    setExpiryLoading(true);
    Promise.all([
      api.get("/api/v1/products", { params: { page: 1, page_size: 100 } }),
      api.get("/api/v1/products/batches/expiry-actions"),
    ])
      .then(([productsResponse, expiryResponse]) => {
        setProducts((productsResponse.data as ProductListResponse).items ?? []);
        setExpiryActions((expiryResponse.data as ExpiryActionListResponse).items ?? []);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load stock flow data."));
      })
      .finally(() => {
        setLoading(false);
        setExpiryLoading(false);
      });
  }, [navigate]);

  function closeMovement() {
    setMovementOpen(false);
    setSelectedProduct(null);
    setQuantity("1");
    setRemarks("");
    setUnitPrice("");
    setBatchNumber("");
    setManufacturedDate("");
    setExpiryDate("");
    setBatches([]);
    setBatchLoading(false);
    setMovementError(null);
  }

  async function openMovement(product: ProductItem, type: MovementType) {
    setSelectedProduct(product);
    setMovementType(type);
    setQuantity("1");
    setRemarks("");
    setUnitPrice(String(product.unit_price));
    setBatchNumber("");
    setManufacturedDate("");
    setExpiryDate("");
    setMovementError(null);
    setMovementOpen(true);

    if (type === "Stock-Out") {
      setBatchLoading(true);
      try {
        const response = await api.get(`/api/v1/products/${product.product_id}/batches`, {
          params: { only_available: true },
        });
        setBatches((response.data as ProductBatchListResponse).items ?? []);
      } catch (requestError) {
        setMovementError(getApiErrorMessage(requestError, "Failed to load batches for FEFO."));
      } finally {
        setBatchLoading(false);
      }
    }
  }

  async function refreshProducts() {
    const response = await api.get("/api/v1/products", { params: { page: 1, page_size: 100 } });
    setProducts((response.data as ProductListResponse).items ?? []);
  }

  async function refreshExpiryActions() {
    const response = await api.get("/api/v1/products/batches/expiry-actions");
    setExpiryActions((response.data as ExpiryActionListResponse).items ?? []);
  }

  async function loadProductBatches(productId: number) {
    const response = await api.get(`/api/v1/products/${productId}/batches`, {
      params: { only_available: false },
    });
    return (response.data as ProductBatchListResponse).items ?? [];
  }

  async function openBatchReview(product: ProductItem) {
    setBatchReviewProduct(product);
    setBatchReviewOpen(true);
    setBatchReviewLoading(true);
    try {
      const items = await loadProductBatches(product.product_id);
      setBatchReviewItems(items);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Failed to load product batches."));
    } finally {
      setBatchReviewLoading(false);
    }
  }

  async function refreshBatchReviewItems() {
    if (!batchReviewProduct) return;
    const items = await loadProductBatches(batchReviewProduct.product_id);
    setBatchReviewItems(items);
  }

  async function executeBatchAction(batchId: number, action: "Quarantine" | "Dispose", remarks: string | null) {
    await api.post(`/api/v1/products/batches/${batchId}/action`, {
      action,
      remarks,
    });
  }

  async function submitMovement(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedProduct) return;

    if (!Number.isFinite(Number(selectedProduct.product_id)) || Number(selectedProduct.product_id) <= 0) {
      setMovementError("Selected product is invalid. Please refresh and try again.");
      return;
    }

    const parsedQuantity = Number(quantity);
    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      setMovementError("Quantity must be greater than zero.");
      return;
    }

    if (movementType === "Stock-In" && !batchNumber.trim()) {
      setMovementError("Batch number is required for Clerk stock-in.");
      return;
    }

    if (
      movementType === "Stock-In" &&
      manufacturedDate &&
      expiryDate &&
      new Date(expiryDate).getTime() < new Date(manufacturedDate).getTime()
    ) {
      setMovementError("Expiry date cannot be earlier than manufactured date.");
      return;
    }

    const parsedUnitPrice = Number(unitPrice);
    if (movementType === "Stock-In" && (!Number.isFinite(parsedUnitPrice) || parsedUnitPrice < 0)) {
      setMovementError("Unit price must be a valid non-negative number.");
      return;
    }

    if (movementType === "Stock-Out" && previewAllocatedTotal < parsedQuantity) {
      setMovementError("Not enough non-expired batch stock available to satisfy this stock-out.");
      return;
    }

    setMovementSaving(true);
    setMovementError(null);

    const payload: Record<string, unknown> = {
      product_id: selectedProduct.product_id,
      type: movementType,
      quantity: parsedQuantity,
      remarks: remarks.trim() || null,
      unit_price: movementType === "Stock-In" ? parsedUnitPrice : null,
    };

    if (movementType === "Stock-In") {
      payload.batch_number = batchNumber.trim();
      payload.manufactured_date = manufacturedDate || null;
      payload.expiry_date = expiryDate || null;
    } else {
      payload.allocations = previewAllocations.map((row) => ({
        batch_id: row.batch_id,
        quantity: row.quantity,
      }));
    }

    try {
      await api.post("/api/v1/transactions", payload);
      await Promise.all([refreshProducts(), refreshExpiryActions()]);
      closeMovement();
    } catch (requestError) {
      setMovementError(getApiErrorMessage(requestError, "Failed to record movement."));
    } finally {
      setMovementSaving(false);
    }
  }

  async function handleExpiryAction(item: ExpiryActionItem, action: "Quarantine" | "Dispose") {
    if (action === "Dispose") {
      const disposeConfirm = window.prompt(`Type DISPOSE to confirm disposal of batch ${item.batch_number}.`, "");
      if ((disposeConfirm ?? "").trim().toUpperCase() !== "DISPOSE") {
        return;
      }
    }

    const promptText = action === "Dispose"
      ? `Dispose batch ${item.batch_number}? This removes ${item.quantity_on_hand} unit(s) from stock. Enter remarks (optional):`
      : `Quarantine batch ${item.batch_number}. Enter remarks (optional):`;
    const remarksInput = window.prompt(promptText, "") ?? "";

    setExpiryActionSavingId(item.batch_id);
    setError(null);
    try {
      await executeBatchAction(item.batch_id, action, remarksInput.trim() || null);
      await Promise.all([refreshProducts(), refreshExpiryActions(), refreshBatchReviewItems()]);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, `Failed to ${action.toLowerCase()} batch.`));
    } finally {
      setExpiryActionSavingId(null);
    }
  }

  async function handleBatchReviewAction(batch: ProductBatchItem, action: "Quarantine" | "Dispose") {
    if (action === "Dispose") {
      const disposeConfirm = window.prompt(`Type DISPOSE to confirm disposal of batch ${batch.batch_number}.`, "");
      if ((disposeConfirm ?? "").trim().toUpperCase() !== "DISPOSE") {
        return;
      }
    }

    const promptText = action === "Dispose"
      ? `Dispose batch ${batch.batch_number}? This removes ${batch.quantity_on_hand} unit(s) from stock. Enter remarks (optional):`
      : `Quarantine batch ${batch.batch_number}. Enter remarks (optional):`;
    const remarksInput = window.prompt(promptText, "") ?? "";

    setExpiryActionSavingId(batch.batch_id);
    setError(null);
    try {
      await executeBatchAction(batch.batch_id, action, remarksInput.trim() || null);
      await Promise.all([refreshProducts(), refreshExpiryActions(), refreshBatchReviewItems()]);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, `Failed to ${action.toLowerCase()} batch.`));
    } finally {
      setExpiryActionSavingId(null);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden text-stone-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-7rem] top-[-6rem] h-80 w-80 rounded-full bg-emerald-300/32 blur-3xl" />
        <div className="absolute right-[-8rem] top-[8rem] h-96 w-96 rounded-full bg-teal-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] min-w-0 flex-col gap-4 px-3 py-4 sm:px-4 lg:px-6 lg:py-5">
        <header className="overflow-hidden rounded-2xl border border-white/60 bg-white/72 px-4 py-3 shadow-[0_22px_70px_rgba(16,185,129,0.08)] backdrop-blur-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700">{user?.role ?? "User"} Workspace</p>
          <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Stock In / Stock Out Flow</h1>
          <p className="mt-2 text-sm text-stone-600">
            Batch-aware flow with FEFO allocation preview for outgoing stock.
          </p>
        </header>

        {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="grid grid-cols-2 gap-2 lg:grid-cols-4">
          <article className="relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br from-stone-900 via-stone-800 to-stone-700 px-3 py-2.5 text-white">
            <p className="truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">Products</p>
            <h2 className="mt-1.5 truncate text-xl font-black tracking-tight lg:text-2xl">{products.length}</h2>
          </article>
          <article className="relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br from-emerald-700 via-emerald-600 to-teal-500 px-3 py-2.5 text-white">
            <p className="truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">Low Stock</p>
            <h2 className="mt-1.5 truncate text-xl font-black tracking-tight lg:text-2xl">{lowStockCount}</h2>
          </article>
          <article className="relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br from-red-700 via-red-600 to-orange-500 px-3 py-2.5 text-white">
            <p className="truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">Expired Products</p>
            <h2 className="mt-1.5 truncate text-xl font-black tracking-tight lg:text-2xl">{expiredProductCount}</h2>
          </article>
          <article className="relative min-w-0 overflow-hidden rounded-xl border border-white/25 bg-gradient-to-br from-emerald-900 via-emerald-800 to-emerald-600 px-3 py-2.5 text-white">
            <p className="truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/80">Signed in</p>
            <h2 className="mt-1.5 truncate text-lg font-black tracking-tight lg:text-xl">{user?.username ?? "clerk"}</h2>
          </article>
        </section>

        <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
          <div className="flex flex-col gap-4 border-b border-emerald-100/80 p-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-emerald-700">Operational list</p>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Pick a product to move</h2>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <label className="flex min-w-[260px] items-center gap-3 rounded-full border border-emerald-200 bg-white/90 px-4 py-2.5 shadow-sm">
                <span className="text-sm text-emerald-500">⌕</span>
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  className="w-full bg-transparent text-sm outline-none placeholder:text-stone-400"
                  placeholder="Search product"
                />
              </label>
              <label className="flex items-center gap-2 rounded-full border border-emerald-200 bg-white/90 px-3 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-800">
                <span>Status</span>
                <select
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
                  className="rounded-full border border-emerald-200 bg-white px-2 py-1 text-[11px] font-semibold text-emerald-900 outline-none"
                >
                  <option value="All">All</option>
                  <option value="Critical">Critical</option>
                  <option value="Needs Attention">Needs Attention</option>
                  <option value="Low Stock">Low Stock</option>
                  <option value="Active">Active</option>
                </select>
              </label>
              <label className="flex items-center gap-2 rounded-full border border-emerald-200 bg-white/90 px-3 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-800">
                <span>Order by</span>
                <select
                  value={orderBy}
                  onChange={(event) => setOrderBy(event.target.value as OrderBy)}
                  className="rounded-full border border-emerald-200 bg-white px-2 py-1 text-[11px] font-semibold text-emerald-900 outline-none"
                >
                  <option value="Priority">Priority</option>
                  <option value="NameAsc">Name A-Z</option>
                  <option value="StockAsc">Stock low-high</option>
                  <option value="StockDesc">Stock high-low</option>
                </select>
              </label>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-[linear-gradient(135deg,#064e3b,#0f766e)] text-left text-[11px] uppercase tracking-[0.22em] text-emerald-50/85">
                <tr>
                  <th className="px-5 py-4 font-semibold">Product</th>
                  <th className="px-5 py-4 font-semibold">Stock</th>
                  <th className="px-5 py-4 font-semibold">Threshold</th>
                  <th className="px-5 py-4 font-semibold">Unit</th>
                  <th className="px-5 py-4 font-semibold">Status</th>
                  <th className="px-5 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 bg-white">
                {pagedProducts.map((product, index) => {
                  const health = getOperationalHealth(
                    product,
                    expiredBatchProductIds.has(product.product_id),
                    quarantinedBatchProductIds.has(product.product_id),
                  );
                  return (
                  <tr key={product.product_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                    <td className="px-5 py-4 font-semibold text-stone-950">{product.name}</td>
                    <td className="px-5 py-4 text-stone-700">{product.current_stock}</td>
                    <td className="px-5 py-4 text-stone-700">{product.low_stock_threshold}</td>
                    <td className="px-5 py-4 text-stone-700">{product.unit}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-between gap-2">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${
                          getOperationalBadgeClasses(health)
                        }`}
                      >
                        {health}
                      </span>
                      {shouldShowOperationalWarning(health) && (
                        <span
                          className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-amber-300 bg-amber-100 text-xs font-black text-amber-700"
                          title="Needs attention"
                          aria-label="Needs attention"
                        >
                          !
                        </span>
                      )}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="inline-flex gap-2">
                        <button
                          type="button"
                          onClick={() => openBatchReview(product)}
                          className="rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-xs font-semibold text-amber-800 transition hover:bg-amber-100"
                        >
                          Batches
                        </button>
                        <button
                          type="button"
                          onClick={() => openMovement(product, "Stock-In")}
                          className="rounded-full border border-emerald-200 bg-white px-4 py-2 text-xs font-semibold text-emerald-800 transition hover:bg-emerald-50"
                        >
                          Stock-In
                        </button>
                        <button
                          type="button"
                          onClick={() => openMovement(product, "Stock-Out")}
                          className="rounded-full border border-stone-200 bg-stone-900 px-4 py-2 text-xs font-semibold text-white transition hover:bg-stone-800"
                        >
                          Stock-Out
                        </button>
                      </div>
                    </td>
                  </tr>
                );})}
                {!loading && pagedProducts.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-5 py-8 text-center text-sm text-stone-500">
                      No products found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 border-t border-emerald-100/80 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-stone-500">
              Showing {(sortedProducts.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1)}-
              {Math.min(currentPage * PAGE_SIZE, sortedProducts.length)} of {sortedProducts.length}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                disabled={currentPage <= 1}
                className="rounded-full border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Prev
              </button>
              <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800">
                Page {currentPage} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                disabled={currentPage >= totalPages}
                className="rounded-full border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </section>

        <section className="overflow-hidden rounded-[2rem] border border-amber-100 bg-white/82 shadow-[0_20px_60px_rgba(180,83,9,0.08)] backdrop-blur-xl">
          <div className="flex flex-col gap-2 border-b border-amber-100 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-amber-700">Expiry actions</p>
            <h2 className="text-2xl font-black tracking-tight text-stone-950">Quarantine or dispose expired stock</h2>
            <p className="text-sm text-stone-600">
              Use quarantine for hold/review. Use dispose to remove unusable units from inventory and log stock-out audit.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-[linear-gradient(135deg,#78350f,#b45309)] text-left text-[11px] uppercase tracking-[0.22em] text-amber-50/90">
                <tr>
                  <th className="px-5 py-4 font-semibold">Product</th>
                  <th className="px-5 py-4 font-semibold">Batch</th>
                  <th className="px-5 py-4 font-semibold">Expiry</th>
                  <th className="px-5 py-4 font-semibold">Qty</th>
                  <th className="px-5 py-4 font-semibold">Status</th>
                  <th className="px-5 py-4 font-semibold">Warehouse</th>
                  <th className="px-5 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 bg-white">
                {expiryActions.map((item, index) => {
                  const isSaving = expiryActionSavingId === item.batch_id;
                  return (
                    <tr key={item.batch_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                      <td className="px-5 py-4 font-semibold text-stone-950">{item.product_name}</td>
                      <td className="px-5 py-4 text-stone-700">{item.batch_number}</td>
                      <td className="px-5 py-4 text-stone-700">{item.expiry_date ?? "N/A"}</td>
                      <td className="px-5 py-4 text-stone-700">{item.quantity_on_hand}</td>
                      <td className="px-5 py-4">
                        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${
                          getStatusBadgeClasses(item.expiry_status, false)
                        }`}>
                          {getStatusDisplay(item.expiry_status, false)}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-stone-700">{item.warehouse}</td>
                      <td className="px-5 py-4 text-right">
                        <div className="inline-flex gap-2">
                          <button
                            type="button"
                            disabled={isSaving || item.expiry_status === "Quarantined"}
                            onClick={() => handleExpiryAction(item, "Quarantine")}
                            className="rounded-full border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {isSaving ? "Saving..." : "Quarantine"}
                          </button>
                          <button
                            type="button"
                            disabled={isSaving}
                            onClick={() => handleExpiryAction(item, "Dispose")}
                            className="rounded-full border border-red-200 bg-red-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {isSaving ? "Saving..." : "Dispose"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}

                {!expiryLoading && expiryActions.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-5 py-8 text-center text-sm text-stone-500">
                      No expired or quarantined batches need action.
                    </td>
                  </tr>
                )}

                {expiryLoading && (
                  <tr>
                    <td colSpan={7} className="px-5 py-8 text-center text-sm text-stone-500">
                      Loading expiry queue...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {movementOpen && selectedProduct && (
        <div className="fixed inset-0 z-20 overflow-y-auto bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="mx-auto flex min-h-full w-full items-start justify-center">
            <div className="flex w-full max-w-3xl max-h-[92vh] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
              <div className="flex items-start justify-between gap-4 border-b border-stone-200 px-6 py-5">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">{movementType}</p>
                  <h3 className="mt-2 text-2xl font-black tracking-tight text-stone-950">{selectedProduct.name}</h3>
                  <p className="mt-1 text-sm text-stone-600">Current stock: {selectedProduct.current_stock} {selectedProduct.unit}</p>
                </div>
                <button
                  type="button"
                  onClick={closeMovement}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                >
                  ×
                </button>
              </div>

              <form className="grid gap-4 overflow-y-auto p-4 sm:p-6 md:grid-cols-2" onSubmit={submitMovement}>
                <label className="block md:col-span-2">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Quantity</span>
                  <input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(event) => setQuantity(event.target.value)}
                    className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  />
                </label>

                {movementType === "Stock-In" ? (
                  <>
                    <label className="block">
                      <span className="mb-2 block text-sm font-semibold text-stone-700">Batch number</span>
                      <input
                        value={batchNumber}
                        onChange={(event) => setBatchNumber(event.target.value)}
                        className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                        placeholder="Required for clerk flow"
                      />
                    </label>

                    <label className="block">
                      <span className="mb-2 block text-sm font-semibold text-stone-700">Unit price</span>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={unitPrice}
                        onChange={(event) => setUnitPrice(event.target.value)}
                        className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                      />
                    </label>

                    <label className="block">
                      <span className="mb-2 block text-sm font-semibold text-stone-700">Manufactured date</span>
                      <input
                        type="date"
                        value={manufacturedDate}
                        onChange={(event) => setManufacturedDate(event.target.value)}
                        className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                      />
                    </label>

                    <label className="block">
                      <span className="mb-2 block text-sm font-semibold text-stone-700">Expiry date</span>
                      <input
                        type="date"
                        value={expiryDate}
                        onChange={(event) => setExpiryDate(event.target.value)}
                        className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-amber-500 focus:ring-4 focus:ring-amber-100"
                      />
                    </label>
                  </>
                ) : (
                  <div className="md:col-span-2 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                    <p className="font-semibold">FEFO Allocation Preview</p>
                    {batchLoading ? (
                      <p className="mt-2">Loading available batches...</p>
                    ) : previewAllocations.length === 0 ? (
                      <p className="mt-2">No eligible non-expired batches available.</p>
                    ) : (
                      <div className="mt-3 overflow-x-auto">
                        <table className="min-w-full text-xs">
                          <thead className="text-left uppercase tracking-[0.14em] text-amber-800/70">
                            <tr>
                              <th className="py-1 pr-4">Batch</th>
                              <th className="py-1 pr-4">Expiry</th>
                              <th className="py-1 pr-4">Available</th>
                              <th className="py-1">Will consume</th>
                            </tr>
                          </thead>
                          <tbody>
                            {previewAllocations.map((row) => (
                              <tr key={row.batch_id}>
                                <td className="py-1 pr-4 font-semibold">{row.batch_number}</td>
                                <td className="py-1 pr-4">{row.expiry_date ?? "N/A"}</td>
                                <td className="py-1 pr-4">{row.available}</td>
                                <td className="py-1">{row.quantity}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    <p className="mt-3 text-xs">
                      Requested: {Number.isFinite(stockOutQuantity) ? stockOutQuantity : 0} • Allocated: {previewAllocatedTotal}
                    </p>
                  </div>
                )}

                <label className="block md:col-span-2">
                  <span className="mb-2 block text-sm font-semibold text-stone-700">Remarks</span>
                  <textarea
                    value={remarks}
                    onChange={(event) => setRemarks(event.target.value)}
                    className="min-h-24 w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                    placeholder="Optional context"
                  />
                </label>

                {movementError && <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 md:col-span-2">{movementError}</p>}

                <div className="flex flex-wrap items-center justify-end gap-3 md:col-span-2">
                  <button
                    type="button"
                    onClick={closeMovement}
                    className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={movementSaving}
                    className="rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {movementSaving ? "Saving..." : movementType === "Stock-In" ? "Save stock-in" : "Save stock-out"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {batchReviewOpen && batchReviewProduct && (
        <div className="fixed inset-0 z-20 overflow-y-auto bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="mx-auto flex min-h-full w-full items-start justify-center">
            <div className="flex w-full max-w-4xl max-h-[92vh] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
              <div className="flex items-start justify-between gap-4 border-b border-stone-200 px-6 py-5">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Batch review</p>
                  <h3 className="mt-2 text-2xl font-black tracking-tight text-stone-950">{batchReviewProduct.name}</h3>
                  <p className="mt-1 text-sm text-stone-600">Quarantine or dispose batches from this product.</p>
                </div>
                <button
                  type="button"
                  onClick={() => setBatchReviewOpen(false)}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:bg-stone-50 hover:text-stone-800"
                >
                  ×
                </button>
              </div>

              <div className="overflow-x-auto p-4 sm:p-6">
                <table className="min-w-full text-sm">
                  <thead className="bg-[linear-gradient(135deg,#374151,#111827)] text-left text-[11px] uppercase tracking-[0.22em] text-stone-100/90">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Batch</th>
                      <th className="px-4 py-3 font-semibold">Mfg</th>
                      <th className="px-4 py-3 font-semibold">Expiry</th>
                      <th className="px-4 py-3 font-semibold">Qty</th>
                      <th className="px-4 py-3 font-semibold">Status</th>
                      <th className="px-4 py-3 font-semibold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 bg-white">
                    {batchReviewItems.map((batch, index) => {
                      const isSaving = expiryActionSavingId === batch.batch_id;
                      return (
                        <tr key={batch.batch_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                          <td className="px-4 py-3 font-semibold text-stone-950">{batch.batch_number}</td>
                          <td className="px-4 py-3 text-stone-700">{batch.manufactured_date ?? "N/A"}</td>
                          <td className="px-4 py-3 text-stone-700">{batch.expiry_date ?? "N/A"}</td>
                          <td className="px-4 py-3 text-stone-700">{batch.quantity_on_hand}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${
                              getStatusBadgeClasses(batch.expiry_status, false)
                            }`}>
                              {getStatusDisplay(batch.expiry_status, false)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="inline-flex gap-2">
                              <button
                                type="button"
                                disabled={isSaving || batch.expiry_status === "Disposed" || batch.expiry_status === "Quarantined"}
                                onClick={() => handleBatchReviewAction(batch, "Quarantine")}
                                className="rounded-full border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {isSaving ? "Saving..." : "Quarantine"}
                              </button>
                              <button
                                type="button"
                                disabled={isSaving || batch.expiry_status === "Disposed" || batch.quantity_on_hand <= 0}
                                onClick={() => handleBatchReviewAction(batch, "Dispose")}
                                className="rounded-full border border-red-200 bg-red-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {isSaving ? "Saving..." : "Dispose"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}

                    {!batchReviewLoading && batchReviewItems.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-sm text-stone-500">
                          No batches found for this product yet. Do a Stock-In with batch number first.
                        </td>
                      </tr>
                    )}

                    {batchReviewLoading && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-sm text-stone-500">
                          Loading batches...
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
