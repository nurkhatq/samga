'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

const RadioGroupContext = React.createContext<{
  value?: string;
  onValueChange?(value: string): void;
}>({});

const RadioGroup = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value?: string;
    onValueChange?(value: string): void;
  }
>(({ className, value, onValueChange, ...props }, ref) => {
  return (
    <RadioGroupContext.Provider value={{ value, onValueChange }}>
      <div ref={ref} className={cn('grid gap-2', className)} {...props} />
    </RadioGroupContext.Provider>
  );
});
RadioGroup.displayName = 'RadioGroup';

const RadioGroupItem = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement> & {
    value: string;
  }
>(({ className, value, checked, ...props }, ref) => {
  const { value: contextValue, onValueChange } = React.useContext(RadioGroupContext);
  
  const isChecked = checked !== undefined ? checked : contextValue === value;

  return (
    <input
      ref={ref}
      type="radio"
      value={value}
      checked={isChecked}
      onChange={(e) => {
        props.onChange?.(e);
        onValueChange?.(value);
      }}
      className={cn(
        'h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500',
        className
      )}
      {...props}
    />
  );
});
RadioGroupItem.displayName = 'RadioGroupItem';

export { RadioGroup, RadioGroupItem };