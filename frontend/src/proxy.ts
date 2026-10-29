import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Rotas de Autenticação e Públicas
const authRoutes = ["/login", "/cadastro"];

export function proxy(request: NextRequest) {
  const token = request.cookies.get("nutrisim_token")?.value;
  const { pathname } = request.nextUrl;

  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));
  const isPublicRoute = pathname === "/";

  // Sem token, não é rota de autenticar e não é rota pública
  if (!token && !isAuthRoute && !isPublicRoute) {
    const urlLogin = new URL("/login", request.url);
    urlLogin.searchParams.set("redirect", pathname);
    return NextResponse.redirect(urlLogin);
  }

  // Já tem token e tentou acessar rota de login/cadastro
  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL("/caso/novo", request.url));
  }

  // Libera o acesso
  return NextResponse.next();
}

// Configura o matcher ignorando arquivos estáticos, imagens e a pasta api local
export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.svg$).*)",
  ],
};