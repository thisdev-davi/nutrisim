import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Rotas de Autenticação e Públicas
const authRoutes = ["/login", "/cadastro"];

export function proxy(request: NextRequest) {
  // mesmo nome do COOKIE_TOKEN do lib/api, que nao entra aqui por puxar codigo do navegador
  const token = request.cookies.get("nutrisim_token")?.value;
  const { pathname } = request.nextUrl;

  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Sem token e não é rota de autenticar
  if (!token && !isAuthRoute) {
    const urlLogin = new URL("/login", request.url);
    urlLogin.searchParams.set("redirect", pathname);
    return NextResponse.redirect(urlLogin);
  }

  // Já tem token e tentou acessar rota de login/cadastro
  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL("/", request.url));
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