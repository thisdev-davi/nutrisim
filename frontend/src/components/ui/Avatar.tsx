// circulo com ate duas iniciais; decorativo, quem usa da o nome por extenso
export function Avatar({ nome, pequeno = false, grande = false }: { nome: string; pequeno?: boolean; grande?: boolean }) {
  const iniciais = nome.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
  const tamanho = pequeno ? "size-7 text-[11px]" : grande ? "size-10 text-[13px]" : "size-8 text-[12px]";
  return (
    <span aria-hidden className={`grid place-items-center shrink-0 rounded-full border border-line bg-surface text-fg-muted font-mono font-medium leading-none ${tamanho}`}>
      {iniciais}
    </span>
  );
}
