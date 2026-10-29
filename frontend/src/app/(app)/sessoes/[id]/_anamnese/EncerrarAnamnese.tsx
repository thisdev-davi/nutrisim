"use client";

import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";
import { api, type Erro } from "@/lib/api";
import { estiloBotao } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { chaveSessao, type Sessao } from "./AnamneseChat";

export function EncerrarAnamnese({ sessaoId, disabled }: { sessaoId: string; disabled: boolean }) {
  const dialogo = useRef<HTMLDialogElement>(null);
  const queryClient = useQueryClient();
  const { mutate: encerrar, isPending, error } = useMutation({
    mutationFn: () => api<{ etapa: string }>(`/sessoes/${sessaoId}/anamnese/encerrar`, { method: "POST" }),
    onSuccess: ({ etapa }) => {
      queryClient.setQueryData<Sessao>(chaveSessao(sessaoId), (s) => s && { ...s, etapa });
      dialogo.current?.close();
    },
  });

  return (
    <>
      <button type="button" className={estiloBotao("primary", true)} disabled={disabled} onClick={() => dialogo.current?.showModal()}>
        Montar o plano
        <ArrowRight size={16} strokeWidth={1.5} aria-hidden className="hidden md:block" />
      </button>

      <dialog
        ref={dialogo}
        aria-labelledby="encerrar-titulo"
        aria-describedby="encerrar-texto"
        className="m-auto w-[calc(100%-32px)] max-w-[440px] p-6 border border-line rounded-lg bg-surface text-fg shadow-[var(--overlay)] backdrop:bg-black/60"
      >
        <div className="flex flex-col gap-3">
          <h2 id="encerrar-titulo" className="m-0 text-[18px] leading-[26px] font-semibold tracking-[-0.02em]">Encerrar a anamnese?</h2>
          {/* sem "ao/a" + nome: a api nao diz o genero do paciente */}
          <p id="encerrar-texto" className="m-0 text-fg-muted">
            Você não vai poder fazer novas perguntas ao paciente até o retorno. A conversa e as anotações continuam no painel ao lado.
          </p>
          {error && <Alert type="danger">{(error as unknown as Erro).mensagem}</Alert>}
          <div className="flex flex-wrap justify-end gap-2 pt-3">
            <button type="button" className={estiloBotao("secondary", true)} onClick={() => dialogo.current?.close()}>
              Continuar conversando
            </button>
            <button type="button" className={estiloBotao("primary", true)} disabled={isPending} onClick={() => encerrar()}>
              Encerrar e montar o plano
            </button>
          </div>
        </div>
      </dialog>
    </>
  );
}
