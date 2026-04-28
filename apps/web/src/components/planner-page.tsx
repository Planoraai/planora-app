"use client";

import { FormEvent, useMemo, useState } from "react";

import { planTrip } from "@/lib/api";
import type { TripPlanResponse } from "@/types/planner";

type PlanningState = "idle" | "loading" | "success" | "validation_failure" | "error";

const DEFAULT_PROMPT =
  "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds.";

export function PlannerPage() {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [state, setState] = useState<PlanningState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<TripPlanResponse | null>(null);

  const badgeText = useMemo(() => {
    if (state === "loading") return "Planning in progress";
    if (state === "success") return "Final itinerary ready";
    if (state === "validation_failure") return "Validation needs revision";
    if (state === "error") return "Request failed";
    return "Ready to plan";
  }, [state]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("loading");
    setError(null);
    setResponse(null);
    try {
      const { data } = await planTrip({ prompt });
      setResponse(data);
      setState(data.approved ? "success" : "validation_failure");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected request failure.";
      setError(message);
      setState("error");
    }
  }

  return (
    <main className="min-h-screen bg-[#f4f8ff] text-slate-900">
      <div className="mx-auto w-full max-w-[1500px] px-5 py-4">
        <header className="flex items-center justify-between rounded-2xl bg-white px-5 py-3 shadow-sm">
          <div className="flex items-center gap-8">
            <p className="text-xl font-semibold text-brand-navy">Voyage AI</p>
            <nav className="flex items-center gap-5 text-sm text-slate-500">
              <span className="font-semibold text-brand-navy">Plan</span>
              <span>Trips</span>
              <span>Explore</span>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-brand-light px-3 py-1 text-xs font-medium text-brand-navy">
              {badgeText}
            </span>
            <Avatar letter="U" />
          </div>
        </header>

        <section className="mt-4 overflow-hidden rounded-3xl bg-white shadow-sm">
          <div className="relative h-[260px] w-full bg-[url('https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1500&q=80')] bg-cover bg-center">
            <div className="absolute inset-0 bg-slate-900/50" />
            <div className="relative z-10 mx-auto flex h-full max-w-3xl flex-col items-center justify-center px-6">
              <h2 className="text-5xl font-semibold text-white">Where to next?</h2>
              <form className="mt-6 flex w-full items-center gap-3 rounded-2xl bg-white p-2 shadow-xl" onSubmit={onSubmit}>
                <span className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-500">*</span>
                <input
                  className="w-full border-none bg-transparent px-2 py-2 text-slate-900 outline-none"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Plan a 10-day trip to London and Paris..."
                />
                <button
                  type="submit"
                  disabled={state === "loading"}
                  className="rounded-xl bg-brand-navy px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                >
                  {state === "loading" ? "Planning..." : "Plan"}
                </button>
              </form>
            </div>
          </div>
        </section>

        <section className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <StatusCard
            title="Research Agent"
            active={state === "loading"}
            subtitle="Analyzing city signals and preference fit"
          />
          <StatusCard
            title="Budget Agent"
            active={state === "loading"}
            subtitle="Estimating category spend and budget flags"
          />
          <StatusCard
            title="Preference Agent"
            active={state === "loading"}
            subtitle="Aligning itinerary with avoidances and priorities"
          />
        </section>

        {error ? <section className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</section> : null}

        {response?.itinerary ? (
          <section className="mt-4 grid grid-cols-1 gap-5 lg:grid-cols-[330px,1fr]">
            <aside className="space-y-4">
              <div className="overflow-hidden rounded-2xl bg-white shadow-sm">
                <div className="h-36 bg-[url('https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=900&q=80')] bg-cover bg-center" />
                <div className="p-4">
                  <h3 className="text-[30px] leading-tight font-semibold text-slate-900">{response.itinerary.title}</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    {response.itinerary.trip_brief.duration_days} days · {response.itinerary.trip_brief.cities.length} travelers
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {response.itinerary.trip_brief.cities.join(" + ")}
                  </p>
                </div>
              </div>

              <div className="rounded-2xl bg-white p-4 shadow-sm">
                <h4 className="text-xs font-semibold tracking-wide text-slate-400">MAP ROUTE</h4>
                <div className="mt-3 rounded-xl bg-slate-200 p-4">
                  <div className="h-44 rounded-lg bg-gradient-to-br from-slate-700 to-slate-500 p-4">
                    <div className="flex h-full items-center justify-between">
                      <Dot color="bg-blue-400" />
                      <div className="h-[2px] w-full bg-white/40" />
                      <Dot color="bg-orange-400" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl bg-brand-navy p-4 text-white shadow-sm">
                <h4 className="text-lg font-semibold">Budget Insight</h4>
                <p className="mt-1 text-sm text-blue-100">Estimated Total</p>
                <p className="mt-1 text-4xl font-bold">
                  ${response.itinerary.budget_report.total_estimate_usd.toFixed(2)}
                </p>
                <div className="mt-3 h-2 rounded-full bg-white/30">
                  <div className="h-2 rounded-full bg-brand-accent" style={{ width: "74%" }} />
                </div>
                <p className="mt-3 text-xs text-blue-100">
                  {response.itinerary.budget_report.within_budget
                    ? "On track with your budget target."
                    : "Over budget: review requested changes."}
                </p>
              </div>

              <div className="rounded-2xl bg-white p-4 shadow-sm">
                <h4 className="text-sm font-semibold text-slate-600">Trip Constraints</h4>
                <p className="mt-2 text-sm text-slate-500">
                  {response.itinerary.trip_brief.duration_days} days ·{" "}
                  {response.itinerary.trip_brief.cities.join(" + ")}
                </p>
                <p className="mt-3 rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700">
                  Budget target: ${response.itinerary.trip_brief.budget_usd.toFixed(2)}
                </p>
              </div>

              {!response.approved ? (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-900 shadow-sm">
                  <h4 className="font-semibold">Validation feedback</h4>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                    {response.review.requested_changes.map((change) => (
                      <li key={change}>{change}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </aside>

            <article className="rounded-2xl bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <h3 className="text-[44px] leading-none font-semibold text-brand-navy">Itinerary Details</h3>
                <div className="flex gap-2">
                  <button className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-500">DL</button>
                  <button className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-500">SH</button>
                </div>
              </div>
              <div className="mt-5 space-y-4">
                {response.itinerary.day_by_day.map((day) => (
                  <div key={`${day.day}-${day.city}`} className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-2xl font-semibold text-slate-800">
                        Day {day.day}: {day.city}
                      </h4>
                      <span className="rounded-full bg-[#fff2e8] px-3 py-1 text-xs font-medium text-[#c06b29]">
                        {day.city}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{day.summary}</p>
                    <div className="mt-3 grid gap-3 md:grid-cols-2">
                      {day.highlights.map((highlight) => (
                        <div key={highlight} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
                          {highlight}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        ) : null}
      </div>
    </main>
  );
}

function StatusCard(props: { title: string; subtitle: string; active: boolean }) {
  return (
    <div
      className={`rounded-2xl border bg-white p-4 shadow-sm transition ${
        props.active ? "border-[#ff9a3d] shadow-[0_0_0_2px_rgba(255,154,61,0.12)]" : "border-slate-200"
      }`}
    >
      <p className="text-base font-semibold">{props.title}</p>
      <p className="mt-1 text-sm text-slate-500">{props.subtitle}</p>
    </div>
  );
}

function Avatar(props: { letter: string }) {
  return (
    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-navy text-sm font-semibold text-white">
      {props.letter}
    </div>
  );
}

function Dot(props: { color: string }) {
  return <span className={`h-3 w-3 rounded-full border-2 border-white ${props.color}`} />;
}
