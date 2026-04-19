import { index, route, type RouteConfig } from "@react-router/dev/routes";

export default [
	index("routes/home.tsx"),
	route("login", "routes/login.tsx"),
	route("", "routes/app-shell.tsx", [
		route("dashboard", "routes/dashboard.tsx"),
		route("accounts", "routes/accounts.tsx"),
		route("categories", "routes/categories.tsx"),
		route("products", "routes/products.tsx"),
		route("profile", "routes/profile.tsx"),
		route("transactions", "routes/transactions.tsx"),
		route("warehouses", "routes/warehouses.tsx"),
	]),
] satisfies RouteConfig;
