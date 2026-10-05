import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl font-semibold tracking-[-0.01em] transition-all duration-200 outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/70 disabled:pointer-events-none disabled:opacity-45",
  {
    variants: {
      variant: {
        primary: "bg-cyan-300 px-4 py-2.5 text-slate-950 shadow-[0_0_24px_rgba(73,230,214,0.22)] hover:bg-cyan-200",
        secondary: "border border-white/10 bg-white/[0.055] px-4 py-2.5 text-slate-100 hover:border-white/20 hover:bg-white/[0.09]",
        ghost: "px-3 py-2 text-slate-400 hover:bg-white/[0.06] hover:text-white",
        danger: "border border-rose-400/20 bg-rose-400/10 px-4 py-2.5 text-rose-200 hover:bg-rose-400/15",
      },
      size: { sm: "h-9 text-xs", md: "h-11 text-sm", icon: "size-10 p-0" },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>;

export function Button({ className, variant, size, type = "button", ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} type={type} {...props} />;
}
