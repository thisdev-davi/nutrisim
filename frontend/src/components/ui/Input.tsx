import { InputHTMLAttributes, ReactNode, forwardRef } from "react";
import { CircleAlert } from "lucide-react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helpText?: ReactNode;
  error?: string;
  hideLabel?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, helpText, error, hideLabel, id, className = "", ...props }, ref) => {
    const isInvalid = Boolean(error);

    return (
      <div className="flex flex-col gap-[6px]">
        <label 
          htmlFor={id} 
          className={`text-[13px] leading-4 font-medium text-fg ${hideLabel ? "sr-only" : ""}`}
        >
          {label}
        </label>
        
        <input
          ref={ref}
          id={id}
          aria-invalid={isInvalid}
          aria-describedby={isInvalid ? `${id}-error` : helpText ? `${id}-help` : undefined}
          className={`h-11 px-3 border rounded-md bg-surface text-fg text-[15px] leading-6 placeholder:text-fg-muted focus:outline-focus focus:outline-2 disabled:opacity-45 disabled:cursor-not-allowed transition-colors
            ${isInvalid ? "border-danger" : "border-line-strong hover:border-fg-muted"}
            ${className}
          `}
          {...props}
        />

        {isInvalid ? (
          <p id={`${id}-error`} className="text-[13px] leading-5 text-danger flex items-center gap-1 mt-1"> <CircleAlert size={16} strokeWidth={1.5} aria-hidden /> {error} </p> ) : helpText ? ( <p id={`${id}-help`} className="text-[13px] leading-5 text-fg-muted mt-1">
            {helpText}
          </p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = "Input";