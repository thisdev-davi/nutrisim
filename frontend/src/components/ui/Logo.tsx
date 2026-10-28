// troca a logo pela classe do next-themes, sem esperar montar
export function Logo({ simbolo = false }: { simbolo?: boolean }) {
  const nome = simbolo ? "nutrisim-simbolo" : "nutrisim";
  return (
    <>
      <img src={`/logo/${nome}-escuro.svg`} alt="" className="h-5 w-auto [.light_&]:hidden" />
      <img src={`/logo/${nome}-claro.svg`} alt="" className="h-5 w-auto hidden [.light_&]:block" />
    </>
  );
}
