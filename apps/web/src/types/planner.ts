export type TripPlanRequest = {
  prompt: string;
};

export type TripBrief = {
  destination_country: string;
  cities: string[];
  duration_days: number;
  budget_usd: number;
  preferences: string[];
  avoidances: string[];
};

export type ItineraryDay = {
  day: number;
  city: string;
  summary: string;
  highlights: string[];
};

export type BudgetReport = {
  total_estimate_usd: number;
  by_category: {
    stay: number;
    transport: number;
    food: number;
    activities: number;
    buffer: number;
  };
  flags: { issue: string; suggestion: string }[];
  within_budget: boolean;
};

export type LogisticsPlan = {
  stay_plan: { city: string; nights: number; area: string }[];
  intercity: { from_city: string; to_city: string; mode: string; duration_min: number }[];
  day_skeleton: {
    day: number;
    city: string;
    blocks: { period: string; activity: string }[];
  }[];
};

export type Itinerary = {
  title: string;
  trip_brief: TripBrief;
  logistics_plan: LogisticsPlan;
  budget_report: BudgetReport;
  day_by_day: ItineraryDay[];
  notes: string[];
};

export type Review = {
  approved: boolean;
  issues: string[];
  requested_changes: string[];
};

export type TripPlanResponse = {
  approved: boolean;
  itinerary: Itinerary;
  review: Review;
};
