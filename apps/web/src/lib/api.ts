import type { TripPlanRequest, TripPlanResponse } from "@/types/planner";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function planTrip(
  payload: TripPlanRequest,
): Promise<{ data: TripPlanResponse; correlationId: string | null }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/trips/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  const data = (await response.json()) as TripPlanResponse;
  const correlationId = response.headers.get("x-correlation-id");
  return { data, correlationId };
}
