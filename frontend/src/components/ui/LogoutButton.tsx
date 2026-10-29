"use client";

import { useAuth } from "@/components/providers/AuthProvider";
import { Button } from "@/components/ui/Button";
import { LogOut } from "lucide-react";

interface LogoutButtonProps {
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
  exibirIcone?: boolean;
}

export function LogoutButton({ 
  variant = "ghost", 
  className = "",
  exibirIcone = true 
}: LogoutButtonProps) {
  const { logout } = useAuth();

  return (
    <Button 
      type="button" 
      variant={variant} 
      // "!" vence o hover neutro da variante
      className={`hover:text-danger! hover:bg-danger-soft! ${className}`}
      onClick={logout}
      title="Sair da conta"
    >
      {exibirIcone && <LogOut size={16} strokeWidth={1.5} aria-hidden />}
      Sair
    </Button>
  );
}