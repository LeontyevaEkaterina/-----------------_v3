export interface UserMe {
  id: number;
  email: string;
  name: string | null;
  avatar_url: string | null;
  role: string;
  default_system_prompt: string | null;
  default_temperature: number | null;
  default_max_tokens: number | null;
  theme: string;
  created_at: string;
  updated_at: string;
}

