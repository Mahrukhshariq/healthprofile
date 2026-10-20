export interface Profile {
  id: number;
  full_name: string;
  date_of_birth: string | null;
  contact_preference: "email" | "phone" | "sms";
  wellness_goals: string;
  allergies: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  lifestyle_notes: string;
  status: "active" | "inactive";
  created_at: string;
  updated_at: string;
}

export interface AdminProfile extends Profile {
  user_email: string;
}

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}