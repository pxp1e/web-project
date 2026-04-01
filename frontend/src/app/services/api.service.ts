import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthResponse } from '../models/user.model';
import { Task, CreateTaskDto } from '../models/task.model';
import { Team } from '../models/team.model';
import { Subject } from '../models/subject.model';
import { Comment } from '../models/comment.model';
import { DashboardStats } from '../models/dashboard.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.base}/auth/login/`, { username, password });
  }

  register(data: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.base}/auth/register/`, data);
  }

  logout(refresh: string): Observable<any> {
    return this.http.post(`${this.base}/auth/logout/`, { refresh });
  }

  getStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.base}/dashboard/stats/`);
  }

  getMyTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.base}/tasks/my/`);
  }

  getTasks(teamId?: number): Observable<Task[]> {
    let params = new HttpParams();
    if (teamId) params = params.set('team_id', teamId.toString());
    return this.http.get<Task[]>(`${this.base}/tasks/`, { params });
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.base}/tasks/${id}/`);
  }

  createTask(task: CreateTaskDto): Observable<Task> {
    return this.http.post<Task>(`${this.base}/tasks/`, task);
  }

  updateTask(id: number, task: Partial<CreateTaskDto>): Observable<Task> {
    return this.http.put<Task>(`${this.base}/tasks/${id}/`, task);
  }

  updateTaskStatus(taskId: number, status: string): Observable<Task> {
    return this.http.patch<Task>(`${this.base}/tasks/update-status/`, { task_id: taskId, status });
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/tasks/${id}/`);
  }

  getTeams(): Observable<Team[]> {
    return this.http.get<Team[]>(`${this.base}/teams/`);
  }

  createTeam(name: string, subjectId: number): Observable<Team> {
    return this.http.post<Team>(`${this.base}/teams/`, { name, subject: subjectId });
  }

  deleteTeam(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/teams/${id}/`);
  }

  getSubjects(): Observable<Subject[]> {
    return this.http.get<Subject[]>(`${this.base}/subjects/`);
  }

  createSubject(data: any): Observable<Subject> {
    return this.http.post<Subject>(`${this.base}/subjects/`, data);
  }

  deleteSubject(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/subjects/${id}/`);
  }

  getComments(taskId: number): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.base}/tasks/${taskId}/comments/`);
  }

  addComment(taskId: number, text: string): Observable<Comment> {
    return this.http.post<Comment>(`${this.base}/tasks/${taskId}/comments/`, { text });
  }
}
