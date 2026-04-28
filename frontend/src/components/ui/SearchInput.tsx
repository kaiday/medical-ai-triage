import { Search } from 'lucide-react';

interface SearchInputProps {
  placeholder?: string;
}

export function SearchInput({ placeholder = 'Search here...' }: SearchInputProps) {
  return (
    <label className="flex h-12 w-full max-w-[630px] items-center gap-3 rounded-lg bg-white px-4 text-ink-500 shadow-sm">
      <Search aria-hidden="true" size={20} strokeWidth={2} />
      <span className="sr-only">Search</span>
      <input
        className="w-full border-0 bg-transparent text-sm font-medium text-ink-700 outline-none placeholder:text-ink-500"
        placeholder={placeholder}
        type="search"
      />
    </label>
  );
}
