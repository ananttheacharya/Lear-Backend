import React from 'react';
import './ui.css';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, icon, size = 'md', id, ...props },
  ref,
) {
  const inputId = id || `input-${label?.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'field'}`;
  return (
    <div className="ui-field">
      {label && <label className="ui-field__label" htmlFor={inputId}>{label}</label>}
      <span className={`ui-input-wrap ui-input-wrap--${size} ${error ? 'ui-input-wrap--error' : ''}`}>
        {icon}
        <input ref={ref} id={inputId} className="ui-input" aria-invalid={!!error} {...props} />
      </span>
      {error ? <span className="ui-field__error">{error}</span> : hint && <span className="ui-field__hint">{hint}</span>}
    </div>
  );
});
