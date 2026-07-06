"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  CircleHelp,
  Heart,
  History,
  Home,
  Info,
  ListChecks,
  LogIn,
  LogOut,
  Menu,
  ScanLine,
  Search,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";

import { logout } from "@/lib/auth";
import { getAccessToken } from "@/lib/storage";

const desktopLinks = [
  { href: "/search/", label: "Search", icon: Search },
  { href: "/scan/", label: "Scan", icon: ScanLine },
  { href: "/ingredients/", label: "Ingredients", icon: ListChecks },
  { href: "/history/", label: "History", icon: History },
  { href: "/favorites/", label: "Saved", icon: Heart },
];

const mobileLinks = [
  { href: "/", label: "Home", icon: Home },
  { href: "/search/", label: "Search", icon: Search },
  { href: "/scan/", label: "Scan", icon: ScanLine },
  { href: "/ingredients/", label: "Check", icon: ListChecks },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [signedIn, setSignedIn] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const check = () => getAccessToken().then((token) => setSignedIn(Boolean(token)));
    void check();
    window.addEventListener("auth-changed", check);
    return () => window.removeEventListener("auth-changed", check);
  }, []);

  useEffect(() => setOpen(false), [pathname]);

  async function signOut() {
    await logout();
    setSignedIn(false);
    setOpen(false);
    router.push("/");
  }

  const isActive = (href: string) => href === "/" ? pathname === "/" : pathname.startsWith(href);

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
          {desktopLinks.map(({ href, label, icon: Icon }) => (
            <Link className={isActive(href) ? "nav-link active" : "nav-link"} href={href} key={href}>
              <Icon size={18} /> {label}
            </Link>
          ))}
        </nav>
        <div className="account-actions">
          {signedIn ? (
            <>
              <Link className="icon-button" href="/profile/" aria-label="Profile"><UserRound size={20} /></Link>
              <button className="icon-button" onClick={signOut} aria-label="Sign out"><LogOut size={20} /></button>
            </>
          ) : (
            <Link className="button small" href="/login/"><LogIn size={17} /> Sign in</Link>
          )}
        </div>
        <button className="mobile-menu-button" onClick={() => setOpen((value) => !value)} aria-label="Open navigation" aria-expanded={open}>
          {open ? <X /> : <Menu />}
        </button>
      </header>

      {open && (
        <div className="mobile-drawer" role="dialog" aria-label="Mobile navigation">
          <div className="mobile-drawer-grid">
            <Link href="/history/"><History /> <span>Scan history</span></Link>
            <Link href="/favorites/"><Heart /> <span>Saved products</span></Link>
            <Link href="/about/"><Info /> <span>About HalalFit</span></Link>
            <Link href="/contact/"><CircleHelp /> <span>Contact support</span></Link>
          </div>
          {signedIn ? (
            <button className="button danger full" onClick={signOut}><LogOut /> Sign out</button>
          ) : (
            <Link className="button full" href="/login/"><LogIn /> Sign in</Link>
          )}
        </div>
      )}

      <nav className="bottom-nav" aria-label="Mobile primary navigation">
        {mobileLinks.map(({ href, label, icon: Icon }) => (
          <Link className={isActive(href) ? "active" : ""} href={href} key={href}>
            <Icon size={21} /><span>{label}</span>
          </Link>
        ))}
        <Link className={pathname.startsWith("/profile") || pathname.startsWith("/login") ? "active" : ""} href={signedIn ? "/profile/" : "/login/"}>
          <UserRound size={21} /><span>{signedIn ? "Profile" : "Sign in"}</span>
        </Link>
      </nav>
    </>
  );
}
