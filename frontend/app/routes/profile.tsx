import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/profile";
import { api, getApiErrorMessage } from "../lib/api";
import { getStoredToken, getStoredUser, saveAuthSession, type AuthUser } from "../lib/auth";
import { getImageUrl } from "../lib/urlUtils";

type WarehouseItem = {
  warehouse_id: number;
  name: string;
};

type ProfileFormState = {
  username: string;
  full_name: string;
  email: string;
  profile_image_url: string;
  assigned_warehouse_id: string;
};

const defaultForm: ProfileFormState = {
  username: "",
  full_name: "",
  email: "",
  profile_image_url: "",
  assigned_warehouse_id: "",
};

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Profile - Warehouse/Store Management" },
    { name: "description", content: "Manage your profile, avatar, and warehouse assignment" },
  ];
}

export default function ProfileRoute() {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(getStoredUser());
  const [form, setForm] = useState<ProfileFormState>(defaultForm);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [warehouses, setWarehouses] = useState<WarehouseItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setLoading(true);
    Promise.all([api.get("/api/v1/auth/me"), api.get("/api/v1/warehouses")])
      .then(([profileResponse, warehousesResponse]) => {
        const profile = profileResponse.data as AuthUser;
        const allWarehouses = (warehousesResponse.data.items ?? []) as WarehouseItem[];

        setUser(profile);
        setWarehouses(allWarehouses);
        setForm({
          username: profile.username ?? "",
          full_name: profile.full_name ?? "",
          email: profile.email ?? "",
          profile_image_url: profile.profile_image_url ?? "",
          assigned_warehouse_id: profile.assigned_warehouse_id ? String(profile.assigned_warehouse_id) : "",
        });
        setAvatarFile(null);
        setError(null);
      })
      .catch((requestError) => {
        setError(getApiErrorMessage(requestError, "Failed to load profile."));
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  const avatarInitial = useMemo(() => {
    return (form.full_name || form.username || "U").trim().charAt(0).toUpperCase();
  }, [form.full_name, form.username]);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      let profileImageUrl = form.profile_image_url.trim() || null;

      if (avatarFile) {
        const avatarData = new FormData();
        avatarData.append("file", avatarFile);
        const avatarResponse = await api.post("/api/v1/auth/avatar", avatarData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        profileImageUrl = avatarResponse.data.profile_image_url ?? profileImageUrl;
      }

      const response = await api.put("/api/v1/auth/profile", {
        username: form.username.trim(),
        full_name: form.full_name.trim(),
        email: form.email.trim() || null,
        profile_image_url: profileImageUrl,
        assigned_warehouse_id: form.assigned_warehouse_id ? Number(form.assigned_warehouse_id) : null,
      });

      const updated = response.data as AuthUser;
      const token = getStoredToken();
      if (token) {
        saveAuthSession(token, updated);
      }
      setUser(updated);
      setForm((current) => ({
        ...current,
        username: updated.username ?? current.username,
        full_name: updated.full_name ?? current.full_name,
        email: updated.email ?? "",
        profile_image_url: updated.profile_image_url ?? "",
        assigned_warehouse_id: updated.assigned_warehouse_id ? String(updated.assigned_warehouse_id) : "",
      }));
      setAvatarFile(null);
      setMessage("Profile updated.");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Failed to update profile."));
    } finally {
      setSaving(false);
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
        <header className="overflow-hidden rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_22px_70px_rgba(16,185,129,0.08)] backdrop-blur">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700">Warehouse/Store Management</p>
                <span className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-500">
                  Profile
                </span>
              </div>
              <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950 sm:text-3xl">My Profile</h1>
            </div>
          </div>
        </header>

        {error && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {message && <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}

        <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/82 shadow-[0_20px_60px_rgba(16,185,129,0.07)] backdrop-blur-xl">
          <form onSubmit={saveProfile} className="grid gap-6 p-6 lg:grid-cols-[280px_minmax(0,1fr)]">
            <div className="rounded-3xl border border-emerald-100 bg-emerald-50/40 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">User Info</p>
              <div className="mt-4 flex items-center gap-4">
                {form.profile_image_url ? (
                  <img src={getImageUrl(form.profile_image_url)} alt="Profile avatar" className="h-16 w-16 rounded-full border border-emerald-200 object-cover" />
                ) : (
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-full border border-emerald-200 bg-white text-2xl font-black text-emerald-700">
                    {avatarInitial}
                  </div>
                )}
                <div>
                  <p className="text-sm font-semibold text-stone-900">{form.full_name || "User"}</p>
                  <p className="text-xs text-stone-500">{user?.role ?? "Role"}</p>
                  <p className="text-xs text-stone-500">@{form.username || "username"}</p>
                </div>
              </div>
              <p className="mt-3 text-xs text-stone-500">Choose an image file or keep a direct avatar URL as fallback.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Username</span>
                <input
                  value={form.username}
                  onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="username"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Full name</span>
                <input
                  value={form.full_name}
                  onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="Your name"
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Email</span>
                <input
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="name@example.com"
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Avatar image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(event) => setAvatarFile(event.target.files?.[0] ?? null)}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition file:mr-4 file:rounded-full file:border-0 file:bg-emerald-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-emerald-700 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                />
                <p className="mt-2 text-xs text-stone-500">{avatarFile ? `Selected: ${avatarFile.name}` : "Choose a file to upload a new avatar."}</p>
              </label>

              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Avatar URL fallback</span>
                <input
                  value={form.profile_image_url}
                  onChange={(event) => setForm((current) => ({ ...current, profile_image_url: event.target.value }))}
                  className="w-full rounded-2xl border border-stone-200 bg-white/90 px-4 py-3 text-stone-900 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="https://..."
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-semibold text-stone-700">Assigned warehouse</span>
                <select
                  value={form.assigned_warehouse_id}
                  onChange={(event) => setForm((current) => ({ ...current, assigned_warehouse_id: event.target.value }))}
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

              <div className="md:col-span-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => navigate("/dashboard")}
                  className="rounded-full border border-stone-200 bg-white px-5 py-2.5 text-sm font-semibold text-stone-700 transition hover:bg-stone-50"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={saving || loading}
                  className="rounded-full bg-[linear-gradient(135deg,#047857,#10b981)] px-5 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {saving ? "Saving..." : "Save profile"}
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
