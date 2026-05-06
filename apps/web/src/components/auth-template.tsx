"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { setAuthSession } from "@/lib/usage";

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
  const [error, setError] = useState<string | null>(null);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    setAuthSession(email);
    router.push(props.nextPath || "/");
  }

  return (
    <main className="min-h-screen bg-[#efefef] text-[#121212]">
      <div className="mx-auto flex min-h-screen w-full max-w-[1440px] flex-col bg-white">
        <header className="flex h-[68px] items-center justify-between border-b border-[#ececec] px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-8">
            <span className="text-3xl font-semibold tracking-[-0.02em]">Planora</span>
            {isSignIn ? (
              <nav className="hidden items-center gap-6 text-base text-[#556070] lg:flex">
                <span>Destinations</span>
                <span>AI Planner</span>
                <span>Experiences</span>
                <span>Support</span>
              </nav>
            ) : null}
          </div>
          {isSignIn ? (
            <button className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white sm:px-5 sm:text-base">
              Sign In
            </button>
          ) : (
            <Link href="/sign-in" className="text-sm font-medium text-[#101010] sm:text-base">
              Sign In
            </Link>
          )}
        </header>

        <section className="grid flex-1 grid-cols-1 lg:grid-cols-2">
          <aside
            className="relative hidden min-h-[460px] overflow-hidden lg:block"
            style={{
              backgroundImage: `linear-gradient(rgba(7, 15, 35, 0.38), rgba(7, 15, 35, 0.48)), url(${
                isSignIn ? signInHero : signUpHero
              })`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            {isSignIn ? (
              <div className="absolute left-1/2 top-[46%] w-[78%] max-w-[520px] -translate-x-1/2 rounded-2xl border border-white/35 bg-white/12 p-6 text-center text-white backdrop-blur-[8px]">
                <p className="text-lg font-semibold tracking-[0.2em]">VOYAGE</p>
                <h2 className="mt-3 text-3xl font-semibold leading-tight xl:text-4xl">Your next journey starts here.</h2>
                <p className="mt-4 text-base leading-snug text-white/90 xl:text-lg">
                  Experience travel curated by the world&apos;s most intelligent AI agents.
                </p>
              </div>
            ) : (
              <div className="absolute bottom-12 left-10 right-10 text-white">
                <h2 className="max-w-[520px] text-4xl font-semibold leading-[1.02] xl:text-5xl">Join the future of travel.</h2>
                <p className="mt-5 max-w-[560px] text-xl leading-snug text-white/90 xl:text-2xl">
                  Experience hyper-personalized itineraries powered by AI agents that understand your unique travel
                  soul.
                </p>
              </div>
            )}
          </aside>

          <div className="flex items-center justify-center px-5 py-8 sm:px-8 lg:px-10">
            <div className="w-full max-w-[500px]">
              <h1 className="text-3xl font-semibold leading-tight sm:text-4xl">{isSignIn ? "Welcome back" : "Create your account"}</h1>
              <p className="mt-2 text-base text-[#606d7a] sm:text-lg">
                {isSignIn
                  ? "Enter your details to access your AI-powered itineraries."
                  : "Start your journey with Planora today."}
              </p>

              <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button className="flex h-12 items-center justify-center gap-2 rounded-xl border border-[#d9d9d9] text-base">
                  <span className="inline-block h-5 w-5 rounded-full border border-[#111] text-[11px] leading-5">G</span>
                  Google
                </button>
                <button className="flex h-12 items-center justify-center gap-2 rounded-xl border border-[#d9d9d9] text-base">
                  <span className="text-xl">A</span>
                  Apple
                </button>
              </div>

              <div className="my-5 flex items-center gap-4 text-xs text-[#8c95a0] sm:text-sm">
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
                    <label className="text-base tracking-wide text-[#2a2a2a] sm:text-lg">{isSignIn ? "PASSWORD" : "Password"}</label>
                    {isSignIn ? (
                      <a href="#" className="text-sm text-[#946e52] sm:text-base">
                        Forgot password?
                      </a>
                    ) : null}
                  </div>
                  <input
                    type="password"
                    defaultValue="password"
                    className="h-12 w-full rounded-xl border border-[#dcdcdc] px-4 text-base text-[#6d7278] outline-none sm:text-lg"
                  />
                </div>

                {!isSignIn ? (
                  <label className="flex items-center gap-3 text-sm text-[#555d67] sm:text-base">
                    <input type="checkbox" className="h-5 w-5 rounded border border-[#c7c7c7]" />
                    <span>
                      I agree to the <a href="#" className="text-[#8a6647]">Terms and Conditions</a> and{" "}
                      <a href="#" className="text-[#8a6647]">Privacy Policy</a>.
                    </span>
                  </label>
                ) : null}

                <button
                  type="submit"
                  className="mt-1 h-12 w-full rounded-xl bg-[#02173d] text-lg font-semibold text-white shadow-[0_7px_16px_rgba(2,23,61,0.2)] sm:text-xl"
                >
                  {isSignIn ? "Sign In  ->" : "Create Account"}
                </button>
                {error ? <p className="text-sm text-red-600">{error}</p> : null}
              </form>

              <p className="mt-8 text-center text-base text-[#525b66] sm:text-lg">
                {isSignIn ? "Don't have an account? " : "Already have an account? "}
                <Link href={isSignIn ? "/sign-up" : "/sign-in"} className="font-semibold text-[#232323]">
                  {isSignIn ? "Sign Up" : "Sign In"}
                </Link>
              </p>
            </div>
          </div>
        </section>

        {isSignIn ? (
          <footer className="flex flex-col gap-4 border-t border-[#ececec] px-5 py-6 text-sm text-[#747c87] sm:px-8 sm:text-base lg:flex-row lg:items-end lg:justify-between lg:px-10">
            <div>
              <p className="text-2xl font-semibold text-[#131313] sm:text-3xl">Planora</p>
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
          <footer className="flex flex-col items-center justify-between gap-4 border-t border-[#ececec] px-5 py-6 text-sm text-[#747c87] sm:px-8 sm:text-base lg:flex-row lg:px-10">
            <p className="text-2xl font-semibold text-[#131313] sm:text-3xl">Planora</p>
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
      <label className="mb-2 block text-base tracking-wide text-[#2a2a2a] sm:text-lg">{props.label}</label>
      <input
        type="text"
        placeholder={props.placeholder}
        value={props.value}
        onChange={(event) => props.onChange?.(event.target.value)}
        className="h-12 w-full rounded-xl border border-[#dcdcdc] px-4 text-base text-[#6d7278] outline-none placeholder:text-[#c3c7cc] sm:text-lg"
      />
    </div>
  );
}
