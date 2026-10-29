import { Etapas } from "@/components/ui/Etapas";
import { AnamneseChat } from "./_anamnese/AnamneseChat";
import { AnamneseInstructions } from "./_anamnese/AnamneseInstructions";

export default async function SessaoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <>
      <Etapas atual={2} compacta />

      <div className="w-full max-w-[1100px] mx-auto px-4 pt-6 pb-6 md:px-10 md:pt-10 md:pb-16 flex flex-col gap-6 md:gap-8">
        <Etapas atual={2} />
        <h1 className="m-0 font-display font-medium text-[24px] leading-[30px] md:text-[28px] md:leading-[34px] tracking-[-0.02em]">
          Anamnese
        </h1>
        <div className="flex flex-col lg:grid lg:grid-cols-[1.3fr_1fr] gap-6 items-start">
          <AnamneseChat sessaoId={id} />
          <AnamneseInstructions sessaoId={id} />
        </div>
      </div>
    </>
  );
}
