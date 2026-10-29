import { FormularioAuth } from "../_auth/FormularioAuth";

// ?email= vem do aviso de e-mail ja cadastrado
export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { email, redirect } = await searchParams;
  return <FormularioAuth modo="entrar" email={typeof email === "string" ? email : ""} redirect={typeof redirect === "string" ? redirect : undefined} />;
}
