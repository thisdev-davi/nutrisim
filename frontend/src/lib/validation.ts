import { ZodError } from "zod";

export function formatZodErrors(error: ZodError): Record<string, string> {
  const errosAchatados = error.flatten().fieldErrors;
  const errosFormatados: Record<string, string> = {};

  for (const [campo, mensagens] of Object.entries(errosAchatados)) {
    if (Array.isArray(mensagens) && mensagens.length > 0) {
      errosFormatados[campo] = mensagens[0];
    }
  }

  return errosFormatados;
}