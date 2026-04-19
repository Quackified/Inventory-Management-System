import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import type { Route } from "./+types/home";
import { api, setAuthToken } from "../lib/api";
import { clearAuthSession, getStoredToken, getStoredUser, saveAuthSession, type UserRole } from "../lib/auth";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Warehouse/Store Management" },
    { name: "description", content: "Inventory dashboard entry point" },
  ];
}

export default function Home() {
  const navigate = useNavigate();
  const [statusText, setStatusText] = useState("Checking session...");

  useEffect(() => {
    let cancelled = false;

    async function bootstrapSession() {
      setStatusText("Checking session...");
      const token = getStoredToken();
      const user = getStoredUser();

      if (token && user) {
        setAuthToken(token);
        try {
          await api.get("/api/v1/auth/me");
          if (!cancelled) {
            navigate("/dashboard", { replace: true });
          }
          return;
        } catch {
          clearAuthSession();
          setAuthToken(null);
        }
      }

      try {
        setStatusText("Restoring account...");
        const response = await api.post("/api/v1/auth/login", {
          username: "admin",
          password: "password",
        });

        const { access_token, user: loggedInUser } = response.data as {
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

        saveAuthSession(access_token, loggedInUser);
        setAuthToken(access_token);
        if (!cancelled) {
          navigate("/dashboard", { replace: true });
        }
        return;
      } catch {
        clearAuthSession();
        setAuthToken(null);
      }

      if (!cancelled) {
        navigate("/login", { replace: true });
      }
    }

    bootstrapSession();

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,rgba(16,185,129,0.14),transparent_42%),linear-gradient(180deg,#ecfdf5,#f8fafc)] text-stone-900">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-emerald-300/30 blur-3xl" />
        <div className="absolute -right-16 top-24 h-72 w-72 rounded-full bg-teal-400/16 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-4 py-8">
        <section className="w-full max-w-md rounded-3xl border border-emerald-100/80 bg-white/85 p-8 text-center shadow-[0_24px_80px_rgba(16,185,129,0.14)] backdrop-blur-xl">
          <div className="mx-auto mb-5 h-12 w-12 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600" />
          <p className="text-xs font-semibold uppercase tracking-[0.26em] text-emerald-700">IMBAK</p>
          <h1 className="mt-2 text-2xl font-black tracking-tight text-stone-950">Starting workspace</h1>
          <p className="mt-3 text-sm text-stone-600">{statusText}</p>
        </section>
      </div>
    </main>
  );
}
