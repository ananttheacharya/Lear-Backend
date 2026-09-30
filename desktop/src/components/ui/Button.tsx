import React from 'react';
import { Loader2 } from 'lucide-react';
import './ui.css';
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant?: 'primary'|'secondary'|'ghost'|'danger'|'success'; size?: 'sm'|'md'|'lg'; loading?: boolean; icon?: React.ReactNode; iconPosition?: 'left'|'right'; fullWidth?: boolean; }
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button({variant='primary',size='md',loading=false,icon,iconPosition='left',fullWidth=false,children,disabled,...props}, ref) { return <button ref={ref} className={`ui-button ui-button--${variant} ui-button--${size} ${fullWidth?'ui-button--full':''}`} disabled={disabled||loading} {...props}>{loading?<Loader2 className="ui-spin" size={16}/>:icon&&iconPosition==='left'?icon:null}{!loading&&children}{!loading&&icon&&iconPosition==='right'?icon:null}</button>; });
