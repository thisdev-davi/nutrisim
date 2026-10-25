import { ReactNode } from "react";
import { Check, CircleAlert, Info, TriangleAlert } from "lucide-react";

interface AlertProps {
  type?: "danger" | "info" | "warning" | "success";
  title?: string;
  children: ReactNode;
  action?: ReactNode;
}

const styles = {
  danger: { box: "border-transparent bg-danger-soft text-danger", Icon: CircleAlert },
  info: { box: "border-line text-fg-muted", Icon: Info },
  warning: { box: "border-transparent bg-warning-soft text-warning", Icon: TriangleAlert },
  success: { box: "border-transparent bg-success-soft text-success", Icon: Check },
};

export function Alert({ type = "danger", title, children, action }: AlertProps) {
  const { box, Icon } = styles[type];

  return (
    <div role={type === "danger" ? "alert" : undefined} className={`flex gap-2 border px-4 py-3 rounded-md text-[13px] leading-5 ${box}`}>
      <Icon size={16} strokeWidth={1.5} aria-hidden className={`shrink-0 mt-0.5 ${type === "info" ? "text-fg" : ""}`} />
      <div className="flex flex-col gap-1 min-w-0">
        {title && <p className="font-semibold text-[14px] leading-5">{title}</p>}
        <div>{children}</div>
        {action && <div>{action}</div>}
      </div>
    </div>
  );
}
