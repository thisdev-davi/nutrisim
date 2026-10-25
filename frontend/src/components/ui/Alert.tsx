import { ReactNode } from "react";

interface AlertProps {
  type?: "danger" | "info" | "warning" | "success";
  title?: string;
  children: ReactNode;
  action?: ReactNode;
}

export function Alert({ type = "danger", title, children, action }: AlertProps) {
  const styles = {
    danger: "bg-danger-soft border-danger/30 text-danger",
    info: "bg-surface border-line text-fg-muted",
    warning: "bg-warning-soft border-warning/30 text-warning",
    success: "bg-success-soft border-success/30 text-success",
  };

  return (
    <div className={`border p-4 rounded-md flex flex-col gap-2 ${styles[type]}`}>
      {title && <h4 className="font-semibold text-[14px]">{title}</h4>}
      <div className="text-[14px] leading-relaxed">{children}</div>
      {action && <div className="mt-1">{action}</div>}
    </div>
  );
}