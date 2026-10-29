import { z } from "zod";

export const cadastroSchema = z.object({
  nome: z
    .string()
    .trim()
    .min(1, "Informe seu nome.")
    .max(100, "O nome deve ter no máximo 100 caracteres"),
  email: z
    .string()
    .trim()
    .email("Informe um e-mail válido, como voce@exemplo.com."),
  senha: z
    .string()
    // diz quanto falta, como no artefato
    .min(8, { error: (iss) => `Use pelo menos 8 caracteres. Faltam ${8 - String(iss.input).length}.` })
    .max(128, "A senha deve ter no máximo 128 caracteres"),
});

export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .email("Informe um e-mail válido, como voce@exemplo.com."),
  senha: z
    .string()
    .min(1, "Informe a senha."),
});

export type CadastroFormData = z.infer<typeof cadastroSchema>;
export type LoginFormData = z.infer<typeof loginSchema>;