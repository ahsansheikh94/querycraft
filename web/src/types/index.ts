// User types
export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  stats?: ProjectStats;
}

export interface ProjectStats {
  schema_count: number;
  query_count: number;
}

// Schema types
export interface Column {
  name: string;
  type: string;
  primary_key?: boolean;
  unique?: boolean;
  not_null?: boolean;
}

export interface TableSchema {
  columns: Column[];
}

export interface Schema {
  id: string;
  project_id: string;
  table_name: string;
  table_schema: TableSchema;
  created_at: string;
}

export interface SchemaInput {
  table_name: string;
  table_schema: TableSchema;
}

export interface SchemaSummary {
  total_tables: number;
  tables: {
    table_name: string;
    column_count: number;
    columns: string[];
  }[];
}

// Query types
export interface Query {
  id: string;
  project_id: string;
  user_input: string;
  generated_sql: string;
  explanation?: string;
  created_at: string;
}

export interface QueryGenerationRequest {
  user_input: string;
}

export interface QueryGenerationResponse {
  query: Query;
  generated_sql: string;
  explanation: string;
}

export interface QueryStats {
  total_queries: number;
  recent_queries: number;
  common_patterns: {
    _id: string;
    count: number;
  }[];
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface SignupForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ProjectForm {
  name: string;
  description?: string;
}

// UI types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}
