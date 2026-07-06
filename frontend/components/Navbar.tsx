"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Heart, History, LogIn, LogOut, ScanLine, Search, UserRound } from "lucide-react";
import { useEffect, useState } from "react";

import { logout } from "@/lib/auth";
import { getAccessToken } from "@/lib/storage";

const links = [
  { href: "/search/", label: "Search", icon: Search },
  { href: "/scan/", label: "Scan", icon: ScanLine },
  { href: "/history/", label: "History", icon: History },
  { href: "/favorites/", label: "Saved", icon: Heart },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    const check = () => getAccessToken().then((token) => setSignedIn(Boolean(token)));
    void check();
    window.addEventListener("auth-changed", check);
    return () => window.removeEventListener("auth-changed", check);
  }, []);

  async function signOut() {
    await logout();
    setSignedIn(false);
    router.push("/");
  }

  return (
    <>
      <header className="topbar">
        <Link className="brand" href="/" aria-label="HalalFit home">
          <span className="brand-mark">H</span>
          <span>
            <strong>HalalFit</strong>
            <small>Halal and healthy food assistant</small>
          </span>
        </Link>
        <nav className="desktop-nav" aria-label="Main navigation">
          {links.map(({ href, label, icon: Icon }) => (
            <Link className={pathname.startsWith(href) ? "nav-link active" : "nav-link"} href={href} key={href}>
              <Icon size={18} /> {label}
            </Link>
          ))}
        </nav>
        <div className="account-actions">
          {signedIn ? (
            <>
              <Link className="icon-button" href="/profile/" aria-label="Profile">
                <UserRound size={20} />
              </Link>
              <button className="icon-button" onClick={signOut} aria-label="Sign out">
                <LogOut size={20} />
              </button>
            </>
          ) : (
            <Link className="button small" href="/login/">
              <LogIn size={17} /> Sign in
            </Link>
          )}
        </div>
      </header>
      <nav className="bottom-nav" aria-label="Mobile navigation">
        {links.map(({ href, label, icon: Icon }) => (
          <Link className={pathname.startsWith(href) ? "active" : ""} href={href} key={href}>
            <Icon size={21} />
            <span>{label}</span>
          </Link>
        ))}
        <Link className={pathname.startsWith("/profile") ? "active" : ""} href={signedIn ? "/profile/" : "/login/"}>
          <UserRound size={21} />
          <span>{signedIn ? "Profile" : "Sign in"}</span>
        </Link>
      </nav>
    </>
  );
}
