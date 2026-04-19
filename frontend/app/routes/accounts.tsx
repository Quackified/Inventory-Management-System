import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/accounts";
import { api, getApiErrorMessage } from "../lib/api";
import { getImageUrl } from "../lib/urlUtils";

import { getRoleHomePath, getStoredToken, getStoredUser, hasRoleAccess, type AuthUser } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Accounts - Warehouse/Store Management" },
    { name: "description", content: "Admin account management" },
  ];
}

type AccountItem = {
  user_id: number;
  username: string;
  full_name: string;
  role: "Admin" | "Manager" | "Clerk";
  email: string | null;
  profile_image_url: string | null;
  assigned_warehouse_id: number | null;
  assigned_warehouse_name: string | null;
  is_active: number;
};

type WarehouseItem = {
  warehouse_id: number;
  name: string;
};

type AccountFormState = {
  username: string;
  full_name: string;
  role: "Admin" | "Manager" | "Clerk";
  email: string;
  profile_image_url: string;
  assigned_warehouse_id: string;
  is_active: "0" | "1";
  password: string;
};

const defaultForm: AccountFormState = {
  username: "",
  full_name: "",
  role: "Clerk",
  email: "",
  profile_image_url: "",
  assigned_warehouse_id: "",
  is_active: "1",
  password: "",
};

export default function AccountsRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());
  const [items, setItems] = useState<AccountItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [form, setForm] = useState<AccountFormState>(defaultForm);
  const [warehouses, setWarehouses] = useState<WarehouseItem[]>([]);
  const [warehouseFilter, setWarehouseFilter] = useState<string>("");
  const [migrationStatus, setMigrationStatus] = useState<{
    remaining_legacy_passwords: number;
    is_fully_migrated: boolean;
  } | null>(null);

  const isAdmin = user?.role === "Admin";

  const filteredItems = useMemo(() => {
    if (!warehouseFilter) {
      return items;
    }
    return items.filter((item) => String(item.assigned_warehouse_id ?? "") === warehouseFilter);
  }, [items, warehouseFilter]);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    if (!hasRoleAccess(user?.role, ["Admin"])) {
      navigate(getRoleHomePath(user?.role), { replace: true });
      return;
    }

    setLoading(true);
    api
      .get("/api/v1/accounts")
      .then((response) => {
        setItems(response.data.items ?? []);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load accounts."));
      })
      .finally(() => setLoading(false));

    api
      .get("/api/v1/auth/migration-status")
      .then((response) => {
        setMigrationStatus({
          remaining_legacy_passwords: response.data.remaining_legacy_passwords ?? 0,
          is_fully_migrated: Boolean(response.data.is_fully_migrated),
        });
      })
      .catch(() => {
        setMigrationStatus(null);
      });

    api
      .get("/api/v1/warehouses")
      .then((response) => {
        setWarehouses(response.data.items ?? []);
      })
      .catch(() => {
        setWarehouses([]);
      });
  }, [navigate, isAdmin]);

  function openCreate() {
    setEditingId(null);
    setForm(defaultForm);
    setAvatarFile(null);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(item: AccountItem) {
    setEditingId(item.user_id);
    setForm({
      username: item.username,
      full_name: item.full_name,
      role: item.role,
      email: item.email ?? "",
      profile_image_url: item.profile_image_url ?? "",
      assigned_warehouse_id: item.assigned_warehouse_id ? String(item.assigned_warehouse_id) : "",
      is_active: item.is_active === 1 ? "1" : "0",
      password: "",
    });
    setAvatarFile(null);
    setFormError(null);
    setModalOpen(true);
  }

  async function uploadAvatar(file: File, targetUserId: number | null) {
    const avatarData = new FormData();
    avatarData.append("file", file);
    if (targetUserId) {
      avatarData.append("user_id", String(targetUserId));
    }

    const response = await api.post("/api/v1/auth/avatar", avatarData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return String(response.data.profile_image_url ?? "");
  }

  async function saveAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);

    try {
      let profileImageUrl = form.profile_image_url.trim() || null;
      if (avatarFile) {
        profileImageUrl = await uploadAvatar(avatarFile, editingId);
      }

      const basePayload = {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        role: form.role,
        email: form.email.trim() || null,
        profile_image_url: profileImageUrl,
        assigned_warehouse_id: form.assigned_warehouse_id ? Number(form.assigned_warehouse_id) : null,
        is_active: Number(form.is_active),
      };

      if (editingId) {
        await api.put(`/api/v1/accounts/${editingId}`, {
          ...basePayload,
          password: form.password.trim() || null,
        });
      } else {
        await api.post("/api/v1/accounts", {
          ...basePayload,
          password: form.password,
        });
      }
      const refreshed = await api.get("/api/v1/accounts");
      setItems(refreshed.data.items ?? []);
      setModalOpen(false);
      setAvatarFile(null);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Failed to save account."));
    } finally {
      setSaving(false);
    }
  }

  async function deleteAccount() {
    if (!deletingId) return;
    setSaving(true);
    setFormError(null);

    try {
      await api.delete(`/api/v1/accounts/${deletingId}`);
      const refreshed = await api.get("/api/v1/accounts");
      setItems(refreshed.data.items ?? []);
      setDeletingId(null);
    } catch (requestError) {
      setFormError(getApiErrorMessage(requestError, "Failed to delete account."));
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
                <span className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-500">Accounts</span>
              </div>
              <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">Account Administration</h1>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {isAdmin && <button type="button" onClick={openCreate} className="inline-flex items-center justify-center rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white">Add account</button>}
            </div>
          </div>
        </header>

        {!isAdmin ? (
          <section className="rounded-[2rem] border border-white/70 bg-white/82 p-8 text-center shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">Access restricted</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-stone-950">Only Admin can manage accounts.</h2>
          </section>
        ) : (
          <>
            {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
            {formError && !modalOpen && !deletingId && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</div>}

            <section className="rounded-[2rem] border border-white/70 bg-white/82 p-5 shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Password migration</p>
                  <p className="mt-1 text-sm text-stone-700">
                    {migrationStatus
                      ? migrationStatus.is_fully_migrated
                        ? "All account passwords are fully migrated"
                        : `${migrationStatus.remaining_legacy_passwords} legacy password value(s) remaining`
                      : "Migration status unavailable"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-[0.2em] text-stone-500">Warehouse</span>
                  <select
                    value={warehouseFilter}
                    onChange={(event) => setWarehouseFilter(event.target.value)}
                    className="rounded-full border border-stone-200 bg-white px-4 py-2 text-sm text-stone-800"
                  >
                    <option value="">All</option>
                    {warehouses.map((warehouse) => (
                      <option key={warehouse.warehouse_id} value={warehouse.warehouse_id}>
                        {warehouse.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(57,32,7,0.08)] backdrop-blur">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-stone-950 text-left text-[11px] uppercase tracking-[0.22em] text-stone-300">
                    <tr>
                      <th className="px-5 py-4 font-semibold">Avatar</th>
                      <th className="px-5 py-4 font-semibold">Username</th>
                      <th className="px-5 py-4 font-semibold">Full name</th>
                      <th className="px-5 py-4 font-semibold">Role</th>
                      <th className="px-5 py-4 font-semibold">Email</th>
                      <th className="px-5 py-4 font-semibold">Warehouse</th>
                      <th className="px-5 py-4 font-semibold">Status</th>
                      <th className="px-5 py-4 font-semibold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100 bg-white">
                    {filteredItems.map((item, index) => (
                      <tr key={item.user_id} className={index % 2 === 0 ? "bg-white" : "bg-stone-50/50"}>
                        <td className="px-5 py-4">
                          {item.profile_image_url ? (
                            <img src={getImageUrl(item.profile_image_url)} alt={`${item.username} avatar`} className="h-9 w-9 rounded-full border border-stone-200 object-cover" />
                          ) : (
                            <div className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-stone-200 bg-stone-100 text-xs font-bold text-stone-700">
                              {(item.full_name || item.username || "U").trim().charAt(0).toUpperCase()}
                            </div>
                          )}
                        </td>
                        <td className="px-5 py-4 font-semibold text-stone-950">{item.username}</td>
                        <td className="px-5 py-4 text-stone-700">{item.full_name}</td>
                        <td className="px-5 py-4 text-stone-700">{item.role}</td>
                        <td className="px-5 py-4 text-stone-700">{item.email || "-"}</td>
                        <td className="px-5 py-4 text-stone-700">{item.assigned_warehouse_name || "-"}</td>
                        <td className="px-5 py-4">
                          <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white ${item.is_active ? "bg-emerald-700" : "bg-stone-500"}`}>
                            {item.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-right">
                          <div className="inline-flex items-center gap-2">
                            <button type="button" onClick={() => openEdit(item)} className="rounded-full border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700">Edit</button>
                            <button type="button" onClick={() => setDeletingId(item.user_id)} className="rounded-full border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-700">Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="border-t border-stone-200/80 px-5 py-4 text-sm text-stone-500">{loading ? "Loading..." : `${filteredItems.length} of ${items.length} accounts loaded`}</div>
            </section>
          </>
        )}
      </div>

      {modalOpen && isAdmin && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-xl overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <div className="flex items-center justify-between border-b border-stone-200 px-6 py-5">
              <h3 className="text-2xl font-black tracking-tight text-stone-950">{editingId ? "Edit account" : "Add account"}</h3>
              <button type="button" onClick={() => setModalOpen(false)} className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 text-stone-500">×</button>
            </div>
            <form className="grid gap-4 p-6" onSubmit={saveAccount}>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Username</span>
                <input value={form.username} onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Full name</span>
                <input value={form.full_name} onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Role</span>
                <select value={form.role} onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as "Admin" | "Manager" | "Clerk" }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900">
                  <option value="Admin">Admin</option>
                  <option value="Manager">Manager</option>
                  <option value="Clerk">Clerk</option>
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Email</span>
                <input value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Assigned warehouse</span>
                <select
                  value={form.assigned_warehouse_id}
                  onChange={(event) => setForm((current) => ({ ...current, assigned_warehouse_id: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900"
                >
                  <option value="">None</option>
                  {warehouses.map((warehouse) => (
                    <option key={warehouse.warehouse_id} value={warehouse.warehouse_id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Avatar image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(event) => setAvatarFile(event.target.files?.[0] ?? null)}
                  className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900 file:mr-4 file:rounded-full file:border-0 file:bg-emerald-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-emerald-700"
                />
                <p className="mt-2 text-xs text-stone-500">{avatarFile ? `Selected: ${avatarFile.name}` : "Choose a file to upload a new avatar for this account."}</p>
              </label>
              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Avatar URL fallback</span>
                <input
                  value={form.profile_image_url}
                  onChange={(event) => setForm((current) => ({ ...current, profile_image_url: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900"
                  placeholder="https://..."
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Status</span>
                <select value={form.is_active} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.value as "0" | "1" }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900">
                  <option value="1">Active</option>
                  <option value="0">Inactive</option>
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Password {editingId ? "(optional)" : ""}</span>
                <input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} className="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-stone-900" />
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

      {deletingId && isAdmin && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-950/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-[2rem] border border-white/70 bg-white p-6 shadow-[0_30px_80px_rgba(57,32,7,0.22)]">
            <h3 className="text-2xl font-black tracking-tight text-stone-950">Delete account?</h3>
            <p className="mt-3 text-sm text-stone-600">This action permanently removes the account.</p>
            <div className="mt-6 flex items-center justify-end gap-3">
              <button type="button" onClick={() => setDeletingId(null)} className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700">Cancel</button>
              <button type="button" onClick={deleteAccount} disabled={saving} className="rounded-full bg-red-600 px-5 py-2.5 text-sm font-semibold text-white">{saving ? "Deleting..." : "Delete"}</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
