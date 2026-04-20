import { User } from './user.model';

export interface Subject {
  id: number;
  name: string;
  code: string;
  semester: number;
  created_by: User;
  created_at: string;
}