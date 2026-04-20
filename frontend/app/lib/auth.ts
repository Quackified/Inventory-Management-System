const TOKEN_KEY = "inventory_auth_token";
const USER_KEY = "inventory_auth_user";

export type AuthUser = {
  user_id: number;
  username: string;
  full_name: string;
  role: UserRole;
  email?: string | null;
  profile_image_url?: string | null;
  assigned_warehouse_id?: number | null;
  assigned_warehouse_name?: string | null;
};

export type UserRole = "Admin" | "Manager" | "Clerk";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  return raw ? (JSON.parse(raw) as AuthUser) : null;
}

export function saveAuthSession(token: string, user: AuthUser) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  window.dispatchEvent(new Event("inventory-auth-updated"));
}

export function clearAuthSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.dispatchEvent(new Event("inventory-auth-updated"));
}

export function getRoleHomePath(role: UserRole | string | null | undefined) {
  if (role === "Admin" || role === "Manager") {
    return "/dashboard";
  }
  if (role === "Clerk") {
    return "/clerk-stock";
  }
  return "/login";
}

export function hasRoleAccess(role: UserRole | string | null | undefined, allowedRoles: UserRole[]) {
  if (!role) return false;
  return allowedRoles.includes(role as UserRole);
}
