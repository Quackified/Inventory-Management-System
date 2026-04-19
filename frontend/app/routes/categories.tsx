import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/categories";
import { api, getApiErrorMessage } from "../lib/api";
import { getRoleHomePath, getStoredToken, getStoredUser, hasRoleAccess, type AuthUser } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Categories - Warehouse/Store Management" },
    { name: "description", content: "Manage categories" },
  ];
}

type CategoryItem = {
  category_id: number;
  name: string;
  description: string | null;
};

type CategoryFormState = {
  name: string;
  description: string;
};

const defaultForm: CategoryFormState = {
  name: "",
  description: "",
};

export default function CategoriesRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());
  const [items, setItems] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [form, setForm] = useState<CategoryFormState>(defaultForm);

  const canManage = useMemo(() => {
    const role = user?.role ?? "";
    return role === "Admin" || role === "Manager";
  }, [user]);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    if (!hasRoleAccess(user?.role, ["Admin", "Manager"])) {
      navigate(getRoleHomePath(user?.role), { replace: true });
      return;
    }

    setLoading(true);
    api
      .get("/api/v1/categories")
      .then((response) => {
        setItems(response.data.items ?? []);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load categories."));
      })
      .finally(() => setLoading(false));
  }, [navigate, user]);

  function openCreate() {
    setEditingId(null);
    setForm(defaultForm);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(item: CategoryItem) {
    setEditingId(item.category_id);
    setForm({
      name: item.name,
      description: item.description ?? "",
    });
    setFormError(null);
    setModalOpen(true);
  }

  async function saveCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
    };

    try {
      if (editingId) {
        await api.put(`/api/v1/categories/${editingId}`, payload);
      } else {
        await api.post("/api/v1/categories", payload);
      }
      const refreshed = await api.get("/api/v1/categories");
      setItems(refreshed.data.items ?? []);
      setModalOpen(false);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Failed to save category."));
    } finally {
      setSaving(false);
    }
  }

  async function deleteCategory() {
    if (!deletingId) return;
    setSaving(true);
    setFormError(null);

    try {
      await api.delete(`/api/v1/categories/${deletingId}`);
      const refreshed = await api.get("/api/v1/categories");
      setItems(refreshed.data.items ?? []);
      setDeletingId(null);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Failed to delete category."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden text-stone-900">
      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] min-w-0 flex-col gap-4 px-3 py-4 sm:px-4 lg:px-6 lg:py-5">
        <header className="overflow-hidden rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_22px_70px_rgba(57,32,7,0.08)] backdrop-blur">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700">Warehouse/Store Management</p>
                <span className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-500">Categories</span>
              </div>
              <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Category Management</h1>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {canManage && <button type="button" onClick={openCreate} className="inline-flex items-center justify-center rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white">Add category</button>}
            </div>
          </div>
        </header>

        {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {formError && !modalOpen && !deletingId && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</div>}

        <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-stone-950 text-left text-[11px] uppercase tracking-[0.22em] text-stone-300">
                <tr>
                  <th className="px-5 py-4 font-semibold">Name</th>
                  <th className="px-5 py-4 font-semibold">Description</th>
                  <th className="px-5 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 bg-white">
                {items.map((item, index) => (
                  <tr key={item.category_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                    <td className="px-5 py-4 font-semibold text-stone-950">{item.name}</td>
                    <td className="px-5 py-4 text-stone-700">{item.description || "-"}</td>
                    <td className="px-5 py-4 text-right">
                      {canManage ? (
                        <div className="inline-flex items-center gap-2">
                          <button type="button" onClick={() => openEdit(item)} className="rounded-full border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700">Edit</button>
                          <button type="button" onClick={() => setDeletingId(item.category_id)} className="rounded-full border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-700">Delete</button>
                        </div>
                      ) : (
                        <span className="text-xs text-stone-400">Read only</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="border-t border-stone-200/80 px-5 py-4 text-sm text-stone-500">{loading ? "Loading..." : `${items.length} categories loaded`}</div>
        </section>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-xl overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <div className="flex items-center justify-between border-b border-stone-200 px-6 py-5">
              <h3 className="text-2xl font-black tracking-tight text-stone-950">{editingId ? "Edit category" : "Add category"}</h3>
              <button type="button" onClick={() => setModalOpen(false)} className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500">×</button>
            </div>
            <form className="grid gap-4 p-6" onSubmit={saveCategory}>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Name</span>
                <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Description</span>
                <textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} className="min-h-24 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
              </label>
              {formError && <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</p>}
              <div className="flex items-center justify-end gap-3">
                <button type="button" onClick={() => setModalOpen(false)} className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700">Cancel</button>
                <button type="submit" disabled={saving} className="rounded-full bg-stone-950 px-5 py-2.5 text-sm font-semibold text-white">{saving ? "Saving..." : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deletingId && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white p-6 shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <h3 className="text-2xl font-black tracking-tight text-stone-950">Delete category?</h3>
            <p className="mt-3 text-sm text-stone-600">This will remove the category record.</p>
            <div className="mt-6 flex items-center justify-end gap-3">
              <button type="button" onClick={() => setDeletingId(null)} className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700">Cancel</button>
              <button type="button" onClick={deleteCategory} disabled={saving} className="rounded-full bg-red-600 px-5 py-2.5 text-sm font-semibold text-white">{saving ? "Deleting..." : "Delete"}</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
