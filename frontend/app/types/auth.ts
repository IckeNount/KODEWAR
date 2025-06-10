export interface User {
  id: string;
  username: string;
  email: string;
  credits: number;
  level: number;
  experience: number;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  username: string;
}
