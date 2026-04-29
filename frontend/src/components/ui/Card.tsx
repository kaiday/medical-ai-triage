import type { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <section className={`portal-card rounded-2xl ${className}`} {...props}>
      {children}
    </section>
  );
}
