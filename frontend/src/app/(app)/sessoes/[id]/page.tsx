import { EtapaSessao } from "./EtapaSessao";

export default async function SessaoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EtapaSessao sessaoId={id} />;
}
