"use client";

import { Search } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function SearchBox({
  initialValue = "",
  large = false,
  onSearch,
}: {
  initialValue?: string;
  large?: boolean;
  onSearch?: (query: string) => void | Promise<void>;
}) {
  const [value, setValue] = useState(initialValue);
  const router = useRouter();

  useEffect(() => setValue(initialValue), [initialValue]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const query = value.trim();
    if (onSearch) {
      await onSearch(query);
      return;
    }
    router.push(query ? `/search/?q=${encodeURIComponent(query)}` : "/search/");
  }

  return (
    <form className={large ? "search-box large" : "search-box"} onSubmit={submit}>
      <Search size={22} aria-hidden="true" />
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Search a product, brand, ingredient or barcode"
        aria-label="Search food"
      />
      <button className="button" type="submit">Search</button>
    </form>
  );
}
