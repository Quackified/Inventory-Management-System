import { useEffect, useMemo, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { clearAuthSession, getRoleHomePath, getStoredToken, getStoredUser, hasRoleAccess, type AuthUser } from "../lib/auth";
import { getImageUrl } from "../lib/urlUtils";


import {
  BookOpen,
  Boxes,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  ScanBarcode,
  Tags,
  UserCog,
  UserRound,
  Warehouse,
} from "lucide-react";

type NavItem = {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: Array<"Admin" | "Manager" | "Clerk">;
};

const navItems: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["Admin", "Manager"] },
  { to: "/clerk-stock", label: "Stock Flow", icon: ScanBarcode, roles: ["Admin", "Manager", "Clerk"] },
  { to: "/products", label: "Products", icon: Boxes, roles: ["Admin", "Manager"] },
  { to: "/transactions", label: "Transactions", icon: BookOpen, roles: ["Admin", "Manager"] },
  { to: "/warehouses", label: "Warehouses", icon: Warehouse, roles: ["Admin", "Manager"] },
  { to: "/categories", label: "Categories", icon: Tags, roles: ["Admin", "Manager"] },
  { to: "/accounts", label: "Accounts", icon: UserCog, roles: ["Admin"] },
];

export default function AppShellRoute() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    setUser(getStoredUser());

    if (typeof window !== "undefined") {
      setCollapsed(window.localStorage.getItem("inventory_sidebar_collapsed") === "1");
    }
  }, [navigate]);

  useEffect(() => {
    function syncUserFromStorage() {
      setUser(getStoredUser());
    }

    if (typeof window === "undefined") return;
    window.addEventListener("inventory-auth-updated", syncUserFromStorage);
    return () => window.removeEventListener("inventory-auth-updated", syncUserFromStorage);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem("inventory_sidebar_collapsed", collapsed ? "1" : "0");
  }, [collapsed]);

  const visibleNav = useMemo(() => {
    const currentRole = user?.role;
    return navItems.filter((item) => !item.roles || hasRoleAccess(currentRole, item.roles));
  }, [user]);

  useEffect(() => {
    if (!user) return;

    const isProfilePath = location.pathname.startsWith("/profile");
    const allowed = navItems.some(
      (item) =>
        location.pathname.startsWith(item.to) &&
        (!item.roles || hasRoleAccess(user.role, item.roles)),
    );

    if (!allowed && !isProfilePath) {
      navigate(getRoleHomePath(user.role), { replace: true });
    }
  }, [location.pathname, navigate, user]);

  function logout() {
    clearAuthSession();
    navigate("/login", { replace: true });
  }

  const userInitial = (user?.full_name || user?.username || "U").trim().charAt(0).toUpperCase();

  return (
    <div className="h-screen w-screen overflow-hidden">
      <div className="grid h-full w-full grid-cols-[auto_minmax(0,1fr)]">
        <aside
          className={`relative h-full border-r border-emerald-950/30 bg-[linear-gradient(180deg,rgba(6,78,59,0.96),rgba(4,47,46,0.95))] text-white shadow-[0_24px_80px_rgba(16,185,129,0.12)] transition-all duration-200 ${collapsed ? "w-[78px]" : "w-[248px]"}`}
        >
          <button
            type="button"
            onClick={() => setCollapsed((current) => !current)}
            className="absolute -right-3 top-16 z-20 inline-flex h-7 w-7 items-center justify-center rounded-full border border-emerald-200 bg-white text-emerald-900 shadow"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>

          <div className="flex h-full flex-col px-3 py-4">
            <div className="mb-4 flex min-h-14 items-center justify-center">
              {!collapsed && (
                <div className="w-full text-center">
                  <p className="text-xl font-black tracking-tight text-emerald-300">IMBAK</p>
                  <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-100/70">Warehouse/Store Management</p>
                </div>
              )}
              {collapsed && <p className="text-sm font-black tracking-tight text-emerald-300">IM</p>}
            </div>

            <nav className="space-y-2 px-1.5">
              {visibleNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                    `flex h-12 w-full items-center justify-center gap-3 rounded-lg px-3 py-2 text-sm font-semibold transition ${
                        isActive ? "bg-emerald-400 text-emerald-950" : "text-emerald-50/90 hover:bg-white/10 hover:text-white"
                      }`
                    }
                    title={collapsed ? item.label : undefined}
                  >
                    <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded border border-white/15 bg-white/10">
                      <Icon className="h-4 w-4" />
                    </span>
                    {!collapsed && <span className="w-[132px] pr-1 leading-none text-left">{item.label}</span>}
                  </NavLink>
                );
              })}
            </nav>

            <div className="mt-auto space-y-2">
              {!collapsed && (
                <NavLink
                  to="/profile"
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-md border p-2 text-left backdrop-blur-sm transition ${
                      isActive
                        ? "border-emerald-200/50 bg-emerald-300/20"
                        : "border-white/10 bg-white/5 hover:bg-white/10"
                    }`
                  }
                >
                  {user?.profile_image_url ? (
                    <img
                       src={getImageUrl(user.profile_image_url)}
                      alt={`${user.full_name} avatar`}
                      className="h-10 w-10 rounded-full border border-white/30 object-cover"
                    />
                  ) : (
                    <div className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/25 bg-white/10 text-sm font-black text-emerald-100">
                      {userInitial}
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold uppercase tracking-[0.15em] text-emerald-100">{user?.role ?? "Role"}</p>
                    <p className="truncate text-xs text-emerald-50/80">{user?.username ?? "username"}</p>
                  </div>
                </NavLink>
              )}
              {collapsed && (
                <NavLink
                  to="/profile"
                  className={({ isActive }) =>
                    `inline-flex w-full items-center justify-center rounded-md border px-2 py-2 transition ${
                      isActive
                        ? "border-emerald-200/50 bg-emerald-300/20"
                        : "border-white/20 bg-white/5 hover:bg-white/10"
                    }`
                  }
                  title="Profile"
                >
                  {user?.profile_image_url ? (
                    <img
                       src={getImageUrl(user.profile_image_url)}
                      alt="Profile avatar"
                      className="h-7 w-7 rounded-full border border-white/30 object-cover"
                    />
                  ) : (
                    <UserRound className="h-4 w-4" />
                  )}
                </NavLink>
              )}
              <button
                type="button"
                onClick={logout}
                className="inline-flex w-full items-center justify-center rounded-md border border-white/20 bg-white/5 px-3 py-2 text-sm font-semibold text-emerald-50 hover:bg-white/10"
                title="Sign out"
                aria-label="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </aside>

        <div className="h-full min-w-0 overflow-x-hidden overflow-y-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
