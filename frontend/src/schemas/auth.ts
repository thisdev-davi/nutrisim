import { z } from "zod";

export const cadastroSchema = z.object({
  nome: z
    .string()
    .trim()
    .min(1, "O nome é obrigatório")
    .max(100, "O nome deve ter no máximo 100 caracteres"),
  email: z
    .string()
    .trim()
    .email("Informe um e-mail válido"),
  senha: z
    .string()
    .min(8, "A senha deve ter no mínimo 8 caracteres")
    .max(128, "A senha deve ter no máximo 128 caracteres"),
});

export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .email("Informe um e-mail válido"),
  senha: z
    .string()
    .min(1, "Informe a senha"),
});

export type CadastroFormData = z.infer<typeof cadastroSchema>;
export type LoginFormData = z.infer<typeof loginSchema>;