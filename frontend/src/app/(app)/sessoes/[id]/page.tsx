import { AnamneseChat } from "./_anamnese/AnamneseChat";

export default async function SessaoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AnamneseChat sessaoId={id} />;
}
