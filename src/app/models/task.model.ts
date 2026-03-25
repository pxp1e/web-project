import { User } from './user.model';
import { Comment } from './comment.model';

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  deadline: string | null;
  team: number;
  team_name: string;
  assigned_to: User | null;
  created_by: User;
  comments: Comment[];
  created_at: string;
  updated_at: string;
}

export interface CreateTaskDto {
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  deadline: string | null;
  team: number;
  assigned_to_id?: number | null;
}