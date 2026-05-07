"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { supabase } from "@/lib/supabase";

type AuthTemplateProps = {
  mode: "sign-in" | "sign-up";
  nextPath?: string;
};

const signInHero =
  "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1400&q=80";
const signUpHero =
  "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=80";

export function AuthTemplate(props: AuthTemplateProps) {
  const isSignIn = props.mode === "sign-in";
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    if (!password.trim()) {
      setError("Password is required.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setError(null);
    setNotice(null);
    setIsSubmitting(true);
    try {
      if (isSignIn) {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim().toLowerCase(),
          password,
        });
        if (signInError) throw signInError;
      } else {
        const { data, error: signUpError } = await supabase.auth.signUp({
          email: email.trim().toLowerCase(),
          password,
          options: {
            emailRedirectTo:
              typeof window !== "undefined" ? `${window.location.origin}/sign-in?next=/` : undefined,
          },
        });
        if (signUpError) throw signUpError;
        if (!data.session) {
          setNotice("Account created. Check your email to verify your account, then sign in.");
          return;
        }
      }
      router.push(props.nextPath || "/");
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : "Authentication failed.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#efefef] text-[#121212]">
      <div className="mx-auto flex min-h-screen w-full max-w-[1440px] flex-col bg-white">
        <header className="flex h-[62px] items-center justify-between border-b border-[#ececec] px-4 sm:px-5 lg:px-7">
          <div className="flex items-center gap-8">
            <span className="text-[28px] font-semibold tracking-[-0.02em]">Planora</span>
            {isSignIn ? (
              <nav className="hidden items-center gap-5 text-[15px] text-[#556070] lg:flex">
                <span>Destinations</span>
                <span>AI Planner</span>
                <span>Experiences</span>
                <span>Support</span>
              </nav>
            ) : null}
          </div>
          {!isSignIn ? (
            <Link href="/sign-in" className="text-sm font-medium text-[#101010] sm:text-sm">
              Sign In
            </Link>
          ) : <span />}
        </header>

        <section className="grid flex-1 grid-cols-1 lg:grid-cols-2">
          <aside
            className="relative hidden min-h-[420px] overflow-hidden lg:block"
            style={{
              backgroundImage: `linear-gradient(rgba(7, 15, 35, 0.38), rgba(7, 15, 35, 0.48)), url(${
                isSignIn ? signInHero : signUpHero
              })`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            {isSignIn ? (
              <div className="absolute left-1/2 top-[46%] w-[76%] max-w-[480px] -translate-x-1/2 rounded-2xl border border-white/35 bg-white/12 p-5 text-center text-white backdrop-blur-[8px]">
                <p className="text-base font-semibold tracking-[0.2em]">PLANORA</p>
                <h2 className="mt-2 text-[30px] font-semibold leading-tight xl:text-3xl">Your next journey starts here.</h2>
                <p className="mt-3 text-[15px] leading-snug text-white/90 xl:text-base">
                  Experience travel curated by the world&apos;s most intelligent AI agents.
                </p>
              </div>
            ) : (
              <div className="absolute bottom-12 left-10 right-10 text-white">
                <h2 className="max-w-[520px] text-[34px] font-semibold leading-[1.02] xl:text-[42px]">Join the future of travel.</h2>
                <p className="mt-4 max-w-[560px] text-lg leading-snug text-white/90 xl:text-xl">
                  Experience hyper-personalized itineraries powered by AI agents that understand your unique travel
                  soul.
                </p>
              </div>
            )}
          </aside>

          <div className="flex items-center justify-center px-5 py-7 sm:px-7 lg:px-9">
            <div className="w-full max-w-[460px]">
              <h1 className="text-[44px] font-semibold leading-tight">{isSignIn ? "Welcome back" : "Create your account"}</h1>
              <p className="mt-1.5 text-[18px] text-[#606d7a]">
                {isSignIn
                  ? "Enter your details to access your AI-powered itineraries."
                  : "Start your journey with Planora today."}
              </p>

              <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button className="flex h-11 items-center justify-center gap-2 rounded-xl border border-[#d9d9d9] text-[15px]">
                  <span className="inline-block h-5 w-5 rounded-full border border-[#111] text-[11px] leading-5">G</span>
                  Google
                </button>
                <button className="flex h-11 items-center justify-center gap-2 rounded-xl border border-[#d9d9d9] text-[15px]">
                  <span className="text-xl">A</span>
                  Apple
                </button>
              </div>

              <div className="my-4 flex items-center gap-4 text-[11px] text-[#8c95a0] sm:text-xs">
                <span className="h-px flex-1 bg-[#e6e6e6]" />
                <span>{isSignIn ? "OR CONTINUE WITH EMAIL" : "OR"}</span>
                <span className="h-px flex-1 bg-[#e6e6e6]" />
              </div>

              <form className="space-y-4" onSubmit={onSubmit}>
                {!isSignIn ? <Field label="Full Name" placeholder="John Doe" /> : null}
                <Field
                  label={isSignIn ? "EMAIL ADDRESS" : "Email Address"}
                  placeholder={isSignIn ? "name@company.com" : "john@example.com"}
                  value={email}
                  onChange={setEmail}
                />
                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <label className="text-[17px] tracking-wide text-[#2a2a2a]">{isSignIn ? "PASSWORD" : "Password"}</label>
                    <div className="flex items-center gap-3">
                      {isSignIn ? (
                        <a href="#" className="text-sm text-[#946e52]">
                          Forgot password?
                        </a>
                      ) : null}
                      <button
                        type="button"
                        onClick={() => setShowPassword((prev) => !prev)}
                        aria-label={showPassword ? "Hide password" : "Show password"}
                        title={showPassword ? "Hide password" : "Show password"}
                        className="text-[#475467] hover:text-[#1f2937]"
                      >
                        {showPassword ? (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                            <path
                              d="M3 3L21 21M10.58 10.59A2 2 0 0013.41 13.41M9.88 5.08A10.94 10.94 0 0112 5c5 0 9.27 3.11 11 7-0.66 1.49-1.76 2.92-3.15 4.1M6.1 6.1C3.91 7.44 2.33 9.58 1 12c1.73 3.89 6 7 11 7 2.06 0 3.99-0.53 5.65-1.46"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        ) : (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                            <path
                              d="M1 12C2.73 8.11 7 5 12 5s9.27 3.11 11 7c-1.73 3.89-6 7-11 7S2.73 15.89 1 12z"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                            <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete={isSignIn ? "current-password" : "new-password"}
                    className="h-11 w-full rounded-xl border border-[#dcdcdc] px-4 text-base text-[#6d7278] outline-none"
                  />
                  {!isSignIn ? (
                    <p className="mt-1 text-xs text-[#667085]">
                      Use at least 8 characters. Strong passwords include upper/lowercase, numbers, and symbols.
                    </p>
                  ) : null}
                </div>

                {!isSignIn ? (
                  <label className="flex items-center gap-3 text-sm text-[#555d67]">
                    <input type="checkbox" className="h-5 w-5 rounded border border-[#c7c7c7]" />
                    <span>
                      I agree to the <a href="#" className="text-[#8a6647]">Terms and Conditions</a> and{" "}
                      <a href="#" className="text-[#8a6647]">Privacy Policy</a>.
                    </span>
                  </label>
                ) : null}

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="mt-1 h-11 w-full rounded-xl bg-[#02173d] text-lg font-semibold text-white shadow-[0_7px_16px_rgba(2,23,61,0.2)]"
                >
                  {isSubmitting ? "Please wait..." : isSignIn ? "Sign In  ->" : "Create Account"}
                </button>
                {error ? <p className="text-sm text-red-600">{error}</p> : null}
                {notice ? <p className="text-sm text-green-700">{notice}</p> : null}
              </form>

              <p className="mt-7 text-center text-base text-[#525b66]">
                {isSignIn ? "Don't have an account? " : "Already have an account? "}
                <Link href={isSignIn ? "/sign-up" : "/sign-in"} className="font-semibold text-[#232323]">
                  {isSignIn ? "Sign Up" : "Sign In"}
                </Link>
              </p>
            </div>
          </div>
        </section>

        {isSignIn ? (
          <footer className="flex flex-col gap-4 border-t border-[#ececec] px-5 py-5 text-sm text-[#747c87] sm:px-8 sm:text-sm lg:flex-row lg:items-end lg:justify-between lg:px-10">
            <div>
              <p className="text-2xl font-semibold text-[#131313]">Planora</p>
              <p className="mt-3">(c) 2024 Planora Technologies. All rights reserved.</p>
            </div>
            <div className="flex flex-wrap gap-x-6 gap-y-2 lg:justify-end">
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
              <a href="#">Cookie Settings</a>
              <a href="#">Help Center</a>
            </div>
          </footer>
        ) : (
          <footer className="flex flex-col items-center justify-between gap-4 border-t border-[#ececec] px-5 py-5 text-sm text-[#747c87] sm:px-8 sm:text-sm lg:flex-row lg:px-10">
            <p className="text-2xl font-semibold text-[#131313]">Planora</p>
            <div className="flex flex-wrap justify-center gap-x-6 gap-y-2">
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
              <a href="#">Cookie Settings</a>
              <a href="#">Help Center</a>
            </div>
            <p>(c) 2024 Planora Technologies. All rights reserved.</p>
          </footer>
        )}
      </div>
    </main>
  );
}

function Field(props: { label: string; placeholder: string; value?: string; onChange?: (value: string) => void }) {
  return (
    <div>
      <label className="mb-2 block text-[17px] tracking-wide text-[#2a2a2a]">{props.label}</label>
      <input
        type="text"
        placeholder={props.placeholder}
        value={props.value}
        onChange={(event) => props.onChange?.(event.target.value)}
        className="h-11 w-full rounded-xl border border-[#dcdcdc] px-4 text-base text-[#6d7278] outline-none placeholder:text-[#c3c7cc]"
      />
    </div>
  );
}
