import { User } from './user.model';

export interface Team {
  id: number;
  name: string;
  subject: number;
  subject_name: string;
  members: User[];
  created_by: User;
  created_at: string;
}