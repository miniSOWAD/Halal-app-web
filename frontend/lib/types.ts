export type HalalStatus =
  | "CERTIFIED_HALAL"
  | "NO_PROHIBITED_INGREDIENT_FOUND"
  | "HARAM"
  | "DOUBTFUL"
  | "UNKNOWN";

export type HealthStatus = "HEALTHY" | "MODERATE" | "UNHEALTHY" | "UNKNOWN";

export interface User {
  id: string;
  name: string;
  email: string;
  country?: string | null;
  phone?: string | null;
  email_verified: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface OTPResponse {
  message: string;
  email: string;
  expires_in_seconds: number;
  resend_in_seconds: number;
}

export interface PasswordResetToken {
  reset_token: string;
  expires_in_seconds: number;
}

export interface Certification {
  id: string;
  product_id: string;
  authority_name: string;
  certificate_number: string;
  country?: string | null;
  valid_from?: string | null;
  valid_until?: string | null;
  verification_url?: string | null;
  status: string;
}

export interface Product {
  id: string;
  name: string;
  brand?: string | null;
  category?: string | null;
  barcode?: string | null;
  country?: string | null;
  image_url?: string | null;
  ingredient_text?: string | null;
  nutrition_data?: Record<string, number | string | null>;
  halal_status: HalalStatus | string;
  halal_confidence: number;
  health_status: HealthStatus | string;
  health_score: number;
  explanation?: string | null;
  data_source?: string;
  certifications?: Certification[];
  created_at?: string;
  updated_at?: string;
}

export interface IngredientResult {
  name: string;
  status: string;
  health_status: string;
  reason: string;
  matched: boolean;
}

export interface RiskyIngredient {
  name: string;
  status: string;
  reason: string;
  matched_name?: string | null;
}

export interface AnalysisResult {
  scan_id: string;
  input_type: string;
  product?: {
    id?: string | null;
    name: string;
    brand?: string | null;
    barcode?: string | null;
    image_url?: string | null;
  } | null;
  extracted_text?: string | null;
  ingredients: IngredientResult[];
  halal: {
    status: HalalStatus;
    label: string;
    confidence: number;
    reasons: string[];
    risky_ingredients: RiskyIngredient[];
    certificate: {
      found: boolean;
      status: string;
      authority?: string | null;
      certificate_number?: string | null;
      valid_until?: string | null;
      verification_url?: string | null;
    };
  };
  health: {
    status: HealthStatus;
    score: number;
    confidence: number;
    reasons: string[];
  };
  recommendation: string;
  alternatives: Array<{
    id: string;
    name: string;
    brand?: string | null;
    image_url?: string | null;
    health_score: number;
    halal_status: string;
  }>;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  input_type: string;
  product?: Product | null;
  halal_status: string;
  halal_confidence: number;
  health_status: string;
  health_score: number;
  created_at: string;
}

export interface Ingredient {
  id: string;
  name: string;
  aliases: string[];
  e_number?: string | null;
  halal_status: string;
  health_status: string;
  source_dependent: boolean;
  risk_level: number;
  explanation: string;
  source?: string | null;
  created_at: string;
}

export interface Report {
  id: string;
  product_id?: string | null;
  subject: string;
  category: string;
  message: string;
  status: string;
  created_at: string;
}

export interface AdminDashboard {
  users: number;
  products: number;
  ingredients: number;
  scans: number;
  open_reports: number;
}
