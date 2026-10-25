import { SelectHTMLAttributes, ReactNode } from "react";
import { ChevronDown } from "lucide-react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  helpText?: ReactNode;
}

export function Select({ label, helpText, id, className = "", children, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5 min-w-0">
      <label htmlFor={id} className="text-[13px] leading-4 font-medium text-fg">
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          className={`w-full h-11 pl-3 pr-10 border border-line-strong bg-surface text-fg rounded-md text-[15px] leading-6 appearance-none cursor-pointer transition-colors hover:border-fg-muted focus-visible:outline-offset-0 focus-visible:border-transparent disabled:opacity-45 disabled:cursor-not-allowed ${className}`}
          {...props}
        >
          {children}
        </select>
        <ChevronDown size={16} strokeWidth={1.5} aria-hidden className="absolute right-3 top-3.5 text-fg-muted pointer-events-none" />
      </div>
      {helpText && (
        <p className="text-[13px] leading-5 text-fg-muted">
          {helpText}
        </p>
      )}
    </div>
  );
}
