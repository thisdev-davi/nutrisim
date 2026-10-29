import { InputHTMLAttributes, ReactNode, forwardRef } from "react";
import { CircleAlert } from "lucide-react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helpText?: ReactNode;
  error?: string;
  hideLabel?: boolean;
  // botao dentro do campo, a direita (ex.: mostrar senha)
  children?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, helpText, error, hideLabel, id, className = "", children, ...props }, ref) => {
    const isInvalid = Boolean(error);

    return (
      <div className="flex flex-col gap-[6px] min-w-0">
        <label htmlFor={id} className={`text-[13px] leading-4 font-medium text-fg ${hideLabel ? "sr-only" : ""}`}>
          {label}
        </label>

        <div className="relative">
          <input
            ref={ref}
            id={id}
            aria-invalid={isInvalid}
            aria-describedby={isInvalid ? `${id}-error` : helpText ? `${id}-help` : undefined}
            className={`w-full h-11 md:h-9 px-3 border rounded-md bg-surface text-fg text-[16px] md:text-[15px] leading-6 placeholder:text-fg-muted focus-visible:outline-offset-0 focus-visible:border-transparent disabled:opacity-45 disabled:cursor-not-allowed transition-colors
              ${isInvalid ? "border-danger" : "border-line-strong hover:border-fg-muted"}
              ${children ? "pr-13" : ""}
              ${className}
            `}
            {...props}
          />
          {children && <div className="absolute top-0 right-0">{children}</div>}
        </div>

        {isInvalid ? (
          <p id={`${id}-error`} className="m-0 text-[13px] leading-5 text-danger flex items-center gap-1">
            <CircleAlert size={16} strokeWidth={1.5} aria-hidden className="shrink-0" /> {error}
          </p>
        ) : helpText ? (
          <p id={`${id}-help`} className="m-0 text-[13px] leading-5 text-fg-muted">
            {helpText}
          </p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = "Input";
