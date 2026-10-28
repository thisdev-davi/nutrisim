export default async function AnamnesesPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 32 }}>
      <h1>Anamnese</h1>
      <p>Sessão: {id}</p>
      <p>Tela de anamnese em construção.</p>
    </div>
  );
}
