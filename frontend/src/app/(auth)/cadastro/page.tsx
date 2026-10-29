import { FormularioAuth } from "../_auth/FormularioAuth";

export default async function CadastroPage({ searchParams }: PageProps<"/cadastro">) {
  const { redirect } = await searchParams;
  return <FormularioAuth modo="criar" redirect={typeof redirect === "string" ? redirect : undefined} />;
}
