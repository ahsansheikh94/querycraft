import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  AuthResponse, 
  Project, 
  Schema, 
  Query, 
  QueryGenerationRequest,
  QueryGenerationResponse,
  SchemaInput,
  ApiResponse,
  PaginatedResponse,
  ProjectStats,
  QueryStats,
  SchemaSummary
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await this.api.post('/auth/register', {
      username,
      email,
      password,
    });
    return response.data.data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response: AxiosResponse<ApiResponse<AuthResponse>> = await this.api.post('/auth/login', {
      email,
      password,
    });
    return response.data.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<ApiResponse<{ user: User }>> = await this.api.get('/auth/me');
    return response.data.data.user;
  }

  async refreshToken(): Promise<{ access_token: string }> {
    const response: AxiosResponse<ApiResponse<{ access_token: string }>> = await this.api.post('/auth/refresh');
    return response.data.data;
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response: AxiosResponse<ApiResponse<{ user: User }>> = await this.api.put('/auth/profile', data);
    return response.data.data.user;
  }

  // Project endpoints
  async createProject(name: string, description?: string): Promise<Project> {
    const response: AxiosResponse<ApiResponse<{ project: Project }>> = await this.api.post('/projects', {
      name,
      description,
    });
    return response.data.data.project;
  }

  async getProjects(page = 1, perPage = 10): Promise<PaginatedResponse<Project>> {
    const response: AxiosResponse<ApiResponse<{ projects: Project[]; pagination: any }>> = await this.api.get('/projects', {
      params: { page, per_page: perPage },
    });
    return {
      data: response.data.data.projects,
      pagination: response.data.data.pagination,
    };
  }

  async getProject(id: string): Promise<Project> {
    const response: AxiosResponse<ApiResponse<{ project: Project }>> = await this.api.get(`/projects/${id}`);
    return response.data.data.project;
  }

  async updateProject(id: string, name: string, description?: string): Promise<Project> {
    const response: AxiosResponse<ApiResponse<{ project: Project }>> = await this.api.put(`/projects/${id}`, {
      name,
      description,
    });
    return response.data.data.project;
  }

  async deleteProject(id: string): Promise<void> {
    await this.api.delete(`/projects/${id}`);
  }

  async getProjectStats(id: string): Promise<ProjectStats> {
    const response: AxiosResponse<ApiResponse<{ stats: ProjectStats }>> = await this.api.get(`/projects/${id}/stats`);
    return response.data.data.stats;
  }

  // Schema endpoints
  async createSchema(projectId: string, schemas: SchemaInput[]): Promise<{ schemas: Schema[]; schema_count: number }> {
    const response: AxiosResponse<ApiResponse<{ schemas: Schema[]; schema_count: number }>> = await this.api.post(`/projects/${projectId}/schema`, {
      schemas,
    });
    return response.data.data;
  }

  async getSchemas(projectId: string): Promise<{ schemas: Schema[]; summary: SchemaSummary }> {
    const response: AxiosResponse<ApiResponse<{ schemas: Schema[]; summary: SchemaSummary }>> = await this.api.get(`/projects/${projectId}/schema`);
    return response.data.data;
  }

  async updateSchema(projectId: string, schemas: SchemaInput[]): Promise<{ schemas: Schema[]; schema_count: number }> {
    const response: AxiosResponse<ApiResponse<{ schemas: Schema[]; schema_count: number }>> = await this.api.put(`/projects/${projectId}/schema`, {
      schemas,
    });
    return response.data.data;
  }

  async deleteSchema(projectId: string, schemaId: string): Promise<void> {
    await this.api.delete(`/projects/${projectId}/schema/${schemaId}`);
  }

  async getSchemaSummary(projectId: string): Promise<SchemaSummary> {
    const response: AxiosResponse<ApiResponse<{ summary: SchemaSummary }>> = await this.api.get(`/projects/${projectId}/schema/summary`);
    return response.data.data.summary;
  }

  // Query endpoints
  async generateQuery(projectId: string, userInput: string): Promise<QueryGenerationResponse> {
    const response: AxiosResponse<ApiResponse<QueryGenerationResponse>> = await this.api.post(`/projects/${projectId}/query`, {
      user_input: userInput,
    });
    return response.data.data;
  }

  async getQueries(projectId: string, page = 1, perPage = 10, search?: string): Promise<PaginatedResponse<Query>> {
    const params: any = { page, per_page: perPage };
    if (search) params.search = search;

    const response: AxiosResponse<ApiResponse<{ queries: Query[]; pagination: any; search_term?: string }>> = await this.api.get(`/projects/${projectId}/queries`, { params });
    return {
      data: response.data.data.queries,
      pagination: response.data.data.pagination,
    };
  }

  async getQuery(id: string): Promise<Query> {
    const response: AxiosResponse<ApiResponse<{ query: Query }>> = await this.api.get(`/queries/${id}`);
    return response.data.data.query;
  }

  async explainQuery(id: string): Promise<{ detailed_explanation: string }> {
    const response: AxiosResponse<ApiResponse<{ detailed_explanation: string }>> = await this.api.get(`/queries/${id}/explain`);
    return response.data.data;
  }

  async suggestImprovements(id: string): Promise<{ suggestions: string[] }> {
    const response: AxiosResponse<ApiResponse<{ suggestions: string[] }>> = await this.api.get(`/queries/${id}/improve`);
    return response.data.data;
  }

  async deleteQuery(id: string): Promise<void> {
    await this.api.delete(`/queries/${id}`);
  }

  async getQueryStats(projectId: string): Promise<{ stats: QueryStats; recent_queries: Query[] }> {
    const response: AxiosResponse<ApiResponse<{ stats: QueryStats; recent_queries: Query[] }>> = await this.api.get(`/projects/${projectId}/queries/stats`);
    return response.data.data;
  }
}

export const apiService = new ApiService();
export default apiService;
