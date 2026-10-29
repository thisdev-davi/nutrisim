// circulo com ate duas iniciais; decorativo, quem usa da o nome por extenso
export function Avatar({ nome, pequeno = false }: { nome: string; pequeno?: boolean }) {
  const iniciais = nome.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
  return (
    <span aria-hidden className={`grid place-items-center shrink-0 rounded-full border border-line bg-surface text-fg-muted font-mono font-medium leading-none ${pequeno ? "size-7 text-[11px]" : "size-8 text-[12px]"}`}>
      {iniciais}
    </span>
  );
}
