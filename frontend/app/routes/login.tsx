import { useState } from "react";
import type { FormEvent } from "react";
import { api, getApiErrorMessage, setAuthToken } from "../lib/api";
import { saveAuthSession, type UserRole } from "../lib/auth";
import type { Route } from "./+types/login";
import { redirect } from "react-router";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Warehouse/Store Management Login" },
    { name: "description", content: "Secure sign in for IMBAK Inventory" },
  ];
}

function EyeOpenIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-5 w-5" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12s3.75-6.75 9.75-6.75S21.75 12 21.75 12 18 18.75 12 18.75 2.25 12 2.25 12Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeClosedIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-5 w-5" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M10.58 10.58A2 2 0 0 0 13.42 13.42" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.88 5.26A10.7 10.7 0 0 1 12 5.25c6 0 9.75 6.75 9.75 6.75a19.7 19.7 0 0 1-4.18 4.91" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.23 6.23A19.2 19.2 0 0 0 2.25 12s3.75 6.75 9.75 6.75a10.8 10.8 0 0 0 5.77-1.69" />
    </svg>
  );
}

export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData();
  const username = String(formData.get("username") ?? "");
  const password = String(formData.get("password") ?? "");

  const response = await api.post("/api/v1/auth/login", { username, password });
  const { access_token, user } = response.data as {
    access_token: string;
    user: {
      user_id: number;
      username: string;
      full_name: string;
      role: UserRole;
      email?: string | null;
      profile_image_url?: string | null;
      assigned_warehouse_id?: number | null;
      assigned_warehouse_name?: string | null;
    };
  };

  saveAuthSession(access_token, user);
  setAuthToken(access_token);
  return redirect("/");
}

export default function LoginRoute() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("password");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await api.post("/api/v1/auth/login", { username, password });
      const { access_token, user } = response.data as {
        access_token: string;
        user: {
          user_id: number;
          username: string;
          full_name: string;
          role: UserRole;
          email?: string | null;
          profile_image_url?: string | null;
          assigned_warehouse_id?: number | null;
          assigned_warehouse_name?: string | null;
        };
      };
      saveAuthSession(access_token, user);
      setAuthToken(access_token);
      window.location.href = "/";
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to sign in. Please try again."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-6 text-stone-900 sm:px-6 lg:px-8 lg:py-10">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-8rem] top-[-8rem] h-80 w-80 rounded-full bg-emerald-300/35 blur-3xl" />
        <div className="absolute right-[-7rem] top-[10rem] h-96 w-96 rounded-full bg-teal-500/12 blur-3xl" />
        <div className="absolute bottom-[-10rem] left-[20%] h-96 w-96 rounded-full bg-[#10b981]/20 blur-3xl" />
      </div>

      <div className="relative mx-auto grid min-h-[calc(100vh-3rem)] max-w-7xl items-stretch gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative flex overflow-hidden rounded-[2rem] border border-emerald-400/20 bg-[linear-gradient(135deg,rgba(6,78,59,0.96),rgba(15,118,110,0.94))] px-8 py-10 text-white shadow-[0_30px_100px_rgba(16,185,129,0.18)] lg:px-10 lg:py-12 backdrop-blur-xl">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.15),_transparent_36%),radial-gradient(circle_at_bottom_left,_rgba(255,255,255,0.08),_transparent_30%)]" />
          <div className="relative flex w-full flex-col justify-between gap-10">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-100">
                Warehouse/Store Management
              </div>
              <h1 className="mt-6 max-w-xl text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                IMBAK Warehouse/Store Management Platform
              </h1>
              <p className="mt-5 max-w-xl text-sm leading-7 text-stone-200 sm:text-base">
                Operate stock, warehouses, categories, transactions, and account access from one secure and modern system.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { label: "Secure access", value: "JWT session control" },
                { label: "Role-based", value: "Admin, Manager, Clerk" },
                { label: "Operations ready", value: "Audit-ready inventory flow" },
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur-md shadow-[inset_0_1px_0_rgba(255,255,255,0.16)]">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.26em] text-emerald-100/80">{item.label}</p>
                  <p className="mt-2 text-sm font-semibold text-white">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-[2rem] border border-white/50 bg-white/78 p-6 shadow-[0_24px_70px_rgba(16,185,129,0.12)] backdrop-blur-xl lg:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-700">Secure sign in</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight text-stone-950">Welcome back</h2>
              <p className="mt-2 text-sm leading-6 text-stone-600">Sign in to continue to the IMBAK warehouse and store operations workspace.</p>
            </div>
            <div className="hidden rounded-2xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700 sm:block">IMBAK</div>
          </div>

          <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-stone-700">Username</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-2xl border border-stone-200 bg-white/85 px-4 py-3 text-stone-900 outline-none transition placeholder:text-stone-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                placeholder="admin"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-stone-700">Password</span>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full rounded-2xl border border-stone-200 bg-white/85 px-4 py-3 pr-12 text-stone-900 outline-none transition placeholder:text-stone-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  placeholder="password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                  className="absolute right-3 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-stone-500 transition hover:bg-stone-100 hover:text-stone-700"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeClosedIcon /> : <EyeOpenIcon />}
                </button>
              </div>
            </label>

            {error && <p className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="group inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,#047857,#10b981)] px-4 py-3 text-sm font-semibold text-white shadow-[0_16px_30px_rgba(16,185,129,0.22)] transition hover:-translate-y-0.5 hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <span>{submitting ? "Signing in..." : "Sign in"}</span>
              <span className="transition group-hover:translate-x-0.5">→</span>
            </button>
          </form>

          <div className="mt-8 rounded-2xl border border-emerald-200/70 bg-emerald-50/80 px-4 py-4 text-sm text-emerald-900/80">
            Tip: Password migration is complete. Use your assigned role account credentials to sign in.
          </div>
        </section>
      </div>
    </main>
  );
}
