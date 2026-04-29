import type { ButtonHTMLAttributes, ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'teal';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-coral-500 text-white shadow-soft hover:bg-coral-600',
  secondary: 'border border-clinic-border bg-white text-ink-700 hover:bg-clinic-canvas',
  ghost: 'bg-transparent text-ink-500 hover:bg-clinic-canvas',
  teal: 'bg-brand-700 text-white shadow-soft hover:bg-brand-800',
};

export function Button({ children, className = '', variant = 'primary', ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 text-sm font-semibold transition ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
