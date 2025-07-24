import React, { useRef, useState, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';

interface LineNumberedTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  className?: string;
  placeholder?: string;
}

export function LineNumberedTextarea({
  value,
  onChange,
  className = '',
  placeholder = '',
  ...props
}: LineNumberedTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [lineNumbers, setLineNumbers] = useState<string>('1');

  // Update line numbers when value changes
  useEffect(() => {
    if (!textareaRef.current) return;
    
    // Split by newlines and count actual lines, including empty ones
    const lines = value.split('\n');
    const lineCount = Math.max(1, lines.length); // Always show at least line 1
    const numbers = Array.from({ length: lineCount }, (_, i) => (i + 1).toString()).join('\n');
    setLineNumbers(numbers);
    
    // Sync scroll position
    const textarea = textareaRef.current;
    const lineNumbersElement = textarea.parentElement?.querySelector('.line-numbers') as HTMLElement;
    if (lineNumbersElement) {
      lineNumbersElement.scrollTop = textarea.scrollTop;
    }
  }, [value]);

  // Handle pasted content and remove line numbers if present
  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const pastedText = e.clipboardData.getData('text');
    
    // Check if the pasted text contains line numbers (e.g., "1. text" or "1 text")
    const hasLineNumbers = /^\s*\d+[\s\.\)]+/m.test(pastedText);
    
    if (hasLineNumbers) {
      e.preventDefault();
      
      // Remove line numbers from pasted text
      const cleanedText = pastedText
        .split('\n')
        .map(line => line.replace(/^\s*\d+[\s\.\)]+/, ''))
        .join('\n');
      
      // Insert the cleaned text at cursor position
      const textarea = textareaRef.current;
      if (textarea) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const currentValue = textarea.value;
        
        const newValue = currentValue.substring(0, start) + cleanedText + currentValue.substring(end);
        
        // Update the value and cursor position
        onChange({ target: { value: newValue } } as React.ChangeEvent<HTMLTextAreaElement>);
        
        // Set cursor position after the inserted text
        setTimeout(() => {
          textarea.selectionStart = start + cleanedText.length;
          textarea.selectionEnd = start + cleanedText.length;
        }, 0);
      }
    }
  };

  // Handle scroll sync
  const handleScroll = (e: React.UIEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    const lineNumbersElement = textarea.parentElement?.querySelector('.line-numbers');
    if (lineNumbersElement) {
      lineNumbersElement.scrollTop = textarea.scrollTop;
    }
  };

  return (
    <div className="relative flex">
      <div className="line-numbers absolute top-0 left-0 bottom-0 overflow-hidden bg-gray-50 border-r border-gray-200 text-gray-500 text-right pr-2 pt-[9px] pb-[9px] select-none w-[45px] z-10 font-mono text-sm leading-[1.4] whitespace-pre">
        {lineNumbers}
      </div>
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={onChange}
        onPaste={handlePaste}
        onScroll={handleScroll}
        className={`pl-[50px] font-mono text-sm leading-[1.4] ${className}`}
        placeholder={placeholder}
        style={{ resize: 'none' }}
        {...props}
      />
    </div>
  );
}
