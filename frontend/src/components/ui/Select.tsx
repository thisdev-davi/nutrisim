import { SelectHTMLAttributes, ReactNode } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  helpText?: ReactNode;
}

export function Select({ label, helpText, id, className = "", children, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-medium text-fg">
        {label}
      </label>
      <select
        id={id}
        className={`h-11 px-3 border border-line-strong bg-surface text-fg rounded-md text-[15px] appearance-none focus:outline-focus focus:outline-2 ${className}`}
        {...props}
      >
        {children}
      </select>
      {helpText && (
        <p className="text-[13px] leading-5 text-fg-muted mt-1">
          {helpText}
        </p>
      )}
    </div>
  );
}